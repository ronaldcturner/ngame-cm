#!/usr/bin/env python3
"""Unit tests for NGAME-CM config, cross-process lock, and run journal."""

from __future__ import annotations

import json
import multiprocessing
import os
import tempfile
import time
import unittest
from pathlib import Path


def _hold_lock(lock_file: str, ready_file: str, release_file: str) -> None:
    os.environ["NGAME_PIPELINE_LOCK_PATH"] = lock_file
    from ngame_run_lock import try_acquire_pipeline_lock

    handle = try_acquire_pipeline_lock()
    if handle is None:
        Path(ready_file).write_text("fail", encoding="utf-8")
        return
    Path(ready_file).write_text("held", encoding="utf-8")
    deadline = time.time() + 10
    while time.time() < deadline and not Path(release_file).exists():
        time.sleep(0.05)
    handle.release()


class NgameCmOpsTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env_keys = (
            "NGAME_PIPELINE_LOCK_PATH",
            "NGAME_JOURNAL_DIR",
        )
        self._saved_env = {key: os.environ.get(key) for key in self._env_keys}

    def tearDown(self) -> None:
        for key, value in self._saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_load_committed_config(self) -> None:
        from ngame_cm_config import load_cm_config

        cfg = load_cm_config()
        self.assertIs(cfg["enabled"], False)
        self.assertEqual(cfg["timezone"], "America/Los_Angeles")
        self.assertEqual(cfg["run_hour_local"], 18)
        self.assertIs(cfg["phase1_weekdays_only"], True)
        self.assertIs(cfg["phase2_every_calendar_day"], True)
        self.assertIs(cfg["dashboard_is_launcher"], True)
        self.assertNotIn("client_id", cfg)
        self.assertNotIn("client_secret", cfg)

    def test_cross_process_lock_refuses_second_holder(self) -> None:
        from ngame_run_lock import try_acquire_pipeline_lock

        with tempfile.TemporaryDirectory() as tmp:
            lock_file = str(Path(tmp) / "ngame_pipeline.lock")
            ready_file = str(Path(tmp) / "ready")
            release_file = str(Path(tmp) / "release")
            proc = multiprocessing.Process(
                target=_hold_lock,
                args=(lock_file, ready_file, release_file),
            )
            proc.start()
            deadline = time.time() + 10
            while time.time() < deadline and not Path(ready_file).exists():
                time.sleep(0.05)
            self.assertEqual(Path(ready_file).read_text(encoding="utf-8"), "held")

            os.environ["NGAME_PIPELINE_LOCK_PATH"] = lock_file
            second = try_acquire_pipeline_lock()
            self.assertIsNone(second)

            Path(release_file).write_text("go", encoding="utf-8")
            proc.join(timeout=10)
            self.assertEqual(proc.exitcode, 0)

            third = try_acquire_pipeline_lock()
            self.assertIsNotNone(third)
            third.release()

    def test_journal_writes_jsonl_and_last_run(self) -> None:
        from ngame_run_journal import last_run_path, runs_path, write_run_record

        with tempfile.TemporaryDirectory() as tmp:
            os.environ["NGAME_JOURNAL_DIR"] = tmp
            record = write_run_record(
                trigger="cli",
                ok=False,
                exit_code=2,
                skipped_reason="lock_busy",
            )
            self.assertEqual(record["trigger"], "cli")
            self.assertEqual(record["skipped_reason"], "lock_busy")
            self.assertEqual(record["exit_code"], 2)
            self.assertIn("utc_ts", record)
            self.assertIn("local_date", record)
            self.assertIn("phase", record)

            lines = Path(runs_path()).read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            parsed = json.loads(lines[0])
            self.assertEqual(parsed["skipped_reason"], "lock_busy")

            last = json.loads(Path(last_run_path()).read_text(encoding="utf-8"))
            self.assertEqual(last["exit_code"], 2)
            self.assertIn("next_scheduled_local", last)

    def test_lamp_fail_and_scheduled_streak(self) -> None:
        from ngame_run_journal import consecutive_scheduled_success_days, lamp_last_result

        with tempfile.TemporaryDirectory() as tmp:
            os.environ["NGAME_JOURNAL_DIR"] = tmp
            runs = Path(tmp) / "ngame_runs.jsonl"
            rows = [
                {"trigger": "schedule", "ok": True, "local_date": "2026-09-16", "exit_code": 0},
                {"trigger": "schedule", "ok": True, "local_date": "2026-09-17", "exit_code": 0},
                {"trigger": "schedule", "ok": False, "local_date": "2026-09-17", "skipped_reason": "lock_busy", "exit_code": 2},
            ]
            runs.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
            self.assertEqual(consecutive_scheduled_success_days(), 2)

            rows.append({
                "trigger": "schedule",
                "ok": False,
                "local_date": "2026-09-18",
                "skipped_reason": "ollama_unavailable",
                "exit_code": 1,
            })
            runs.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
            self.assertEqual(consecutive_scheduled_success_days(), 0)

        self.assertEqual(lamp_last_result({"ok": False, "risk": "LOW"}), "FAIL")
        self.assertEqual(lamp_last_result({"ok": True, "risk": "HIGH"}), "HIGH")
        self.assertEqual(
            lamp_last_result({"ok": True, "skipped_reason": "already_ran"}),
            "OK",
        )

    def test_soak_check_empty_journal_fails(self) -> None:
        from ngame_soak_check import evaluate_soak

        with tempfile.TemporaryDirectory() as tmp:
            os.environ["NGAME_JOURNAL_DIR"] = tmp
            result = evaluate_soak(required_days=14)
            self.assertFalse(result["gate_passed"])
            by_id = {item["id"]: item for item in result["checks"]}
            self.assertFalse(by_id["journal"]["passed"])
            self.assertFalse(by_id["human"]["passed"])
            self.assertFalse(by_id["lock"]["passed"])
            self.assertFalse(by_id["failure_injection"]["passed"])

    def test_soak_check_synthetic_fourteen_day_pass(self) -> None:
        from ngame_soak_check import evaluate_soak

        with tempfile.TemporaryDirectory() as tmp:
            os.environ["NGAME_JOURNAL_DIR"] = tmp
            runs = Path(tmp) / "ngame_runs.jsonl"
            rows: list = [
                {
                    "trigger": "schedule",
                    "ok": False,
                    "local_date": "2026-09-04",
                    "skipped_reason": "ollama_unavailable",
                    "phase": "training",
                    "matrix_days": 0,
                    "exit_code": 1,
                }
            ]
            for offset in range(14):
                day = 5 + offset
                rows.append(
                    {
                        "trigger": "schedule",
                        "ok": True,
                        "local_date": f"2026-09-{day:02d}",
                        "skipped_reason": None,
                        "phase": "training",
                        "matrix_days": offset + 1,
                        "exit_code": 0,
                    }
                )
            rows.append(
                {
                    "trigger": "dashboard",
                    "ok": False,
                    "local_date": "2026-09-18",
                    "skipped_reason": "lock_busy",
                    "phase": "training",
                    "matrix_days": 14,
                    "exit_code": 2,
                }
            )
            runs.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
            result = evaluate_soak(required_days=14)
            self.assertTrue(result["gate_passed"], result["checks"])

            rows[-2]["matrix_days"] = 20
            runs.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
            jumped = evaluate_soak(required_days=14)
            by_id = {item["id"]: item for item in jumped["checks"]}
            self.assertFalse(by_id["matrix"]["passed"])
            self.assertFalse(jumped["gate_passed"])


if __name__ == "__main__":
    unittest.main()

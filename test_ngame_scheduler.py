#!/usr/bin/env python3
"""Unit tests for NGAME-CM scheduler tick rules."""

from __future__ import annotations

import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from ngame_scheduler import (
    ACTION_FAIL,
    ACTION_IDLE,
    ACTION_RUN,
    ACTION_SKIP,
    classify_pipeline_output,
    decide_tick,
    tick,
)


TZ = ZoneInfo("America/Los_Angeles")


def _cfg(**overrides):
    cfg = {
        "enabled": True,
        "timezone": "America/Los_Angeles",
        "run_hour_local": 18,
        "phase1_weekdays_only": True,
        "phase2_every_calendar_day": True,
        "dashboard_is_launcher": True,
    }
    cfg.update(overrides)
    return cfg


def _dt(weekday_hour: str) -> datetime:
    """weekday_hour like 'wed-19' or 'sat-18'. Uses a fixed week in 2026."""
    day, hour = weekday_hour.split("-")
    hour_i = int(hour)
    # 2026-09-16 Wed, 17 Thu, 18 Fri, 19 Sat, 20 Sun, 21 Mon
    days = {"wed": 16, "thu": 17, "fri": 18, "sat": 19, "sun": 20, "mon": 21}
    return datetime(2026, 9, days[day], hour_i, 0, 0, tzinfo=TZ)


class NgameSchedulerTests(unittest.TestCase):
    def setUp(self) -> None:
        self._saved = os.environ.get("NGAME_JOURNAL_DIR")
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["NGAME_JOURNAL_DIR"] = self._tmp.name

    def tearDown(self) -> None:
        if self._saved is None:
            os.environ.pop("NGAME_JOURNAL_DIR", None)
        else:
            os.environ["NGAME_JOURNAL_DIR"] = self._saved
        self._tmp.cleanup()

    def test_disabled_idles(self) -> None:
        d = decide_tick(
            cfg=_cfg(enabled=False),
            now=_dt("wed-19"),
            last_run=None,
            phase="training",
            ollama_ok=True,
        )
        self.assertEqual(d.action, ACTION_IDLE)

    def test_before_hour_idles(self) -> None:
        d = decide_tick(
            cfg=_cfg(),
            now=_dt("wed-17"),
            last_run=None,
            phase="training",
            ollama_ok=True,
        )
        self.assertEqual(d.action, ACTION_IDLE)

    def test_phase1_weekend_skips(self) -> None:
        d = decide_tick(
            cfg=_cfg(),
            now=_dt("sat-18"),
            last_run=None,
            phase="training",
            ollama_ok=True,
        )
        self.assertEqual(d.action, ACTION_SKIP)
        self.assertEqual(d.skipped_reason, "wrong_weekday")
        self.assertTrue(d.ok)

    def test_already_ok_today_idles_without_rerun(self) -> None:
        d = decide_tick(
            cfg=_cfg(),
            now=_dt("wed-19"),
            last_run={"local_date": "2026-09-16", "ok": True},
            phase="training",
            ollama_ok=True,
        )
        self.assertEqual(d.action, ACTION_IDLE)

    def test_weekend_skip_not_repeated(self) -> None:
        d = decide_tick(
            cfg=_cfg(),
            now=_dt("sat-19"),
            last_run={
                "local_date": "2026-09-19",
                "ok": True,
                "skipped_reason": "wrong_weekday",
            },
            phase="training",
            ollama_ok=True,
        )
        self.assertEqual(d.action, ACTION_IDLE)

    def test_phase2_weekend_runs(self) -> None:
        d = decide_tick(
            cfg=_cfg(),
            now=_dt("sat-18"),
            last_run=None,
            phase="fraud_analysis",
            ollama_ok=True,
        )
        self.assertEqual(d.action, ACTION_RUN)

    def test_phase2_without_ollama_fails(self) -> None:
        d = decide_tick(
            cfg=_cfg(),
            now=_dt("wed-18"),
            last_run=None,
            phase="fraud_analysis",
            ollama_ok=False,
        )
        self.assertEqual(d.action, ACTION_FAIL)
        self.assertEqual(d.skipped_reason, "ollama_unavailable")
        self.assertFalse(d.ok)

    def test_failed_today_retries(self) -> None:
        d = decide_tick(
            cfg=_cfg(),
            now=_dt("wed-19"),
            last_run={
                "local_date": "2026-09-16",
                "ok": False,
                "skipped_reason": "lock_busy",
            },
            phase="training",
            ollama_ok=True,
        )
        self.assertEqual(d.action, ACTION_RUN)

    def test_tick_run_calls_runner_once(self) -> None:
        called = {"n": 0}

        def fake_runner():
            called["n"] += 1
            return 0, None, "ok"

        decision = tick(
            cfg=_cfg(),
            now=_dt("wed-18"),
            last_run=None,
            phase="training",
            ollama_ok=True,
            runner=fake_runner,
        )
        self.assertEqual(decision.action, ACTION_RUN)
        self.assertEqual(called["n"], 1)

    def test_tick_disabled_does_not_call_runner(self) -> None:
        called = {"n": 0}

        def fake_runner():
            called["n"] += 1
            return 0, None, "ok"

        decision = tick(
            cfg=_cfg(enabled=False),
            now=_dt("wed-18"),
            last_run=None,
            phase="training",
            ollama_ok=True,
            runner=fake_runner,
        )
        self.assertEqual(decision.action, ACTION_IDLE)
        self.assertEqual(called["n"], 0)
        self.assertFalse(list(Path(self._tmp.name).glob("*")))

    def test_classify_invalid_grant(self) -> None:
        self.assertEqual(
            classify_pipeline_output("OAuth failed: invalid_grant"),
            "reconnect_required",
        )


if __name__ == "__main__":
    unittest.main()

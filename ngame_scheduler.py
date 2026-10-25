#!/usr/bin/env python3
"""
NGAME-CM scheduler: unattended daily sampler.

Long-running once-per-minute poller. It does not pull QuickBooks while
ngame_cm_config.json has enabled=false. It does not open a browser.
Start in a Terminal and leave it running for the lab prove.

Usage
-----
    python3 ngame_scheduler.py
    python3 ngame_scheduler.py --once
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from ngame_cm_config import load_cm_config, local_now
from ngame_env import configure_utf8_stdio, repo_root
from ngame_run_journal import read_last_run, snapshot_pipeline_facts, write_run_record
from ngame_notify import notify_for_record
from ngame_run_lock import child_lock_env, try_acquire_pipeline_lock

try:
    configure_utf8_stdio()
except Exception:
    pass

POLL_SECONDS = 60
DAILY_LOG_NAME = "ngame_daily.log"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
UNATTENDED_ENV = "NGAME_UNATTENDED"

ACTION_IDLE = "idle"
ACTION_SKIP = "skip"
ACTION_FAIL = "fail"
ACTION_RUN = "run"


@dataclass(frozen=True)
class TickDecision:
    action: str
    skipped_reason: Optional[str] = None
    journal: bool = False
    ok: bool = True
    note: str = ""


def decide_tick(
    *,
    cfg: Dict[str, Any],
    now: datetime,
    last_run: Optional[Dict[str, Any]],
    phase: str,
    ollama_ok: bool,
) -> TickDecision:
    """Pure scheduler rules. No I/O."""
    if not cfg.get("enabled"):
        return TickDecision(ACTION_IDLE, note="enabled is false")

    if now.hour < int(cfg["run_hour_local"]):
        return TickDecision(ACTION_IDLE, note="before run_hour_local")

    today = now.date().isoformat()
    if last_run and last_run.get("local_date") == today:
        if last_run.get("ok"):
            return TickDecision(ACTION_IDLE, note="already succeeded today")
        if last_run.get("skipped_reason") in ("already_ran", "wrong_weekday"):
            return TickDecision(ACTION_IDLE, note="already recorded today's skip")

    weekend = now.weekday() >= 5
    if (
        phase == "training"
        and cfg.get("phase1_weekdays_only")
        and weekend
    ):
        return TickDecision(
            ACTION_SKIP,
            skipped_reason="wrong_weekday",
            journal=True,
            ok=True,
            note="Phase I weekday-only",
        )

    if phase == "fraud_analysis" and not ollama_ok:
        return TickDecision(
            ACTION_FAIL,
            skipped_reason="ollama_unavailable",
            journal=True,
            ok=False,
            note="Phase II requires Ollama",
        )

    return TickDecision(ACTION_RUN, note="run dual_mode")


def detect_phase() -> str:
    """Same column rule as determine_mode, without its screen text.

    determine_mode prints "Determining NGAME Mode" every time it is called.
    The scheduler used to call it on every poll, so a finished day still
    looked like a new QuickBooks pull.
    """
    matrix = Path(repo_root()) / "NGAME_Training_Matrix.xlsx"
    if not matrix.is_file():
        return "training"
    try:
        from openpyxl import load_workbook

        workbook = load_workbook(matrix, read_only=True, data_only=True)
        try:
            worksheet = workbook.active
            training_days = (worksheet.max_column or 0) - 2
        finally:
            workbook.close()
    except Exception:
        return snapshot_pipeline_facts()["phase"]
    if training_days < 30:
        return "training"
    return "fraud_analysis"


def ollama_is_up(url: str = OLLAMA_TAGS_URL, timeout: float = 5.0) -> bool:
    try:
        import requests

        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False


def classify_pipeline_output(text: str) -> Optional[str]:
    lower = (text or "").lower()
    if "invalid_grant" in lower or "reconnect_required" in lower:
        return "reconnect_required"
    if "ollama is not running" in lower or "ollama_unavailable" in lower:
        return "ollama_unavailable"
    return None


def daily_log_path() -> Path:
    return Path(repo_root()) / "logs" / DAILY_LOG_NAME


_PICTURE_FRESH_SECONDS = 20 * 3600
_PICTURE_MARKS = (
    "NGAME execution completed successfully",
    "Fraud Analysis Mode completed successfully",
    "Fraud analysis completed",
)


def _recent_file(path: Path) -> bool:
    try:
        age = time.time() - path.stat().st_mtime
    except OSError:
        return False
    return 0 <= age <= _PICTURE_FRESH_SECONDS


def _bytes_have_mark(data: bytes) -> bool:
    for mark in _PICTURE_MARKS:
        if mark.encode("utf-8") in data or mark.encode("utf-16-le") in data:
            return True
    return False


def picture_finished_on(day) -> bool:
    """True when today's Phase II picture is already on disk.

    The fraud file records a local analysis_date. Match that date. Do not
    match dates inside ngame_daily.log: those stamps are UTC, and an evening
    run in Pacific time is already the next calendar day there.
    """
    fraud = Path(repo_root()) / "NGAME_Fraud_Analysis.json"
    stamp = str(day).encode("ascii")
    if fraud.is_file():
        try:
            data = fraud.read_bytes()
        except OSError:
            data = b""
        if b"analysis_date" in data and stamp in data:
            return True
        if data and _recent_file(fraud) and b"analysis_date" in data:
            return True
    log_path = daily_log_path()
    if log_path.is_file() and _recent_file(log_path):
        try:
            if _bytes_have_mark(log_path.read_bytes()):
                return True
        except OSError:
            pass
    return False


def journal_scheduled(**kwargs):
    """Journal a scheduled attempt, then notify if the FRP's switches say so."""
    record = write_run_record(**kwargs)
    notify_for_record(record)
    return record


def run_dual_mode() -> tuple[int, Optional[str], str]:
    """Lock → ngame_dual_mode.py → tee logs/ngame_daily.log. Parent journals."""
    handle = try_acquire_pipeline_lock()
    if handle is None:
        journal_scheduled(
            trigger="schedule",
            ok=False,
            exit_code=2,
            skipped_reason="lock_busy",
        )
        return 2, "lock_busy", ""

    log_path = daily_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    script = Path(repo_root()) / "ngame_dual_mode.py"
    env = child_lock_env(os.environ.copy(), trigger="schedule")
    env[UNATTENDED_ENV] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    chunks: list[str] = []
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        with log_path.open("a", encoding="utf-8") as logf:
            logf.write(f"\n----- {stamp} schedule -----\n")
            proc = subprocess.Popen(
                [sys.executable, "-u", str(script)],
                cwd=str(repo_root()),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                chunks.append(line)
                logf.write(line)
                logf.flush()
                print(line, end="")
            proc.wait()
            code = int(proc.returncode or 0)
        text = "".join(chunks)
        completed = "NGAME execution completed successfully" in text
        # A finished picture is today's run even if the log text mentions
        # invalid_grant or ollama from an earlier line. Otherwise the next
        # poll starts another QuickBooks pull the same evening.
        reason = None if (code == 0 or completed) else classify_pipeline_output(text)
        ok = code == 0 or completed
        journal_scheduled(
            trigger="schedule",
            ok=ok,
            exit_code=0 if ok else (code if code != 0 else 1),
            skipped_reason=reason,
        )
        return (0 if ok else (code if code != 0 else 1)), reason, text
    finally:
        handle.release()


def apply_decision(
    decision: TickDecision,
    *,
    phase: str,
    runner: Callable[[], tuple[int, Optional[str], str]] = run_dual_mode,
) -> TickDecision:
    if decision.action == ACTION_IDLE:
        return decision
    if decision.action == ACTION_SKIP and decision.journal:
        journal_scheduled(
            trigger="schedule",
            ok=True,
            exit_code=0,
            skipped_reason=decision.skipped_reason,
            phase=phase,
        )
        print(f"NGAME scheduler skip: {decision.skipped_reason}")
        return decision
    if decision.action == ACTION_FAIL and decision.journal:
        journal_scheduled(
            trigger="schedule",
            ok=False,
            exit_code=1,
            skipped_reason=decision.skipped_reason,
            phase=phase,
        )
        print(f"NGAME scheduler FAIL: {decision.skipped_reason}")
        return decision
    if decision.action == ACTION_RUN:
        print("NGAME scheduler: starting ngame_dual_mode.py")
        runner()
        return decision
    return decision


def tick(
    *,
    cfg: Optional[Dict[str, Any]] = None,
    now: Optional[datetime] = None,
    last_run: Optional[Dict[str, Any]] = None,
    phase: Optional[str] = None,
    ollama_ok: Optional[bool] = None,
    runner: Callable[[], tuple[int, Optional[str], str]] = run_dual_mode,
) -> TickDecision:
    cfg = cfg if cfg is not None else load_cm_config()
    now = now if now is not None else local_now(cfg)
    if last_run is None:
        last_run = read_last_run()
    if not cfg.get("enabled"):
        decision = TickDecision(ACTION_IDLE, note="enabled is false")
        return apply_decision(decision, phase=phase or "training", runner=runner)
    if now.hour < int(cfg["run_hour_local"]):
        decision = TickDecision(ACTION_IDLE, note="before run_hour_local")
        return apply_decision(decision, phase=phase or "training", runner=runner)
    today = now.date().isoformat()
    if last_run and last_run.get("local_date") == today and (
        last_run.get("ok")
        or last_run.get("skipped_reason") in ("already_ran", "wrong_weekday")
    ):
        decision = TickDecision(ACTION_IDLE, note="already succeeded today")
        return apply_decision(decision, phase=phase or "fraud_analysis", runner=runner)
    if phase is None:
        try:
            phase = detect_phase()
        except Exception:
            phase = snapshot_pipeline_facts()["phase"]
    if ollama_ok is None:
        ollama_ok = True if phase != "fraud_analysis" else ollama_is_up()
    decision = decide_tick(
        cfg=cfg,
        now=now,
        last_run=last_run,
        phase=phase,
        ollama_ok=bool(ollama_ok),
    )
    if decision.action == ACTION_RUN and picture_finished_on(now.date()):
        print("  already finished today — polling only.")
        if not (
            last_run
            and last_run.get("local_date") == now.date().isoformat()
            and last_run.get("ok")
        ):
            journal_scheduled(
                trigger="schedule",
                ok=True,
                exit_code=0,
                skipped_reason="already_ran",
            )
        decision = TickDecision(ACTION_IDLE, note="already succeeded today")
    return apply_decision(decision, phase=phase, runner=runner)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NGAME-CM unattended scheduler")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Evaluate one tick and exit (lab / tests)",
    )
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=int(os.environ.get("NGAME_SCHEDULER_POLL_SECONDS", POLL_SECONDS)),
        help="Sleep between ticks (default 60)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    cfg = load_cm_config()
    print("NGAME-CM scheduler")
    print(f"  enabled={cfg['enabled']}  timezone={cfg['timezone']}  "
          f"run_hour_local={cfg['run_hour_local']}")
    if not cfg["enabled"]:
        print("  enabled is false — will idle until soak turns it on.")
    if args.once:
        tick(cfg=cfg)
        return 0
    poll = max(5, int(args.poll_seconds))
    print(f"  polling every {poll}s. Ctrl-C to stop.")
    try:
        while True:
            tick()
            time.sleep(poll)
    except KeyboardInterrupt:
        print("\nNGAME scheduler stopped.")
        return 0


if __name__ == "__main__":
    sys.exit(main())

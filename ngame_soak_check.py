#!/usr/bin/env python3
"""
Score the NGAME-CM run journal against the Step 6 fourteen-day soak gate.

This does not start the soak. enabled stays false until a never-sleep host
is chosen. Run after the scheduler has been left alone:

    python3 ngame_soak_check.py

Exit 0 only if every pass rule is evidenced in the journal. The 14-day clock
is calendar evidence, not a code drop.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Sequence

from ngame_cm_config import load_cm_config
from ngame_env import configure_utf8_stdio
from ngame_run_journal import read_run_records, scheduled_success_streak_dates

try:
    configure_utf8_stdio()
except Exception:
    pass

SOAK_REQUIRED_DAYS = 14
SKIP_OK = frozenset({"already_ran", "wrong_weekday"})
LOCK_BUSY = "lock_busy"
BABYSIT_TRIGGERS = frozenset({"dashboard", "cli"})


def _is_actual_pull(record: Dict[str, Any]) -> bool:
    if not record.get("ok"):
        return False
    skip = record.get("skipped_reason")
    return skip in (None, "", False)


def _window_records(
    records: Sequence[Dict[str, Any]],
    window_dates: Sequence[str],
) -> List[Dict[str, Any]]:
    wanted = set(window_dates)
    return [row for row in records if row.get("local_date") in wanted]


def _check_journal(streak_dates: Sequence[str], required_days: int) -> Dict[str, Any]:
    streak = len(streak_dates)
    passed = streak >= required_days
    if streak == 0:
        detail = f"0 consecutive scheduled successes (need {required_days})"
    elif passed:
        detail = (
            f"{streak} consecutive scheduled successes "
            f"({streak_dates[0]} … {streak_dates[-1]})"
        )
    else:
        detail = f"{streak} consecutive scheduled successes (need {required_days})"
    return {"id": "journal", "passed": passed, "detail": detail, "streak": streak}


def _check_matrix(
    records: Sequence[Dict[str, Any]],
    window_dates: Sequence[str],
) -> Dict[str, Any]:
    if not window_dates:
        return {
            "id": "matrix",
            "passed": False,
            "detail": "no 14-day window yet; matrix rule not evidenced",
        }
    notes: List[str] = []
    by_date: Dict[str, List[Dict[str, Any]]] = {}
    for row in _window_records(records, window_dates):
        if row.get("trigger") != "schedule" or not _is_actual_pull(row):
            continue
        by_date.setdefault(str(row["local_date"]), []).append(row)

    if not by_date:
        return {
            "id": "matrix",
            "passed": False,
            "detail": "window has scheduled successes but no actual pulls to score columns",
        }

    ok = True
    for day, rows in sorted(by_date.items()):
        if len(rows) > 1:
            ok = False
            notes.append(f"{day}: {len(rows)} scheduled pulls")

    prev_days: Optional[int] = None
    prev_phase: Optional[str] = None
    for day in sorted(by_date):
        latest = by_date[day][-1]
        days = latest.get("matrix_days")
        phase = latest.get("phase")
        if prev_days is not None and isinstance(days, int) and isinstance(prev_days, int):
            if phase == "fraud_analysis" and prev_phase == "fraud_analysis":
                if days != prev_days:
                    ok = False
                    notes.append(f"{day}: Phase II matrix_days {prev_days} → {days}")
            else:
                delta = days - prev_days
                if delta > 1:
                    ok = False
                    notes.append(f"{day}: matrix_days jumped {prev_days} → {days}")
                if delta < 0:
                    ok = False
                    notes.append(f"{day}: matrix_days fell {prev_days} → {days}")
        prev_days = days if isinstance(days, int) else prev_days
        prev_phase = str(phase) if phase else prev_phase

    if ok:
        detail = (
            f"{len(by_date)} actual scheduled pull-day(s) in window; "
            "at most one column per date"
        )
    else:
        detail = "; ".join(notes) if notes else "matrix rule failed"
    return {"id": "matrix", "passed": ok, "detail": detail}


def _check_lock(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    hits = [row for row in records if row.get("skipped_reason") == LOCK_BUSY]
    if hits:
        last = hits[-1]
        detail = (
            f"lock_busy recorded {last.get('local_date')} "
            f"trigger={last.get('trigger')}"
        )
        return {"id": "lock", "passed": True, "detail": detail}
    return {
        "id": "lock",
        "passed": False,
        "detail": "no lock_busy record yet — overlap a dashboard/CLI run once during soak",
    }


def _check_failure_injection(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    pending: Optional[Dict[str, Any]] = None
    babysat: Optional[Dict[str, Any]] = None
    recovered_from: Optional[Dict[str, Any]] = None
    recovered_on: Optional[Dict[str, Any]] = None
    for row in records:
        if (
            row.get("trigger") == "schedule"
            and not row.get("ok")
            and row.get("skipped_reason") != LOCK_BUSY
        ):
            pending = row
            continue
        if pending is None or not row.get("ok"):
            continue
        if row.get("trigger") == "schedule":
            recovered_from = pending
            recovered_on = row
            pending = None
            continue
        if row.get("trigger") in BABYSIT_TRIGGERS and _is_actual_pull(row):
            babysat = pending
            pending = None
    if recovered_from is not None and recovered_on is not None:
        reason = recovered_from.get("skipped_reason") or "FAIL"
        return {
            "id": "failure_injection",
            "passed": True,
            "detail": (
                f"{reason} on {recovered_from.get('local_date')}; "
                f"later scheduled success on {recovered_on.get('local_date')}"
            ),
        }
    if pending is not None:
        return {
            "id": "failure_injection",
            "passed": False,
            "detail": (
                f"FAIL on {pending.get('local_date')} "
                f"({pending.get('skipped_reason')}); no later scheduled success"
            ),
        }
    if babysat is not None:
        return {
            "id": "failure_injection",
            "passed": False,
            "detail": (
                f"FAIL on {babysat.get('local_date')} recovered by a "
                "dashboard/CLI click, not the scheduler"
            ),
        }
    return {
        "id": "failure_injection",
        "passed": False,
        "detail": "no scheduled FAIL yet — kill Ollama or pull the network once",
    }


def _check_human(
    records: Sequence[Dict[str, Any]],
    window_dates: Sequence[str],
    journal_ok: bool,
) -> Dict[str, Any]:
    if not journal_ok:
        return {
            "id": "human",
            "passed": False,
            "detail": "no 14-day unattended window yet",
        }
    babysit: List[str] = []
    for row in _window_records(records, window_dates):
        if row.get("trigger") not in BABYSIT_TRIGGERS:
            continue
        if row.get("skipped_reason") == LOCK_BUSY:
            continue
        if _is_actual_pull(row):
            babysit.append(
                f"{row.get('local_date')} {row.get('trigger')} pull"
            )
    if babysit:
        return {
            "id": "human",
            "passed": False,
            "detail": "babysat: " + "; ".join(babysit),
        }
    return {
        "id": "human",
        "passed": True,
        "detail": (
            f"{window_dates[0]} … {window_dates[-1]}: "
            "no dashboard/CLI pulls in the streak window"
        ),
    }


def evaluate_soak(*, required_days: int = SOAK_REQUIRED_DAYS) -> Dict[str, Any]:
    cfg = load_cm_config()
    records = read_run_records()
    streak_dates = scheduled_success_streak_dates()
    window = list(streak_dates[-required_days:]) if streak_dates else []
    journal = _check_journal(streak_dates, required_days)
    checks = [
        journal,
        _check_matrix(records, window),
        _check_lock(records),
        _check_failure_injection(records),
        _check_human(records, window, journal["passed"]),
    ]
    return {
        "gate_passed": all(item["passed"] for item in checks),
        "required_days": required_days,
        "scheduler_enabled": bool(cfg.get("enabled")),
        "streak_dates": list(streak_dates),
        "window_dates": window,
        "checks": checks,
    }


def format_report(result: Dict[str, Any]) -> str:
    lines = [
        "NGAME-CM soak check",
        "===================",
        f"scheduler enabled: {str(result['scheduler_enabled']).lower()}",
        f"streak: {len(result['streak_dates'])} / {result['required_days']}",
        f"gate: {'PASSED' if result['gate_passed'] else 'NOT PASSED'}",
        "",
    ]
    labels = {
        "journal": "journal",
        "matrix": "matrix",
        "lock": "lock test",
        "failure_injection": "failure inject",
        "human": "human",
    }
    for item in result["checks"]:
        mark = "PASS" if item["passed"] else "FAIL"
        name = labels.get(item["id"], item["id"])
        lines.append(f"{name:<16} {mark}  {item['detail']}")
    if not result["scheduler_enabled"] and not result["gate_passed"]:
        lines.extend(
            [
                "",
                "Soak is not started. On a never-sleep host with a working",
                "Track A or Track B company: set enabled=true in",
                "ngame_cm_config.json, run python3 ngame_scheduler.py, and",
                "do not click the FRP button. Re-run this checker after 14 days.",
            ]
        )
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Score the 14-day unattended soak gate")
    parser.add_argument(
        "--required-days",
        type=int,
        default=SOAK_REQUIRED_DAYS,
        help="Consecutive scheduled successes required (default 14)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the raw result object instead of the text report",
    )
    args = parser.parse_args(argv)
    result = evaluate_soak(required_days=max(1, int(args.required_days)))
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_report(result), end="")
    return 0 if result["gate_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

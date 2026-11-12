#!/usr/bin/env python3
"""CLI wrapper: acquire the pipeline lock, run main(), journal the attempt."""

from __future__ import annotations

import os
import sys
from typing import Callable, Optional

from ngame_run_journal import write_run_record
from ngame_run_lock import (
    BUSY_EXIT_CODE,
    BUSY_MESSAGE,
    TRIGGER_ENV,
    lock_held_by_parent,
    try_acquire_pipeline_lock,
)


def cli_guarded_exit(main_fn: Callable[[], object], *, trigger: Optional[str] = None) -> None:
    """
    Run a CLI entry point under the cross-process lock.

    If the parent (dashboard) already holds the lock, run without re-acquiring
    or journaling — the parent records the attempt after the child exits.
    """
    sys.exit(cli_guarded_main(main_fn, trigger=trigger))


def cli_guarded_main(main_fn: Callable[[], object], *, trigger: Optional[str] = None) -> int:
    resolved_trigger = trigger or os.environ.get(TRIGGER_ENV, "cli")

    if lock_held_by_parent():
        return _call_main(main_fn)

    handle = try_acquire_pipeline_lock()
    if handle is None:
        print(BUSY_MESSAGE, file=sys.stderr)
        write_run_record(
            trigger=resolved_trigger,
            ok=False,
            exit_code=BUSY_EXIT_CODE,
            skipped_reason="lock_busy",
        )
        return BUSY_EXIT_CODE

    try:
        code = _call_main(main_fn)
        write_run_record(
            trigger=resolved_trigger,
            ok=(code == 0),
            exit_code=code,
        )
        return code
    except Exception:
        write_run_record(
            trigger=resolved_trigger,
            ok=False,
            exit_code=1,
        )
        raise
    finally:
        handle.release()


def _call_main(main_fn: Callable[[], object]) -> int:
    result = main_fn()
    if result is True or result is None:
        return 0
    if result is False:
        return 1
    try:
        return int(result)
    except (TypeError, ValueError):
        return 0 if result else 1

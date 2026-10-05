#!/usr/bin/env python3
"""Cross-process pipeline lock. Serializes dashboard, CLI, and (later) scheduler."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from ngame_env import repo_root

LOCK_FILENAME = "ngame_pipeline.lock"
LOCK_HELD_ENV = "NGAME_PIPELINE_LOCK_HELD"
TRIGGER_ENV = "NGAME_RUN_TRIGGER"
LOCK_PATH_ENV = "NGAME_PIPELINE_LOCK_PATH"

BUSY_EXIT_CODE = 2
BUSY_MESSAGE = (
    "NGAME pipeline already running (cross-process lock busy). "
    "Do not start a second pull."
)


def lock_path() -> Path:
    override = os.environ.get(LOCK_PATH_ENV)
    if override:
        return Path(override)
    return Path(repo_root()) / "logs" / LOCK_FILENAME


def lock_held_by_parent() -> bool:
    return os.environ.get(LOCK_HELD_ENV, "").strip() in ("1", "true", "yes")


def child_lock_env(existing: Optional[dict] = None, *, trigger: Optional[str] = None) -> dict:
    """Env for a subprocess whose parent already holds the pipeline lock."""
    env = dict(existing if existing is not None else os.environ)
    env[LOCK_HELD_ENV] = "1"
    if trigger:
        env[TRIGGER_ENV] = trigger
    else:
        env.setdefault(TRIGGER_ENV, "dashboard")
    return env


class PipelineLock:
    """Exclusive lock held for the lifetime of one pipeline attempt."""

    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path is not None else lock_path()
        self._fh = None

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.path, "a+b")
        try:
            if os.name == "nt":
                self._acquire_windows()
            else:
                self._acquire_posix()
            return True
        except (BlockingIOError, OSError, PermissionError):
            self._close()
            return False

    def release(self) -> None:
        if self._fh is None:
            return
        try:
            if os.name == "nt":
                import msvcrt

                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        finally:
            self._close()

    def _acquire_posix(self) -> None:
        import fcntl

        fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _acquire_windows(self) -> None:
        import msvcrt

        self._fh.seek(0)
        if self._fh.read(1) == b"":
            self._fh.write(b"\0")
            self._fh.flush()
        self._fh.seek(0)
        msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)

    def _close(self) -> None:
        if self._fh is not None:
            try:
                self._fh.close()
            except OSError:
                pass
            self._fh = None


def try_acquire_pipeline_lock() -> Optional[PipelineLock]:
    """Non-blocking exclusive acquire. None means another process holds the lock."""
    handle = PipelineLock()
    if handle.acquire():
        return handle
    return None

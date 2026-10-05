#!/usr/bin/env python3
"""Load NGAME-CM orchestration config. No secrets. Detector-neutral."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import json

from ngame_env import repo_root

CONFIG_FILENAME = "ngame_cm_config.json"

_DEFAULTS: Dict[str, Any] = {
    "enabled": False,
    "timezone": "America/Los_Angeles",
    "run_hour_local": 18,
    "phase1_weekdays_only": True,
    "phase2_every_calendar_day": True,
    "dashboard_is_launcher": True,
}


def config_path() -> Path:
    return Path(repo_root()) / CONFIG_FILENAME


def load_cm_config() -> Dict[str, Any]:
    """Return validated CM config. Missing file yields defaults (scheduler stays off)."""
    cfg = dict(_DEFAULTS)
    path = config_path()
    if path.is_file():
        with path.open(encoding="utf-8") as fh:
            raw = json.load(fh)
        if not isinstance(raw, dict):
            raise ValueError(f"{CONFIG_FILENAME} must be a JSON object")
        for key in _DEFAULTS:
            if key in raw and raw[key] is not None:
                cfg[key] = raw[key]
    _validate(cfg)
    return cfg


def config_timezone(cfg: Dict[str, Any] | None = None) -> ZoneInfo:
    cfg = cfg if cfg is not None else load_cm_config()
    name = str(cfg["timezone"])
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown timezone in {CONFIG_FILENAME}: {name}") from exc


def local_now(cfg: Dict[str, Any] | None = None) -> datetime:
    return datetime.now(config_timezone(cfg))


def next_scheduled_local(cfg: Dict[str, Any] | None = None) -> str:
    """ISO local timestamp of the next run_hour_local in the org timezone."""
    cfg = cfg if cfg is not None else load_cm_config()
    tz = config_timezone(cfg)
    hour = int(cfg["run_hour_local"])
    now = datetime.now(tz)
    candidate = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if now >= candidate:
        candidate = candidate + timedelta(days=1)
    return candidate.isoformat()


def _validate(cfg: Dict[str, Any]) -> None:
    cfg["enabled"] = bool(cfg["enabled"])
    cfg["phase1_weekdays_only"] = bool(cfg["phase1_weekdays_only"])
    cfg["phase2_every_calendar_day"] = bool(cfg["phase2_every_calendar_day"])
    cfg["dashboard_is_launcher"] = bool(cfg["dashboard_is_launcher"])
    cfg["timezone"] = str(cfg["timezone"]).strip()
    hour = int(cfg["run_hour_local"])
    if hour < 0 or hour > 23:
        raise ValueError("run_hour_local must be an integer 0–23")
    cfg["run_hour_local"] = hour
    if not cfg["timezone"]:
        raise ValueError("timezone must be a non-empty IANA name")
    config_timezone(cfg)

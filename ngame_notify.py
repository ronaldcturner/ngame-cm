#!/usr/bin/env python3
"""Optional FRP notification after a scheduled picture.

Switches live in ngame_notify_settings.json (no mailbox password).
The installer puts SMTP and text-account secrets in ngame_notify_secrets.json.
Both files stay off the clock's decision to run. A send failure does not
change the journal.
"""

from __future__ import annotations

import json
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ngame_env import repo_root

SETTINGS_NAME = "ngame_notify_settings.json"
SECRETS_NAME = "ngame_notify_secrets.json"
ALERT_RISKS = {"MEDIUM", "HIGH"}
_SKIP = {"already_ran", "wrong_weekday", "lock_busy"}


def settings_path() -> Path:
    return Path(repo_root()) / SETTINGS_NAME


def secrets_path() -> Path:
    return Path(repo_root()) / SECRETS_NAME


def default_settings() -> Dict[str, Any]:
    return {
        "email_on": False,
        "email_to": "",
        "text_on": False,
        "text_to": "",
    }


def load_settings() -> Dict[str, Any]:
    data = default_settings()
    path = settings_path()
    if not path.is_file():
        return data
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return data
    if not isinstance(raw, dict):
        return data
    data["email_on"] = bool(raw.get("email_on"))
    data["text_on"] = bool(raw.get("text_on"))
    data["email_to"] = str(raw.get("email_to") or "").strip()
    data["text_to"] = str(raw.get("text_to") or "").strip()
    return data


def save_settings(incoming: Dict[str, Any]) -> Dict[str, Any]:
    data = default_settings()
    data["email_on"] = bool(incoming.get("email_on"))
    data["text_on"] = bool(incoming.get("text_on"))
    data["email_to"] = str(incoming.get("email_to") or "").strip()
    data["text_to"] = str(incoming.get("text_to") or "").strip()
    path = settings_path()
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def load_secrets() -> Dict[str, Any]:
    path = secrets_path()
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def should_notify(record: Dict[str, Any]) -> Optional[str]:
    """Return a short reason to send, or None for a quiet night."""
    if record.get("trigger") != "schedule":
        return None
    if record.get("skipped_reason") in _SKIP:
        return None
    if not record.get("ok"):
        return "FAIL"
    risk = str(record.get("risk") or "").upper()
    if risk in ALERT_RISKS:
        return risk
    return None


def _message(record: Dict[str, Any], reason: str) -> tuple[str, str]:
    when = record.get("local_date") or "the scheduled night"
    subject = f"NGAME picture — {reason}"
    body = (
        f"NGAME took the scheduled picture for {when}.\n"
        f"Result: {reason}.\n"
        "Open the dashboard on the NGAME computer to read last run, "
        "last result, scheduled successes, and next scheduled.\n"
        "A quiet night does not send this message.\n"
        "NGAME does not see every QuickBooks save. "
        "The Audit Log stays in QuickBooks."
    )
    return subject, body


def _send_email(secrets: Dict[str, Any], to_addr: str, subject: str, body: str) -> None:
    host = str(secrets.get("smtp_host") or "").strip()
    user = str(secrets.get("smtp_user") or "").strip()
    password = str(secrets.get("smtp_password") or "")
    sender = str(secrets.get("smtp_from") or user).strip()
    port = int(secrets.get("smtp_port") or 587)
    if not (host and user and password and sender and to_addr):
        raise RuntimeError("email switch is on but mailbox settings are incomplete")
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_addr
    with smtplib.SMTP(host, port, timeout=30) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(sender, [to_addr], msg.as_string())


def _send_text(secrets: Dict[str, Any], to_number: str, body: str) -> None:
    sid = str(secrets.get("twilio_account_sid") or "").strip()
    token = str(secrets.get("twilio_auth_token") or "").strip()
    sender = str(secrets.get("twilio_from") or "").strip()
    if not (sid and token and sender and to_number):
        raise RuntimeError("text switch is on but the phone-message account is incomplete")
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    data = urlencode({"From": sender, "To": to_number, "Body": body}).encode("utf-8")
    req = Request(url, data=data, method="POST")
    import base64

    cred = base64.b64encode(f"{sid}:{token}".encode("utf-8")).decode("ascii")
    req.add_header("Authorization", f"Basic {cred}")
    try:
        with urlopen(req, timeout=30) as resp:
            resp.read()
    except URLError as exc:
        raise RuntimeError(str(exc)) from exc


def notify_for_record(record: Dict[str, Any]) -> None:
    """Send email and/or text when the FRP's switches say so. Never raises."""
    try:
        reason = should_notify(record)
        if not reason:
            return
        settings = load_settings()
        secrets = load_secrets()
        subject, body = _message(record, reason)
        if settings["email_on"] and settings["email_to"]:
            try:
                _send_email(secrets, settings["email_to"], subject, body)
                print("NGAME notify: email sent")
            except Exception as exc:
                print(f"NGAME notify: email not sent ({exc})")
        if settings["text_on"] and settings["text_to"]:
            try:
                _send_text(secrets, settings["text_to"], body)
                print("NGAME notify: text sent")
            except Exception as exc:
                print(f"NGAME notify: text not sent ({exc})")
    except Exception as exc:
        print(f"NGAME notify skipped: {exc}")

"""
Current date and time in the patient's timezone for prompt injection.

Used so the patient bot knows "today" and "current time" when saying things
like "this Thursday" or "next week". Timezone is configurable via env
PATIENT_TIMEZONE (default America/Chicago for Hermitage, TN).
"""

import os
from datetime import datetime
from zoneinfo import ZoneInfo


def get_patient_timezone() -> str:
    """Return IANA timezone name from env, default America/Chicago (Hermitage, TN)."""
    return os.getenv("PATIENT_TIMEZONE", "America/Chicago")


def get_patient_now() -> datetime:
    """Return current datetime in the patient's timezone (timezone-aware)."""
    tz = ZoneInfo(get_patient_timezone())
    return datetime.now(tz)


def get_datetime_context_string() -> str:
    """
    Return a short string for injection into the system prompt, e.g.:
    "Today is Monday, February 17, 2026. Current time is 3:45 PM Central Time."
    """
    now = get_patient_now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M %p").lstrip("0") or "12"  # 3:45 PM (portable)
    tz_name = now.tzname() or get_patient_timezone().split("/")[-1].replace("_", " ")
    return f"Today is {date_str}. Current time is {time_str} {tz_name}."

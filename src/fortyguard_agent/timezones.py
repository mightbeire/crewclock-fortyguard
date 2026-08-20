from __future__ import annotations

from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def project_timezone(name: str = "America/Phoenix") -> ZoneInfo | timezone:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        # Phoenix is UTC−07 year-round. This fallback keeps Windows demo runs
        # safe when the optional tzdata package is not installed.
        if name == "America/Phoenix":
            return timezone(timedelta(hours=-7), name="America/Phoenix")
        raise


def as_project_local(value: datetime, name: str = "America/Phoenix") -> datetime:
    if value.tzinfo is None:
        raise ValueError("timestamp_must_be_timezone_aware")
    return value.astimezone(project_timezone(name))

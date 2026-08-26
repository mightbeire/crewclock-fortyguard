from __future__ import annotations

from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


_US_FALLBACK_OFFSETS = {
    "America/New_York": -5,
    "America/Chicago": -6,
    "America/Denver": -7,
    "America/Los_Angeles": -8,
    "America/Phoenix": -7,
    "America/Anchorage": -9,
    "Pacific/Honolulu": -10,
}


def project_timezone(name: str = "America/Phoenix", at: datetime | None = None) -> ZoneInfo | timezone:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        # Windows builds may not ship IANA tzdata. Keep the supported US
        # project timezones usable without silently accepting arbitrary labels.
        if name in _US_FALLBACK_OFFSETS:
            offset = _US_FALLBACK_OFFSETS[name]
            if name != "America/Phoenix" and name not in {"Pacific/Honolulu", "America/Anchorage"} and at is not None:
                # US DST is a bounded operational detail here; exact historical
                # rule changes are irrelevant to the supported 2019+ site path.
                month = at.month
                if 3 < month < 11 or month in {4, 5, 6, 7, 8, 9, 10}:
                    offset += 1
            return timezone(timedelta(hours=offset), name=name)
        raise


def as_project_local(value: datetime, name: str = "America/Phoenix") -> datetime:
    if value.tzinfo is None:
        raise ValueError("timestamp_must_be_timezone_aware")
    return value.astimezone(project_timezone(name))

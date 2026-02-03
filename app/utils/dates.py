from __future__ import annotations

from datetime import datetime, timezone


def epoch_to_dt(value: int | float | None) -> datetime | None:
    """
    Convert epoch timestamps to a timezone-aware UTC datetime.

    Handles:
    - seconds      (~1e9)
    - milliseconds (~1e12)
    - microseconds (~1e15)
    - nanoseconds  (~1e18)

    Any malformed or out-of-range values safely return None.
    """
    if value is None:
        return None

    try:
        v = float(value)
    except (TypeError, ValueError):
        return None

    # Magnitude heuristics
    # seconds  ~ 1e9
    # millis   ~ 1e12
    # micros   ~ 1e15
    # nanos    ~ 1e18
    if v > 1e17:          # nanoseconds
        v = v / 1_000_000_000.0
    elif v > 1e14:        # microseconds
        v = v / 1_000_000.0
    elif v > 1e12:        # milliseconds
        v = v / 1_000.0

    try:
        return datetime.fromtimestamp(v, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        # Prevents crashes like: ValueError: year 31969 is out of range
        return None


def dt_to_iso(dt: datetime | None) -> str | None:
    """Render datetime as ISO-8601 string."""
    if dt is None:
        return None
    return dt.isoformat()

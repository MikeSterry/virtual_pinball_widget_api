from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Union

Number = Union[int, float]


def epoch_to_dt(v: Optional[Number]) -> Optional[datetime]:
    """
    Convert epoch timestamp to UTC datetime.

    Accepts:
      - seconds (1700000000)
      - milliseconds (1700000000000)

    Returns None for null / invalid values.
    """
    if v is None:
        return None

    try:
        n = float(v)
    except (TypeError, ValueError):
        return None

    if n <= 0:
        return None

    # Heuristic: anything >= 1e11 is milliseconds
    if n >= 100_000_000_000:
        n /= 1000.0

    try:
        return datetime.fromtimestamp(n, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


def dt_to_iso(dt: datetime | None) -> str | None:
    """Render datetime as ISO string."""
    if dt is None:
        return None
    return dt.isoformat()

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List, Sequence


def _dt_or_min_utc(dt: datetime | None) -> datetime:
    """
    Normalize datetimes for safe comparison:
    - If None: return the minimum UTC-aware datetime
    - If naive: treat it as UTC (attach tzinfo=UTC)
    - If aware: keep as-is
    """
    if not isinstance(dt, datetime):
        return datetime.min.replace(tzinfo=timezone.utc)

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt


# -------- Games --------

def sort_games_by_created_at(games: Sequence[Any]) -> List[Any]:
    """Sort games by createdAt descending."""
    return sorted(games, key=lambda g: _dt_or_min_utc(getattr(g, "createdAt", None)), reverse=True)


def sort_games_by_updated_at(games: Sequence[Any]) -> List[Any]:
    """Sort games by updatedAt descending."""
    return sorted(games, key=lambda g: _dt_or_min_utc(getattr(g, "updatedAt", None)), reverse=True)


# -------- Tables --------

def sort_tables_by_created_at(tables: Sequence[Any]) -> List[Any]:
    """Sort tables by createdAt descending."""
    return sorted(tables, key=lambda t: _dt_or_min_utc(getattr(t, "createdAt", None)), reverse=True)


def sort_tables_by_updated_at(tables: Sequence[Any]) -> List[Any]:
    """Sort tables by updatedAt descending."""
    return sorted(tables, key=lambda t: _dt_or_min_utc(getattr(t, "updatedAt", None)), reverse=True)


# -------- Backglasses --------

def sort_backglasses_by_created_at(bgs: Sequence[Any]) -> List[Any]:
    """Sort backglasses by createdAt descending."""
    return sorted(bgs, key=lambda b: _dt_or_min_utc(getattr(b, "createdAt", None)), reverse=True)


def sort_backglasses_by_updated_at(bgs: Sequence[Any]) -> List[Any]:
    """Sort backglasses by updatedAt descending."""
    return sorted(bgs, key=lambda b: _dt_or_min_utc(getattr(b, "updatedAt", None)), reverse=True)

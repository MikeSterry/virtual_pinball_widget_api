from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from app.models.game import Game
from app.models.game_table import GameTable
from app.models.game_back_glass import GameBackGlass


def _dt_or_min(dt: datetime | None) -> datetime:
    """Return dt or a minimal datetime for safe sorting."""
    return dt if dt is not None else datetime.min.replace(tzinfo=timezone.utc)


def sort_games_by_updated_at(games: List[Game]) -> List[Game]:
    """Sort games descending by updatedAt."""
    return sorted(games, key=lambda g: _dt_or_min(g.updatedAt), reverse=True)


def sort_tables_by_updated_at(tables: List[GameTable]) -> List[GameTable]:
    """Sort tables descending by updatedAt."""
    return sorted(tables, key=lambda t: _dt_or_min(t.updatedAt), reverse=True)


def sort_backglasses_by_updated_at(backglasses: List[GameBackGlass]) -> List[GameBackGlass]:
    """Sort backglasses descending by updatedAt."""
    return sorted(backglasses, key=lambda b: _dt_or_min(b.updatedAt), reverse=True)

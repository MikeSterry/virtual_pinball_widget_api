from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Iterable, Sequence

from app.models.base_model import BaseModel
from app.models.game_table import GameTable
from app.models.game_back_glass import GameBackGlass
from app.utils.dates import dt_to_iso


@dataclass
class Game(BaseModel):
    """Root model representing a pinball game entry."""

    id: str
    name: str | None = None
    year: int | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    tableFiles: List[GameTable] = field(default_factory=list)
    b2sFiles: List[GameBackGlass] = field(default_factory=list)

    # ---------- Query helpers (static) ----------

    @staticmethod
    def most_recent_games(games: Iterable["Game"], limit: int = 10) -> List["Game"]:
        """Return the most recently updated games."""
        from app.utils.comparators import sort_games_by_updated_at

        return sort_games_by_updated_at(list(games))[:limit]

    @staticmethod
    def most_recent_tables(games: Iterable["Game"], limit: int = 10) -> List[GameTable]:
        """Return the most recently updated tables across all games."""
        from app.utils.comparators import sort_tables_by_updated_at

        tables: List[GameTable] = []
        for g in games:
            tables.extend(g.tableFiles)
        return sort_tables_by_updated_at(tables)[:limit]

    @staticmethod
    def most_recent_backglasses(games: Iterable["Game"], limit: int = 10) -> List[GameBackGlass]:
        """Return the most recently updated backglasses across all games."""
        from app.utils.comparators import sort_backglasses_by_updated_at

        bgs: List[GameBackGlass] = []
        for g in games:
            bgs.extend(g.b2sFiles)
        return sort_backglasses_by_updated_at(bgs)[:limit]

    @staticmethod
    def tables_by_formats(
        games: Iterable["Game"],
        table_formats: Sequence[str],
        limit: int | None = None,
    ) -> List[GameTable]:
        """Filter tables by one-or-more formats and return most recently updated."""
        from app.utils.comparators import sort_tables_by_updated_at

        wanted = {(f or "").strip().lower() for f in (table_formats or []) if (f or "").strip()}
        if not wanted:
            return []

        tables: List[GameTable] = []
        for g in games:
            for t in g.tableFiles:
                if (t.tableFormat or "").strip().lower() in wanted:
                    tables.append(t)

        tables = sort_tables_by_updated_at(tables)
        return tables[:limit] if limit else tables

    @staticmethod
    def tables_by_format(games: Iterable["Game"], table_format: str, limit: int | None = None) -> List[GameTable]:
        """Back-compat single-format filter."""
        return Game.tables_by_formats(games, [table_format], limit=limit)

    @staticmethod
    def backglasses_by_features(
        games: Iterable["Game"],
        features: Sequence[str],
        limit: int | None = None,
    ) -> List[GameBackGlass]:
        """Filter backglasses by one-or-more features and return most recently updated."""
        from app.utils.comparators import sort_backglasses_by_updated_at

        wanted = {(f or "").strip().lower() for f in (features or []) if (f or "").strip()}
        if not wanted:
            return []

        bgs: List[GameBackGlass] = []
        for g in games:
            for b in g.b2sFiles:
                if any((x or "").strip().lower() in wanted for x in (b.features or [])):
                    bgs.append(b)

        bgs = sort_backglasses_by_updated_at(bgs)
        return bgs[:limit] if limit else bgs

    @staticmethod
    def backglasses_by_feature(games: Iterable["Game"], feature: str, limit: int | None = None) -> List[GameBackGlass]:
        """Back-compat single-feature filter."""
        return Game.backglasses_by_features(games, [feature], limit=limit)

    def to_dict(self) -> dict:
        """Serialize to JSON-friendly dict."""
        return {
            "id": self.id,
            "name": self.name,
            "year": self.year,
            "createdAt": dt_to_iso(self.createdAt),
            "updatedAt": dt_to_iso(self.updatedAt),
            "tableFiles": [t.to_dict() for t in self.tableFiles],
            "b2sFiles": [b.to_dict() for b in self.b2sFiles],
        }

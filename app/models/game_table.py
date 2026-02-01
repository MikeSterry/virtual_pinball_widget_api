from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from app.models.base_model import BaseModel
from app.models.game_item_url import GameItemUrl
from app.utils.dates import dt_to_iso


@dataclass
class GameTable(BaseModel):
    """Represents a table file (VPX/FP/...) tied to a game."""

    id: str
    version: str | None = None
    tableFormat: str | None = None
    authors: List[str] = field(default_factory=list)
    imgUrl: str | None = None
    urls: List[GameItemUrl] = field(default_factory=list)
    createdAt: datetime | None = None
    updatedAt: datetime | None = None

    # Parent metadata (for widgets / flattened APIs)
    gameId: str | None = None
    gameName: str | None = None

    def add_url(self, url: str, broken: bool = False) -> None:
        """Add a URL with incrementing priority."""
        priority = len(self.urls) + 1
        self.urls.append(GameItemUrl(url=url, broken=broken, priority=priority))

    def best_url(self) -> str | None:
        """Return the highest-priority non-broken URL, falling back to first."""
        candidates = sorted(self.urls, key=lambda u: u.priority)
        for u in candidates:
            if not u.broken and u.url:
                return u.url
        return candidates[0].url if candidates else None

    def to_dict(self) -> dict:
        """Serialize to JSON-friendly dict."""
        return {
            "id": self.id,
            "version": self.version,
            "tableFormat": self.tableFormat,
            "authors": self.authors,
            "imgUrl": self.imgUrl,
            "urls": [u.to_dict() for u in self.urls],
            "createdAt": dt_to_iso(self.createdAt),
            "updatedAt": dt_to_iso(self.updatedAt),
            "game": {"id": self.gameId, "name": self.gameName},
        }

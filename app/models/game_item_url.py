from __future__ import annotations

from dataclasses import dataclass, field

from app.models.base_model import BaseModel


@dataclass
class GameItemUrl(BaseModel):
    """A URL entry for a table/backglass item."""

    url: str
    broken: bool = False
    priority: int = field(default=1)

    def to_dict(self) -> dict:
        """Serialize to JSON-friendly dict."""
        return {"url": self.url, "broken": self.broken, "priority": self.priority}

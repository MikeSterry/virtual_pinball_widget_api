from __future__ import annotations

from dataclasses import dataclass
from typing import List

from flask import current_app

from app.models.game import Game
from app.services.vpsdb_loader import VpsDbLoader
from app.services.vpsdb_mapper import VpsDbMapper


@dataclass
class GameRepository:
    """Repository that provides mapped Game models."""

    loader: VpsDbLoader
    mapper: VpsDbMapper

    @classmethod
    def from_flask_app(cls) -> "GameRepository":
        """Create repository from Flask app settings."""
        settings = current_app.config["SETTINGS"]
        return cls(loader=VpsDbLoader(settings), mapper=VpsDbMapper())

    def list_games(self) -> List[Game]:
        """Load and map all games."""
        raw = self.loader.load_raw()
        return self.mapper.map_games(raw)

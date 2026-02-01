from __future__ import annotations

from typing import List

from flask import Blueprint, render_template, current_app

from app.models.game import Game
from app.models.game_back_glass import GameBackGlass
from app.services.game_repository import GameRepository
from app.services.vpsdb_sync_service import VpsDbSyncService
from app.utils.dates import dt_to_iso
from app.utils.query import get_int, get_str, get_csv_list
from app.utils.strings import truncate

backglass_widget_bp = Blueprint("backglass_widgets", __name__)


def _rows_from_backglasses(bgs: List[GameBackGlass]) -> List[dict]:
    """Create display rows for backglass widgets."""
    rows: List[dict] = []
    for b in bgs:
        rows.append(
            {
                "name": b.gameName or "",
                "version": b.version or "",
                "features": truncate(", ".join(b.features or []), 40),
                "authors": truncate(", ".join(b.authors or []), 40),
                "updatedAt": (dt_to_iso(b.updatedAt) or "")[:10],
                "url": b.best_url() or "",
                "imgUrl": b.imgUrl or "",
            }
        )
    return rows

def sync_tables():
    """Force a sync check for tables (downloads only when remote is newer)."""
    # This is a placeholder function. Implement sync logic as needed.
    settings = current_app.config["SETTINGS"]
    svc = VpsDbSyncService(settings)
    svc.sync_if_needed()


@backglass_widget_bp.get("/list")
def backglass_list_widget():
    """HTML card with a mini-table of recently updated backglasses."""
    limit = get_int("limit", 10, 1, 100)
    theme = get_str("theme", "light")
    features = get_csv_list("feature")

    sync_tables()
    repo = GameRepository.from_flask_app()
    games = repo.list_games()

    bgs = Game.backglasses_by_features(games, features, limit=limit) if features else Game.most_recent_backglasses(games, limit=limit)
    rows = _rows_from_backglasses(bgs)
    return render_template("backglasses_list.html", theme=theme, rows=rows, title="Recent Backglasses")


@backglass_widget_bp.get("/images")
def backglass_image_row():
    """HTML card with a row of clickable backglass images."""
    limit = get_int("limit", 10, 1, 100)
    theme = get_str("theme", "light")
    features = get_csv_list("feature")

    sync_tables()
    repo = GameRepository.from_flask_app()
    games = repo.list_games()

    bgs = Game.backglasses_by_features(games, features, limit=limit) if features else Game.most_recent_backglasses(games, limit=limit)
    rows = [r for r in _rows_from_backglasses(bgs) if r.get("imgUrl")]
    return render_template("backglasses_images.html", theme=theme, rows=rows, title="Recent Backglasses")

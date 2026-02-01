from __future__ import annotations

from typing import List

from flask import Blueprint, render_template, current_app

from app.models.game import Game
from app.models.game_table import GameTable
from app.services.game_repository import GameRepository
from app.services.vpsdb_sync_service import VpsDbSyncService
from app.utils.dates import dt_to_iso
from app.utils.query import get_int, get_str, get_csv_list
from app.utils.strings import truncate

table_widget_bp = Blueprint("table_widgets", __name__)


def _rows_from_tables(tables: List[GameTable]) -> List[dict]:
    """Create display rows for table widgets."""
    rows: List[dict] = []
    for t in tables:
        rows.append(
            {
                "name": t.gameName or "",
                "version": t.version or "",
                "format": t.tableFormat or "",
                "authors": truncate(", ".join(t.authors or []), 40),
                "updatedAt": (dt_to_iso(t.updatedAt) or "")[:10],
                "url": t.best_url() or "",
                "imgUrl": t.imgUrl or "",
            }
        )
    return rows

def sync_tables():
    """Force a sync check for tables (downloads only when remote is newer)."""
    # This is a placeholder function. Implement sync logic as needed.
    settings = current_app.config["SETTINGS"]
    svc = VpsDbSyncService(settings)
    svc.sync_if_needed()


@table_widget_bp.get("/list")
def tables_list_widget():
    """HTML card with a mini-table of recently updated tables."""
    limit = get_int("limit", 10, 1, 100)
    theme = get_str("theme", "light")
    formats = get_csv_list("format")

    sync_tables()
    repo = GameRepository.from_flask_app()
    games = repo.list_games()

    tables = Game.tables_by_formats(games, formats, limit=limit) if formats else Game.most_recent_tables(games, limit=limit)
    rows = _rows_from_tables(tables)
    return render_template("tables_list.html", theme=theme, rows=rows, title="Recent Tables")


@table_widget_bp.get("/images")
def tables_image_row():
    """HTML card with a row of clickable table images."""
    limit = get_int("limit", 10, 1, 100)
    theme = get_str("theme", "light")
    formats = get_csv_list("format")

    sync_tables()
    repo = GameRepository.from_flask_app()
    games = repo.list_games()

    tables = Game.tables_by_formats(games, formats, limit=limit) if formats else Game.most_recent_tables(games, limit=limit)
    rows = [r for r in _rows_from_tables(tables) if r.get("imgUrl")]
    return render_template("tables_images.html", theme=theme, rows=rows, title="Recent Tables")

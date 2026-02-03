from __future__ import annotations

from typing import Any, List

from flask import Blueprint, render_template

from app.models.game import Game
from app.models.game_table import GameTable
from app.services.game_repository import GameRepository
from app.utils.dates import dt_to_iso
from app.utils.query import get_int, get_str, get_csv_list
from app.utils.strings import truncate

table_widget_bp = Blueprint("table_widgets", __name__)


def _get_attr(obj: Any, name: str, default: Any = "") -> Any:
    """Safely get an attribute if it exists."""
    return getattr(obj, name, default)


def _game_field_from_table(t: GameTable, field: str) -> Any:
    """
    Try multiple locations for game metadata:
    1) flattened attrs (gameManufacturer/gameYear)
    2) nested dict attr 'game' if present
    3) default
    """
    if field == "manufacturer":
        v = _get_attr(t, "gameManufacturer", None)
        if v:
            return v
    if field == "year":
        v = _get_attr(t, "gameYear", None)
        if v is not None and v != "":
            return v

    game_obj = _get_attr(t, "game", None)
    if isinstance(game_obj, dict):
        return game_obj.get(field, "")

    return ""


def _rows_from_tables(tables: List[GameTable]) -> List[dict]:
    """Create display rows for table widgets."""
    rows: List[dict] = []
    for t in tables:
        created_dt = _get_attr(t, "createdAt", None) or _get_attr(t, "updatedAt", None)
        updated_dt = _get_attr(t, "updatedAt", None)
        authors = _get_attr(t, "authors", []) or []
        first_author = authors[0] if authors else ""

        rows.append(
            {
                "name": _get_attr(t, "gameName", "") or "",
                "manufacturer": _game_field_from_table(t, "manufacturer") or "",
                "year": _game_field_from_table(t, "year") or "",
                "version": _get_attr(t, "version", "") or "",
                "format": _get_attr(t, "tableFormat", "") or "",
                "authors": truncate(first_author, 40),
                "createdAt": (dt_to_iso(created_dt) or "")[:10],
                "updatedAt": (dt_to_iso(updated_dt) or "")[:10],
                "url": (t.best_url() if hasattr(t, "best_url") else "") or "",
                "imgUrl": _get_attr(t, "imgUrl", "") or "",
            }
        )
    return rows


def _norm_sort(value: str | None) -> str:
    """Normalize sort to createdAt/updatedAt (default createdAt)."""
    v = (value or "").strip().lower()
    if v in ("updatedat", "updated", "u"):
        return "updatedAt"
    return "createdAt"


@table_widget_bp.get("/list")
def tables_list_widget():
    """HTML card with a mini-table of most recently created/updated tables."""
    limit = get_int("limit", 10, 1, 100)
    theme = get_str("theme", "light")
    formats = get_csv_list("format")
    sort = _norm_sort(get_str("sort", None))

    repo = GameRepository.from_flask_app()
    games = repo.list_games()

    tables = (
        Game.tables_by_formats(games, formats, limit=limit, sort=sort)  # type: ignore[arg-type]
        if formats
        else Game.most_recent_tables(games, limit=limit, sort=sort)  # type: ignore[arg-type]
    )

    rows = _rows_from_tables(tables)
    return render_template("tables_list.html", theme=theme, rows=rows, title="Recent Tables", sort=sort)


@table_widget_bp.get("/images")
def tables_image_row():
    """HTML card with a row of clickable table images."""
    limit = get_int("limit", 10, 1, 100)
    theme = get_str("theme", "light")
    formats = get_csv_list("format")
    sort = _norm_sort(get_str("sort", None))

    repo = GameRepository.from_flask_app()
    games = repo.list_games()

    tables = (
        Game.tables_by_formats(games, formats, limit=limit, sort=sort)  # type: ignore[arg-type]
        if formats
        else Game.most_recent_tables(games, limit=limit, sort=sort)  # type: ignore[arg-type]
    )

    rows = [r for r in _rows_from_tables(tables) if r.get("imgUrl")]
    return render_template("tables_images.html", theme=theme, rows=rows, title="Recent Tables", sort=sort)

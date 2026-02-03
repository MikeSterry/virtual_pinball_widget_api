from __future__ import annotations

from typing import Any, List

from flask import Blueprint, render_template

from app.models.game import Game
from app.models.game_back_glass import GameBackGlass
from app.services.game_repository import GameRepository
from app.utils.dates import dt_to_iso
from app.utils.query import get_int, get_str, get_csv_list
from app.utils.strings import truncate

backglass_widget_bp = Blueprint("backglass_widgets", __name__)


def _get_attr(obj: Any, name: str, default: Any = "") -> Any:
    """Safely get an attribute if it exists."""
    return getattr(obj, name, default)


def _game_field_from_bg(b: GameBackGlass, field: str) -> Any:
    """See table controller for precedence rules."""
    if field == "manufacturer":
        v = _get_attr(b, "gameManufacturer", None)
        if v:
            return v
    if field == "year":
        v = _get_attr(b, "gameYear", None)
        if v is not None and v != "":
            return v

    game_obj = _get_attr(b, "game", None)
    if isinstance(game_obj, dict):
        return game_obj.get(field, "")

    return ""


def _rows_from_backglasses(bgs: List[GameBackGlass]) -> List[dict]:
    """Create display rows for backglass widgets."""
    rows: List[dict] = []
    for b in bgs:
        created_dt = _get_attr(b, "createdAt", None) or _get_attr(b, "updatedAt", None)
        updated_dt = _get_attr(b, "updatedAt", None)
        authors = _get_attr(b, "authors", []) or []
        first_author = authors[0] if authors else ""

        rows.append(
            {
                "name": _get_attr(b, "gameName", "") or "",
                "manufacturer": _game_field_from_bg(b, "manufacturer") or "",
                "year": _game_field_from_bg(b, "year") or "",
                "version": _get_attr(b, "version", "") or "",
                "features": truncate(", ".join(_get_attr(b, "features", []) or []), 40),
                "authors": truncate(first_author, 40),
                "createdAt": (dt_to_iso(created_dt) or "")[:10],
                "updatedAt": (dt_to_iso(updated_dt) or "")[:10],
                "url": (b.best_url() if hasattr(b, "best_url") else "") or "",
                "imgUrl": _get_attr(b, "imgUrl", "") or "",
            }
        )
    return rows


def _norm_sort(value: str | None) -> str:
    """Normalize sort to createdAt/updatedAt (default createdAt)."""
    v = (value or "").strip().lower()
    if v in ("updatedat", "updated", "u"):
        return "updatedAt"
    return "createdAt"


@backglass_widget_bp.get("/list")
def backglass_list_widget():
    """HTML card with a mini-table of most recently created/updated backglasses."""
    limit = get_int("limit", 10, 1, 100)
    theme = get_str("theme", "light")
    features = get_csv_list("feature")
    sort = _norm_sort(get_str("sort", None))

    repo = GameRepository.from_flask_app()
    games = repo.list_games()

    bgs = (
        Game.backglasses_by_features(games, features, limit=limit, sort=sort)  # type: ignore[arg-type]
        if features
        else Game.most_recent_backglasses(games, limit=limit, sort=sort)  # type: ignore[arg-type]
    )

    rows = _rows_from_backglasses(bgs)
    return render_template("backglasses_list.html", theme=theme, rows=rows, title="Recent Backglasses", sort=sort)


@backglass_widget_bp.get("/images")
def backglass_image_row():
    """HTML card with a row of clickable backglass images."""
    limit = get_int("limit", 10, 1, 100)
    theme = get_str("theme", "light")
    features = get_csv_list("feature")
    sort = _norm_sort(get_str("sort", None))

    repo = GameRepository.from_flask_app()
    games = repo.list_games()

    bgs = (
        Game.backglasses_by_features(games, features, limit=limit, sort=sort)  # type: ignore[arg-type]
        if features
        else Game.most_recent_backglasses(games, limit=limit, sort=sort)  # type: ignore[arg-type]
    )

    rows = [r for r in _rows_from_backglasses(bgs) if r.get("imgUrl")]
    return render_template("backglasses_images.html", theme=theme, rows=rows, title="Recent Backglasses", sort=sort)

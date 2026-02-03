from __future__ import annotations

from flask import Blueprint, jsonify

from app.models.game import Game
from app.services.game_repository import GameRepository
from app.utils.query import get_int, get_str, get_csv_list
from app.utils.comparators import (
    sort_games_by_created_at,
    sort_games_by_updated_at,
    sort_tables_by_updated_at,
    sort_tables_by_created_at,
    sort_backglasses_by_updated_at,
    sort_backglasses_by_created_at,
)

api_bp = Blueprint("api", __name__)


@api_bp.get("/games")
def list_games():
    """Return a JSON list of games with child models."""
    limit = get_int("limit", default=50, min_value=1, max_value=500)
    sort_mode = (get_str("sort", "game_created") or "game_created").strip().lower()

    repo = GameRepository.from_flask_app()
    games = repo.list_games()

    if sort_mode == "table_created":
        tables = sort_tables_by_created_at([t for g in games for t in g.tableFiles])[:limit]
        game_ids: list[str] = []
        for t in tables:
            if t.gameId and t.gameId not in game_ids:
                game_ids.append(t.gameId)
        games = [g for g in games if g.id in set(game_ids)]
        games = sorted(games, key=lambda g: game_ids.index(g.id))
    elif sort_mode == "table_updated":
        tables = sort_tables_by_updated_at([t for g in games for t in g.tableFiles])[:limit]
        game_ids: list[str] = []
        for t in tables:
            if t.gameId and t.gameId not in game_ids:
                game_ids.append(t.gameId)
        games = [g for g in games if g.id in set(game_ids)]
        games = sorted(games, key=lambda g: game_ids.index(g.id))
    elif sort_mode == "backglass_created":
        bgs = sort_backglasses_by_created_at([b for g in games for b in g.b2sFiles])[:limit]
        game_ids: list[str] = []
        for b in bgs:
            if b.gameId and b.gameId not in game_ids:
                game_ids.append(b.gameId)
        games = [g for g in games if g.id in set(game_ids)]
        games = sorted(games, key=lambda g: game_ids.index(g.id))
    elif sort_mode == "backglass_updated":
        bgs = sort_backglasses_by_updated_at([b for g in games for b in g.b2sFiles])[:limit]
        game_ids: list[str] = []
        for b in bgs:
            if b.gameId and b.gameId not in game_ids:
                game_ids.append(b.gameId)
        games = [g for g in games if g.id in set(game_ids)]
        games = sorted(games, key=lambda g: game_ids.index(g.id))
    elif sort_mode == "game_updated":
        games = sort_games_by_updated_at(games)[:limit]
    else:
        games = sort_games_by_created_at(games)[:limit]

    return jsonify({"count": len(games), "games": [g.to_dict() for g in games]})


@api_bp.get("/tables")
def list_tables():
    """Return a flattened list of most-recent tables (optionally filtered by format)."""
    limit = get_int("limit", default=50, min_value=1, max_value=500)
    formats = get_csv_list("format")

    repo = GameRepository.from_flask_app()
    games = repo.list_games()

    tables = Game.tables_by_formats(games, formats, limit=limit) if formats else Game.most_recent_tables(games, limit=limit)
    return jsonify({"count": len(tables), "tables": [t.to_dict() for t in tables]})


@api_bp.get("/backglasses")
def list_backglasses():
    """Return a flattened list of most-recent backglasses (optionally filtered by feature)."""
    limit = get_int("limit", default=50, min_value=1, max_value=500)
    features = get_csv_list("feature")

    repo = GameRepository.from_flask_app()
    games = repo.list_games()

    bgs = Game.backglasses_by_features(games, features, limit=limit) if features else Game.most_recent_backglasses(games, limit=limit)
    return jsonify({"count": len(bgs), "backglasses": [b.to_dict() for b in bgs]})

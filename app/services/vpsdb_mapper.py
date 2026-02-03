from __future__ import annotations

from typing import Any, Dict, List

from app.models.game import Game
from app.models.game_table import GameTable
from app.models.game_back_glass import GameBackGlass
from app.utils.dates import epoch_to_dt


class VpsDbMapper:
    """Maps VPSDB JSON objects into our typed model classes."""

    def map_games(self, raw: Any) -> List[Game]:
        """Map raw JSON root into a list of Game models."""
        items = self._extract_items(raw)
        return [g for g in (self._map_game(it) for it in items) if g is not None]

    def _extract_items(self, raw: Any) -> List[Dict[str, Any]]:
        """Extract the top-level array from common container shapes."""
        if isinstance(raw, list):
            return [x for x in raw if isinstance(x, dict)]
        if isinstance(raw, dict):
            for key in ("data", "items", "games"):
                v = raw.get(key)
                if isinstance(v, list):
                    return [x for x in v if isinstance(x, dict)]
        return []

    def _map_game(self, it: Dict[str, Any]) -> Game | None:
        """Map a single game dict."""
        gid = str(it.get("id") or "")
        if not gid:
            return None

        updated_dt = epoch_to_dt(it.get("updatedAt"))
        created_dt = epoch_to_dt(it.get("createdAt")) or updated_dt

        game = Game(
            id=gid,
            name=it.get("name"),
            manufacturer=it.get("manufacturer"),
            year=self._safe_int(it.get("year")),
            createdAt=created_dt,
            updatedAt=updated_dt,
        )

        for t in self._as_dict_list(it.get("tableFiles")):
            mapped = self._map_table(t, game)
            if mapped:
                game.tableFiles.append(mapped)

        for b in self._as_dict_list(it.get("b2sFiles")):
            mapped = self._map_backglass(b, game)
            if mapped:
                game.b2sFiles.append(mapped)

        return game

    def _map_table(self, it: Dict[str, Any], parent: Game) -> GameTable | None:
        """Map a table dict."""
        tid = str(it.get("id") or "")
        if not tid:
            return None

        # allow child entries to override parent via embedded "game" dict
        game_meta = it.get("game") if isinstance(it.get("game"), dict) else {}
        game_id = str(game_meta.get("id") or parent.id)
        game_name = str(game_meta.get("name") or parent.name or "")
        game_mfr = game_meta.get("manufacturer") or parent.manufacturer
        game_year = self._safe_int(game_meta.get("year")) if "year" in game_meta else parent.year

        t = GameTable(
            id=tid,
            version=it.get("version"),
            tableFormat=it.get("tableFormat"),
            authors=self._as_str_list(it.get("authors")),
            imgUrl=it.get("imgUrl"),
            updatedAt=epoch_to_dt(it.get("updatedAt")) or epoch_to_dt(it.get("createdAt")),
            createdAt=epoch_to_dt(it.get("createdAt")),
            gameId=game_id,
            gameName=game_name,
            gameManufacturer=game_mfr,
            gameYear=game_year,
        )

        for u in self._as_dict_list(it.get("urls")):
            url = u.get("url")
            if url:
                t.add_url(url=str(url), broken=bool(u.get("broken", False)))

        return t

    def _map_backglass(self, it: Dict[str, Any], parent: Game) -> GameBackGlass | None:
        """Map a backglass dict."""
        bid = str(it.get("id") or "")
        if not bid:
            return None

        game_meta = it.get("game") if isinstance(it.get("game"), dict) else {}
        game_id = str(game_meta.get("id") or parent.id)
        game_name = str(game_meta.get("name") or parent.name or "")
        game_mfr = game_meta.get("manufacturer") or parent.manufacturer
        game_year = self._safe_int(game_meta.get("year")) if "year" in game_meta else parent.year

        b = GameBackGlass(
            id=bid,
            version=it.get("version"),
            authors=self._as_str_list(it.get("authors")),
            features=self._as_str_list(it.get("features")),
            imgUrl=it.get("imgUrl"),
            updatedAt=epoch_to_dt(it.get("updatedAt")),
            createdAt=epoch_to_dt(it.get("createdAt")) or epoch_to_dt(it.get("updatedAt")),
            gameId=game_id,
            gameName=game_name,
            gameManufacturer=game_mfr,
            gameYear=game_year,
        )

        for u in self._as_dict_list(it.get("urls")):
            url = u.get("url")
            if url:
                b.add_url(url=str(url), broken=bool(u.get("broken", False)))

        return b

    def _as_dict_list(self, v: Any) -> List[Dict[str, Any]]:
        """Return a list of dicts from a value."""
        if isinstance(v, list):
            return [x for x in v if isinstance(x, dict)]
        return []

    def _as_str_list(self, v: Any) -> List[str]:
        """Return a list of strings from a value."""
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x) for x in v if str(x).strip()]
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return [str(v)]

    def _safe_int(self, v: Any) -> int | None:
        """Parse int safely."""
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

from app.configs.settings import Settings
from app.services.vpsdb_sync_service import VpsDbSyncService


@dataclass
class CachedPayload:
    """Simple in-memory cache payload."""
    loaded_at: float
    data: Any


class VpsDbLoader:
    """Loads VPSDB JSON from a **local** copy, syncing from remote when needed."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._cache: CachedPayload | None = None
        self._sync = VpsDbSyncService(settings)

    def _cache_valid(self) -> bool:
        """Return True when cache exists and is within TTL."""
        if not self._cache:
            return False
        age = time.time() - self._cache.loaded_at
        return age < self._settings.CACHE_TTL_SECONDS

    def load_raw(self) -> Any:
        """Return the raw parsed JSON with caching."""
        if self._cache_valid():
            return self._cache.data

        data = self._load_uncached()
        self._cache = CachedPayload(loaded_at=time.time(), data=data)
        return data

    def _load_uncached(self) -> Any:
        """Load JSON from disk, syncing first if configured."""
        if self._settings.SYNC_ON_START:
            # Best-effort sync; failures should not prevent running if local exists.
            try:
                self._sync.sync_if_needed()
            except Exception:
                if not self._sync.local_json_exists():
                    raise

        with open(self._settings.LOCAL_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

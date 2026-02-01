from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Central configuration model loaded from env vars."""

    VPSDB_REMOTE_URL: str
    VPSDB_LASTUPDATED_URL: str

    STORAGE_DIR: str
    LOCAL_JSON_PATH: str
    LOCAL_TIMESTAMP_PATH: str

    CACHE_TTL_SECONDS: int
    SYNC_ON_START: bool

    @staticmethod
    def _get_int(name: str, default: int) -> int:
        """Read an int env var with a safe default."""
        try:
            return int(os.getenv(name, str(default)))
        except ValueError:
            return default

    @staticmethod
    def _get_bool(name: str, default: bool) -> bool:
        """Read a bool env var with a safe default."""
        v = os.getenv(name, None)
        if v is None:
            return default
        return v.strip().lower() in ("1", "true", "t", "yes", "y", "on")

    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables."""
        storage_dir = os.getenv("VPSDB_STORAGE_DIR", "./data").rstrip("/")
        local_json = os.getenv("VPSDB_LOCAL_JSON_PATH", f"{storage_dir}/vpsdb.json")
        local_ts = os.getenv("VPSDB_LOCAL_TIMESTAMP_PATH", f"{storage_dir}/vpsdb.lastUpdated.json")

        return cls(
            VPSDB_REMOTE_URL=os.getenv(
                "VPSDB_REMOTE_URL",
                "https://virtualpinballspreadsheet.github.io/vps-db/db/vpsdb.json",
            ),
            VPSDB_LASTUPDATED_URL=os.getenv(
                "VPSDB_LASTUPDATED_URL",
                "https://virtualpinballspreadsheet.github.io/vps-db/lastUpdated.json",
            ),
            STORAGE_DIR=storage_dir,
            LOCAL_JSON_PATH=local_json,
            LOCAL_TIMESTAMP_PATH=local_ts,
            CACHE_TTL_SECONDS=cls._get_int("CACHE_TTL_SECONDS", 900),
            SYNC_ON_START=cls._get_bool("VPSDB_SYNC_ON_START", True),
        )

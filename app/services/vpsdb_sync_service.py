from __future__ import annotations

import json
import os
from dataclasses import dataclass
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.clients.vpsdb_client import VpsDbClient
from app.configs.settings import Settings


@dataclass
class SyncResult:
    """Result of a sync operation."""
    updated: bool
    local_timestamp: int
    remote_timestamp: int


class VpsDbSyncService:
    """Keeps a local VPS DB JSON copy in sync with the remote source."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = VpsDbClient(
            last_updated_url=settings.VPSDB_LASTUPDATED_URL,
            db_url=settings.VPSDB_REMOTE_URL,
        )

    def ensure_storage_dir(self) -> None:
        """Ensure the storage directory exists."""
        os.makedirs(self._settings.STORAGE_DIR, exist_ok=True)

    def read_local_timestamp(self) -> int:
        """Read the local associated epoch timestamp (0 when missing/invalid)."""
        try:
            with open(self._settings.LOCAL_TIMESTAMP_PATH, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if isinstance(payload, int):
                return int(payload)
            if isinstance(payload, dict) and "lastUpdated" in payload:
                return int(payload["lastUpdated"])
        except Exception:
            return 0
        return 0

    def write_local_timestamp(self, epoch: int) -> None:
        """Write the local associated epoch timestamp."""
        self.ensure_storage_dir()
        payload = {"lastUpdated": int(epoch)}
        with open(self._settings.LOCAL_TIMESTAMP_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f)

    def local_json_exists(self) -> bool:
        """Return True when the local JSON file exists."""
        return os.path.exists(self._settings.LOCAL_JSON_PATH)

    def sync_if_needed(self) -> SyncResult:
        """Sync local file if the remote timestamp is newer.

        - If local JSON doesn't exist, we always download.
        - If remote lastUpdated > local lastUpdated, download and update both files.
        """
        self.ensure_storage_dir()
        local_ts = self.read_local_timestamp()
        remote_ts = self._client.fetch_remote_timestamp()

        needs_download = (not self.local_json_exists()) or (remote_ts > local_ts)
        if not needs_download:
            return SyncResult(updated=False, local_timestamp=local_ts, remote_timestamp=remote_ts)

        json_text = self._client.fetch_db_json_text()
        try:
            with self.open_file_with_tenacity(self._settings.LOCAL_JSON_PATH) as f:
                f.write(json_text)
        except Exception as e:
            print(f"Failed to open file after all retries: {e}")

        self.write_local_timestamp(remote_ts)
        return SyncResult(updated=True, local_timestamp=remote_ts, remote_timestamp=remote_ts)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((FileNotFoundError, IOError, PermissionError))
    )
    def open_file_with_tenacity(self, filepath: str, mode: str ='w', encoding:str ='utf-8'):
        """Function to open a file with automatic retries on specific IO exceptions."""
        print(f"Attempting to open file: {filepath}")
        return open(filepath, mode, encoding)

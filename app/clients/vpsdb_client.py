from __future__ import annotations

import requests


class VpsDbClient:
    """HTTP client for the upstream VPS DB endpoints."""

    def __init__(self, last_updated_url: str, db_url: str, timeout_seconds: int = 30):
        self._last_updated_url = last_updated_url
        self._db_url = db_url
        self._timeout = timeout_seconds

    def fetch_remote_timestamp(self) -> int:
        """Fetch the remote epoch timestamp from lastUpdated.json.

        Expected payload shape (current upstream): { "lastUpdated": 1234567890 }
        We also support plain integer payloads defensively.
        """
        resp = requests.get(self._last_updated_url, timeout=self._timeout)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, int):
            return int(data)
        if isinstance(data, dict):
            # Preferred key from upstream
            if "lastUpdated" in data:
                return int(data["lastUpdated"])
            # Defensive: use first int-like value
            for v in data.values():
                try:
                    return int(v)
                except (TypeError, ValueError):
                    continue

        raise ValueError("Unexpected lastUpdated.json payload shape")

    def fetch_db_json_text(self) -> str:
        """Fetch the full VPS DB JSON as text."""
        resp = requests.get(self._db_url, timeout=self._timeout)
        resp.raise_for_status()
        return resp.text

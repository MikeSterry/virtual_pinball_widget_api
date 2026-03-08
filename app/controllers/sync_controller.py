from __future__ import annotations

from flask import Blueprint, current_app, jsonify
import logging
from app.services.vpsdb_sync_service import VpsDbSyncService

sync_bp = Blueprint("sync", __name__)
Logger = logging.getLogger(__name__)


@sync_bp.post("/sync")
def sync_now():
    """Force a sync check (downloads only when remote is newer)."""
    settings = current_app.config["SETTINGS"]
    svc = VpsDbSyncService(settings)
    result = svc.sync_if_needed()
    logging.info(f"Received request for /sync/sync, sync result: updated={result.updated}, local_timestamp={result.local_timestamp}, remote_timestamp={result.remote_timestamp}")
    return jsonify(
        {
            "updated": result.updated,
            "localTimestamp": result.local_timestamp,
            "remoteTimestamp": result.remote_timestamp,
        }
    )

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from app.services.vpsdb_sync_service import VpsDbSyncService

sync_bp = Blueprint("sync", __name__)


@sync_bp.post("/sync")
def sync_now():
    """Force a sync check (downloads only when remote is newer)."""
    settings = current_app.config["SETTINGS"]
    svc = VpsDbSyncService(settings)
    result = svc.sync_if_needed()
    return jsonify(
        {
            "updated": result.updated,
            "localTimestamp": result.local_timestamp,
            "remoteTimestamp": result.remote_timestamp,
        }
    )

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from app.services.vpsdb_sync_service import VpsDbSyncService

vpsdb_sync_bp = Blueprint("vpsdb_sync", __name__)


@vpsdb_sync_bp.get("/sync/status")
def sync_status():
    """Return local vs remote sync timestamps without downloading the DB."""
    settings = current_app.config["SETTINGS"]
    svc = VpsDbSyncService(settings)

    local_ts = svc.read_local_timestamp()
    # Remote timestamp call is the same one used to decide whether to download.
    remote_ts = svc._client.fetch_remote_timestamp()  # intentionally internal; kept in one place

    return jsonify({"localTimestamp": local_ts, "remoteTimestamp": remote_ts})


@vpsdb_sync_bp.post("/sync")
def sync_now():
    """Manual sync: download the DB only if the remote timestamp is newer."""
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

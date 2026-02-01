from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from app.services.vpsdb_sync_service import VpsDbSyncService

vpsdb_sync_bp = Blueprint("vpsdb_sync", __name__)


def _parse_bool(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "t", "yes", "y", "on")


@vpsdb_sync_bp.get("/sync/status")
def sync_status():
    """Return local vs remote sync timestamps.

    Query params:
    - remote=true|false (default: true)
      When false, the remote timestamp is not fetched.
    """
    settings = current_app.config["SETTINGS"]
    svc = VpsDbSyncService(settings)

    include_remote = _parse_bool(request.args.get("remote"), default=True)

    local_ts = svc.read_local_timestamp()
    remote_ts = None

    if include_remote:
        remote_ts = svc._client.fetch_remote_timestamp()

    return jsonify(
        {
            "localTimestamp": local_ts,
            "remoteTimestamp": remote_ts,
        }
    )


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

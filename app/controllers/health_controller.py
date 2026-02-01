from __future__ import annotations

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    """Health check endpoint used by docker healthchecks and monitoring."""
    return jsonify({"status": "ok"})

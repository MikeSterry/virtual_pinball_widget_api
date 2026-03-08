from __future__ import annotations
import logging
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)
Logger = logging.getLogger(__name__)


@health_bp.get("/health")
def health():
    """Health check endpoint used by docker healthchecks and monitoring."""
    logging.info("Received health check request")
    return jsonify({"status": "ok"})

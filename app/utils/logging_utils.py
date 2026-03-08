"""Logging helpers."""

import logging


def configure_logging(level_name: str) -> None:
    """Configure application logging once."""
    level = getattr(logging, (level_name or "INFO").upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
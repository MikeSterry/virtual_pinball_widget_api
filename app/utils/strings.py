from __future__ import annotations


def truncate(text: str | None, max_len: int = 60) -> str:
    """Truncate a string for display."""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"

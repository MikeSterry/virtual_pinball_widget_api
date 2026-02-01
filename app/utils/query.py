from __future__ import annotations

from flask import request


def get_str(name: str, default: str | None = None) -> str | None:
    """Read a string query param."""
    v = request.args.get(name, default)
    return v if v not in ("", None) else default


def get_int(name: str, default: int, min_value: int = 1, max_value: int = 500) -> int:
    """Read an int query param with bounds."""
    v = request.args.get(name, None)
    try:
        i = int(v) if v is not None else default
    except ValueError:
        i = default
    return max(min_value, min(max_value, i))


def get_bool(name: str, default: bool = False) -> bool:
    """Read a boolean query param."""
    v = request.args.get(name, None)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "t", "yes", "y", "on")


def get_csv_list(name: str) -> list[str]:
    """Read a comma-separated list query param.

    Example: ?format=VPX,FP  ->  ["vpx", "fp"]
    """
    raw = request.args.get(name, "")
    parts = [p.strip().lower() for p in raw.split(",") if p.strip()]
    out: list[str] = []
    for p in parts:
        if p not in out:
            out.append(p)
    return out

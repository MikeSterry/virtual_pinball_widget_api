from __future__ import annotations

from typing import Any, Dict


class BaseModel:
    """Base model providing get/set/update helpers."""

    def get_attr(self, name: str, default: Any = None) -> Any:
        """Get an attribute value with a default."""
        return getattr(self, name, default)

    def set_attr(self, name: str, value: Any) -> None:
        """Set an attribute value."""
        setattr(self, name, value)

    def update_attr(self, name: str, value: Any) -> None:
        """Alias for set_attr for clarity when updating."""
        self.set_attr(name, value)

    def update_from_dict(self, updates: Dict[str, Any]) -> None:
        """Bulk update fields from a dict."""
        for k, v in updates.items():
            self.set_attr(k, v)

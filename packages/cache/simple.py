"""Simple in-memory TTL cache for triggers."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass(slots=True)
class CacheEntry:
    value: Any
    expires_at: float


class TTLCache:
    def __init__(self, default_ttl: float = 3600.0) -> None:
        self.default_ttl = default_ttl
        self._store: Dict[str, CacheEntry] = {}

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        expires = time.time() + (ttl if ttl is not None else self.default_ttl)
        self._store[key] = CacheEntry(value=value, expires_at=expires)

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            return None
        if entry.expires_at < time.time():
            self._store.pop(key, None)
            return None
        return entry.value

    def clear(self) -> None:
        self._store.clear()


__all__ = ["TTLCache"]

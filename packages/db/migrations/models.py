"""Migration primitives for the lightweight migration runner."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncEngine

UpgradeCallable = Callable[[AsyncEngine], Awaitable[None]]
DowngradeCallable = Callable[[AsyncEngine], Awaitable[None]]


@dataclass(frozen=True)
class Migration:
    """Represents a reversible database migration step."""

    id: str
    name: str
    upgrade: UpgradeCallable
    downgrade: DowngradeCallable

    def __post_init__(self) -> None:  # pragma: no cover - defensive
        if not self.id:
            msg = "Migration id must be non-empty"
            raise ValueError(msg)
        if not self.name:
            msg = "Migration name must be non-empty"
            raise ValueError(msg)

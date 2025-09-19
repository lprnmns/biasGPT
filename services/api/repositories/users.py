"""User repository utilities."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import User

from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.get(email=email)

    async def activate(self, user_id: str) -> int:
        return await self.update({"id": user_id}, {"is_active": True})

    async def deactivate(self, user_id: str) -> int:
        return await self.update({"id": user_id}, {"is_active": False})


__all__ = ["UserRepository"]

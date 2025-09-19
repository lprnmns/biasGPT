"""Wallet repository for managing tracked addresses."""

from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import Wallet

from .base import BaseRepository


class WalletRepository(BaseRepository[Wallet]):
    model = Wallet

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_active(self) -> Iterable[Wallet]:
        return await self.list(filters={"is_active": True})

    async def set_active(self, wallet_id: str, active: bool) -> int:
        return await self.update({"id": wallet_id}, {"is_active": active})

    async def add_tags(self, wallet_id: str, tags: list[str]) -> Optional[Wallet]:
        wallet = await self.get(id=wallet_id)
        if not wallet:
            return None
        current = set(wallet.tags or [])
        wallet.tags = sorted(current.union(tags))
        await self.session.flush()
        return wallet


__all__ = ["WalletRepository"]

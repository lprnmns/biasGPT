"""Event and order related repositories."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import Event, Order, Wallet

from .base import BaseRepository


class EventRepository(BaseRepository[Event]):
    model = Event

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def recent_for_wallet(self, wallet_id: str, *, since_minutes: int = 60) -> Iterable[Event]:
        window = datetime.utcnow() - timedelta(minutes=since_minutes)
        stmt = (
            select(Event)
            .where(Event.wallet_id == wallet_id, Event.timestamp >= window)
            .order_by(desc(Event.timestamp))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def upsert(self, *, tx_hash: str, defaults: dict) -> Event:
        existing = await self.get(tx_hash=tx_hash)
        if existing:
            for key, value in defaults.items():
                setattr(existing, key, value)
            await self.session.flush()
            return existing
        return await self.create(tx_hash=tx_hash, **defaults)


class OrderRepository(BaseRepository[Order]):
    model = Order

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def for_wallet(self, wallet: Wallet) -> Iterable[Order]:
        stmt = (
            select(Order)
            .join(Event, Order.signal_event_id == Event.id)
            .where(Event.wallet_id == wallet.id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


__all__ = ["EventRepository", "OrderRepository"]

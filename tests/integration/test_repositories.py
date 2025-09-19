import pytest

from datetime import datetime

from packages.db.models import Event
from services.api.repositories import EventRepository, UserRepository, WalletRepository

from tests.fixtures.db import db_session  # noqa: F401


@pytest.mark.asyncio
async def test_user_repository_crud(db_session):
    repo = UserRepository(db_session)
    created = await repo.create(email="user@example.com", password_hash="hash")
    assert created.id

    fetched = await repo.get_by_email("user@example.com")
    assert fetched is not None
    assert fetched.id == created.id

    await repo.deactivate(created.id)
    await db_session.refresh(created)
    assert created.is_active is False


@pytest.mark.asyncio
async def test_wallet_repository_tags(db_session):
    repo = WalletRepository(db_session)
    wallet = await repo.create(address="0xabc", chain="ethereum")
    updated = await repo.add_tags(wallet.id, ["smart", "fund"])
    assert updated is not None
    assert updated.tags == ["fund", "smart"]


@pytest.mark.asyncio
async def test_event_repository_upsert(db_session):
    wallet_repo = WalletRepository(db_session)
    wallet = await wallet_repo.create(address="0xdef", chain="ethereum")

    repo = EventRepository(db_session)
    event = await repo.upsert(tx_hash="0x123", defaults={
        "wallet_id": wallet.id,
        "timestamp": datetime.utcnow(),
        "event_type": "transfer",
    })
    assert event.tx_hash == "0x123"
    second = await repo.upsert(tx_hash="0x123", defaults={"event_type": "swap"})
    assert second.event_type == "swap"

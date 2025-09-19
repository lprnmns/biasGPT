import pytest

from packages.db.models import (
    AuditLog,
    Base,
    BiasSnapshot,
    Event,
    EventAnalysis,
    Order,
    Position,
    Report,
    User,
    Wallet,
    WalletScore,
)

EXPECTED_TABLES = {
    "users",
    "wallets",
    "wallet_scores",
    "events",
    "event_analysis",
    "bias",
    "orders",
    "positions",
    "reports",
    "audit_logs",
}


def test_metadata_tables_present():
    tables = set(Base.metadata.tables.keys())
    assert EXPECTED_TABLES.issubset(tables)


@pytest.mark.parametrize(
    "model, primary_keys",
    [
        (User, {"id"}),
        (Wallet, {"id"}),
        (WalletScore, {"wallet_id", "timestamp"}),
        (Event, {"id"}),
        (EventAnalysis, {"event_id"}),
        (BiasSnapshot, {"timestamp", "asset", "timeframe"}),
        (Order, {"id"}),
        (Position, {"id"}),
        (Report, {"id"}),
        (AuditLog, {"id"}),
    ],
)
def test_primary_keys(model, primary_keys: set[str]):
    assert {col.name for col in model.__table__.primary_key.columns} == primary_keys


def test_wallet_score_relationships():
    mapper = WalletScore.__mapper__
    wallet_rel = mapper.relationships["wallet"]
    assert wallet_rel.mapper.class_ is Wallet
    assert wallet_rel.direction.name == "MANYTOONE"

    wallet_mapper = Wallet.__mapper__
    scores_rel = wallet_mapper.relationships["scores"]
    assert scores_rel.uselist is True
    assert "delete-orphan" in scores_rel.cascade


def test_event_relationship_config():
    analysis_rel = Event.__mapper__.relationships["analysis"]
    assert analysis_rel.uselist is False
    orders_rel = Event.__mapper__.relationships["orders"]
    assert orders_rel.uselist is True


def test_order_index_names():
    index_names = {index.name for index in Order.__table__.indexes}
    assert {"idx_orders_status", "idx_orders_client_id"}.issubset(index_names)


def test_bias_snapshot_index():
    index_names = {index.name for index in BiasSnapshot.__table__.indexes}
    assert "idx_bias_asset" in index_names


def test_audit_log_user_relationship():
    rel = AuditLog.__mapper__.relationships["user"]
    assert rel.mapper.class_ is User
    assert rel.uselist is False

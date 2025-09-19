"""Initial schema creation covering core trading tables."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Index, MetaData, Table, text
from sqlalchemy.ext.asyncio import AsyncEngine

from .models import Migration

metadata = MetaData()

# Users and authentication --------------------------------------------------
users = Table(
    "users",
    metadata,
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column("email", sa.String(255), nullable=False, unique=True),
    sa.Column("password_hash", sa.String(255), nullable=False),
    sa.Column("trading_mode", sa.String(20), nullable=False, server_default=sa.text("'demo'")),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("last_login", sa.DateTime(timezone=True)),
    sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    sa.Column("two_fa_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    sa.Column("two_fa_secret", sa.String(255)),
)
Index("idx_users_email", users.c.email, unique=True)

# Wallet catalog ------------------------------------------------------------
wallets = Table(
    "wallets",
    metadata,
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column("address", sa.String(42), nullable=False, unique=True),
    sa.Column("label", sa.String(100)),
    sa.Column("chain", sa.String(20), nullable=False, server_default=sa.text("'ethereum'")),
    sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("last_activity", sa.DateTime(timezone=True)),
    sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    sa.Column("tags", sa.JSON()),
    sa.Column("metadata", sa.JSON()),
)
Index("idx_wallets_active", wallets.c.is_active)

wallet_scores = Table(
    "wallet_scores",
    metadata,
    sa.Column("wallet_id", sa.String(36), sa.ForeignKey("wallets.id"), nullable=False),
    sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    sa.Column("credibility_1h", sa.Numeric(3, 1)),
    sa.Column("credibility_4h", sa.Numeric(3, 1)),
    sa.Column("credibility_24h", sa.Numeric(3, 1)),
    sa.Column("equity_usd", sa.Numeric(20, 2)),
    sa.Column("trading_volume_24h", sa.Numeric(20, 2)),
    sa.Column("win_rate", sa.Numeric(3, 2)),
    sa.Column("archetype", sa.String(50)),
    sa.PrimaryKeyConstraint("wallet_id", "timestamp", name="pk_wallet_scores"),
)
Index("idx_wallet_scores_composite", wallet_scores.c.wallet_id, wallet_scores.c.timestamp)

# Event pipeline ------------------------------------------------------------
events = Table(
    "events",
    metadata,
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    sa.Column("wallet_id", sa.String(36), sa.ForeignKey("wallets.id")),
    sa.Column("tx_hash", sa.String(66), nullable=False, unique=True),
    sa.Column("event_type", sa.String(50), nullable=False),
    sa.Column("asset", sa.String(20)),
    sa.Column("amount", sa.Numeric(30, 10)),
    sa.Column("notional_usd", sa.Numeric(20, 2)),
    sa.Column("size_fraction", sa.Numeric(5, 4)),
    sa.Column("venue", sa.String(50)),
    sa.Column("gas_price", sa.Numeric(20, 10)),
    sa.Column("is_first_since_watch", sa.Boolean(), server_default=sa.false()),
    sa.Column("raw_data", sa.JSON()),
    sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
)
Index("idx_events_wallet", events.c.wallet_id, events.c.timestamp)
Index("idx_events_type", events.c.event_type)

# LLM event analysis --------------------------------------------------------
event_analysis = Table(
    "event_analysis",
    metadata,
    sa.Column("event_id", sa.String(36), sa.ForeignKey("events.id"), primary_key=True),
    sa.Column("llm_classification", sa.String(100)),
    sa.Column("llm_confidence", sa.Numeric(3, 2)),
    sa.Column("llm_narrative", sa.Text()),
    sa.Column("pattern_matched", sa.String(100)),
    sa.Column("bias_impact", sa.Numeric(4, 3)),
    sa.Column("proposed_action", sa.JSON()),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
)

# Bias surface --------------------------------------------------------------
bias = Table(
    "bias",
    metadata,
    sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    sa.Column("asset", sa.String(20), nullable=False),
    sa.Column("timeframe", sa.String(10), nullable=False),
    sa.Column("value", sa.Numeric(4, 3)),
    sa.Column("components", sa.JSON()),
    sa.Column("confidence", sa.Numeric(3, 2)),
    sa.PrimaryKeyConstraint("timestamp", "asset", "timeframe", name="pk_bias"),
)
Index("idx_bias_asset", bias.c.asset, bias.c.timestamp)

# Orders --------------------------------------------------------------------
orders = Table(
    "orders",
    metadata,
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("trading_mode", sa.String(20), nullable=False),
    sa.Column("exchange", sa.String(20), nullable=False, server_default=sa.text("'okx'")),
    sa.Column("client_order_id", sa.String(100), nullable=False, unique=True),
    sa.Column("exchange_order_id", sa.String(100)),
    sa.Column("asset", sa.String(20), nullable=False),
    sa.Column("side", sa.String(10), nullable=False),
    sa.Column("order_type", sa.String(20), nullable=False),
    sa.Column("size", sa.Numeric(20, 10)),
    sa.Column("price", sa.Numeric(20, 10)),
    sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'pending'")),
    sa.Column("filled_size", sa.Numeric(20, 10), server_default=sa.text("'0'")),
    sa.Column("avg_fill_price", sa.Numeric(20, 10)),
    sa.Column("fees", sa.Numeric(20, 10), server_default=sa.text("'0'")),
    sa.Column("stop_loss", sa.Numeric(20, 10)),
    sa.Column("take_profit", sa.JSON()),
    sa.Column("signal_event_id", sa.String(36), sa.ForeignKey("events.id")),
    sa.Column("policy_snapshot", sa.JSON()),
    sa.Column("error_message", sa.Text()),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
)
Index("idx_orders_status", orders.c.status)
Index("idx_orders_client_id", orders.c.client_order_id)

# Positions -----------------------------------------------------------------
positions = Table(
    "positions",
    metadata,
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column("opened_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("closed_at", sa.DateTime(timezone=True)),
    sa.Column("trading_mode", sa.String(20), nullable=False),
    sa.Column("asset", sa.String(20), nullable=False),
    sa.Column("side", sa.String(10), nullable=False),
    sa.Column("entry_price", sa.Numeric(20, 10)),
    sa.Column("exit_price", sa.Numeric(20, 10)),
    sa.Column("size", sa.Numeric(20, 10)),
    sa.Column("leverage", sa.Numeric(4, 2), server_default=sa.text("'1'")),
    sa.Column("unrealized_pnl", sa.Numeric(20, 2)),
    sa.Column("realized_pnl", sa.Numeric(20, 2)),
    sa.Column("fees_paid", sa.Numeric(20, 2)),
    sa.Column("funding_paid", sa.Numeric(20, 2)),
    sa.Column("max_drawdown", sa.Numeric(5, 2)),
    sa.Column("holding_time", sa.Integer()),
    sa.Column("risk_consumed", sa.Numeric(5, 4)),
    sa.Column("signal_wallet_id", sa.String(36), sa.ForeignKey("wallets.id")),
)
Index("idx_positions_closed_at", positions.c.closed_at)

# Reports -------------------------------------------------------------------
reports = Table(
    "reports",
    metadata,
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
    sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
    sa.Column("report_type", sa.String(20), server_default=sa.text("'4h'")),
    sa.Column("summary_markdown", sa.Text()),
    sa.Column("metrics", sa.JSON()),
    sa.Column("notable_events", sa.JSON()),
    sa.Column("delivered_at", sa.DateTime(timezone=True)),
    sa.Column("push_sent", sa.Boolean(), server_default=sa.false()),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
)
Index("idx_reports_period", reports.c.period_end)

# Audit logs ----------------------------------------------------------------
audit_logs = Table(
    "audit_logs",
    metadata,
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id")),
    sa.Column("action", sa.String(100), nullable=False),
    sa.Column("entity_type", sa.String(50)),
    sa.Column("entity_id", sa.String(36)),
    sa.Column("old_value", sa.JSON()),
    sa.Column("new_value", sa.JSON()),
    sa.Column("ip_address", sa.String(45)),
    sa.Column("user_agent", sa.Text()),
    sa.Column("trace_id", sa.String(100)),
)
Index("idx_audit_timestamp", audit_logs.c.timestamp)
Index("idx_audit_trace", audit_logs.c.trace_id)

TABLES = [
    users,
    wallets,
    wallet_scores,
    events,
    event_analysis,
    bias,
    orders,
    positions,
    reports,
    audit_logs,
]


async def _create_views(engine: AsyncEngine) -> None:
    view_sql = """
    CREATE VIEW IF NOT EXISTS active_positions_view AS
    SELECT
        p.id,
        p.opened_at,
        p.closed_at,
        p.trading_mode,
        p.asset,
        p.side,
        p.entry_price,
        p.exit_price,
        p.size,
        p.leverage,
        p.unrealized_pnl,
        p.realized_pnl,
        p.fees_paid,
        p.funding_paid,
        p.max_drawdown,
        p.holding_time,
        p.risk_consumed,
        p.signal_wallet_id,
        w.address AS signal_wallet,
        (
            SELECT ws.credibility_4h
            FROM wallet_scores ws
            WHERE ws.wallet_id = p.signal_wallet_id
            ORDER BY ws.timestamp DESC
            LIMIT 1
        ) AS wallet_credibility,
        (
            SELECT b.value
            FROM bias b
            WHERE b.asset = p.asset
            ORDER BY b.timestamp DESC
            LIMIT 1
        ) AS current_bias
    FROM positions p
    LEFT JOIN wallets w ON w.id = p.signal_wallet_id
    WHERE p.closed_at IS NULL
    """
    async with engine.begin() as conn:
        await conn.execute(text(view_sql))


async def _drop_views(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.execute(text("DROP VIEW IF EXISTS active_positions_view"))


async def upgrade(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    await _create_views(engine)


async def downgrade(engine: AsyncEngine) -> None:
    await _drop_views(engine)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


migration = Migration(
    id="0001_initial",
    name="initial_schema",
    upgrade=upgrade,
    downgrade=downgrade,
)

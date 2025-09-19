"""SQLAlchemy ORM models mirroring the core trading schema."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy import Index, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from .base import Base


def _uuid_str() -> str:
    return str(uuid4())


class User(Base):
    __tablename__ = "users"
    __table_args__ = (Index("idx_users_email", "email", unique=True),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    trading_mode: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'demo'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    two_fa_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    two_fa_secret: Mapped[Optional[str]] = mapped_column(String(255))

    audit_logs: Mapped[List[AuditLog]] = relationship("AuditLog", back_populates="user")


class Wallet(Base):
    __tablename__ = "wallets"
    __table_args__ = (Index("idx_wallets_active", "is_active"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    address: Mapped[str] = mapped_column(String(42), nullable=False, unique=True)
    label: Mapped[Optional[str]] = mapped_column(String(100))
    chain: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'ethereum'"))
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON)
    metadata_: Mapped[Optional[Dict[str, object]]] = mapped_column("metadata", JSON)

    scores: Mapped[List[WalletScore]] = relationship("WalletScore", back_populates="wallet", cascade="all, delete-orphan")
    events: Mapped[List[Event]] = relationship("Event", back_populates="wallet")
    signal_positions: Mapped[List[Position]] = relationship("Position", back_populates="signal_wallet")


class WalletScore(Base):
    __tablename__ = "wallet_scores"
    __table_args__ = (Index("idx_wallet_scores_composite", "wallet_id", "timestamp"),)

    wallet_id: Mapped[str] = mapped_column(ForeignKey("wallets.id"), primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    credibility_1h: Mapped[Optional[float]] = mapped_column(Numeric(3, 1))
    credibility_4h: Mapped[Optional[float]] = mapped_column(Numeric(3, 1))
    credibility_24h: Mapped[Optional[float]] = mapped_column(Numeric(3, 1))
    equity_usd: Mapped[Optional[float]] = mapped_column(Numeric(20, 2))
    trading_volume_24h: Mapped[Optional[float]] = mapped_column(Numeric(20, 2))
    win_rate: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    archetype: Mapped[Optional[str]] = mapped_column(String(50))

    wallet: Mapped[Wallet] = relationship("Wallet", back_populates="scores")


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("idx_events_wallet", "wallet_id", "timestamp"),
        Index("idx_events_type", "event_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    wallet_id: Mapped[Optional[str]] = mapped_column(ForeignKey("wallets.id"))
    tx_hash: Mapped[str] = mapped_column(String(66), nullable=False, unique=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    asset: Mapped[Optional[str]] = mapped_column(String(20))
    amount: Mapped[Optional[float]] = mapped_column(Numeric(30, 10))
    notional_usd: Mapped[Optional[float]] = mapped_column(Numeric(20, 2))
    size_fraction: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    venue: Mapped[Optional[str]] = mapped_column(String(50))
    gas_price: Mapped[Optional[float]] = mapped_column(Numeric(20, 10))
    is_first_since_watch: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)
    raw_data: Mapped[Optional[Dict[str, object]]] = mapped_column(JSON)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    wallet: Mapped[Optional[Wallet]] = relationship("Wallet", back_populates="events")
    analysis: Mapped[Optional[EventAnalysis]] = relationship("EventAnalysis", back_populates="event", uselist=False)
    orders: Mapped[List[Order]] = relationship("Order", back_populates="signal_event")


class EventAnalysis(Base):
    __tablename__ = "event_analysis"

    event_id: Mapped[str] = mapped_column(ForeignKey("events.id"), primary_key=True)
    llm_classification: Mapped[Optional[str]] = mapped_column(String(100))
    llm_confidence: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    llm_narrative: Mapped[Optional[str]] = mapped_column(Text)
    pattern_matched: Mapped[Optional[str]] = mapped_column(String(100))
    bias_impact: Mapped[Optional[float]] = mapped_column(Numeric(4, 3))
    proposed_action: Mapped[Optional[Dict[str, object]]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    event: Mapped[Event] = relationship("Event", back_populates="analysis")


class BiasSnapshot(Base):
    __tablename__ = "bias"
    __table_args__ = (Index("idx_bias_asset", "asset", "timestamp"),)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    asset: Mapped[str] = mapped_column(String(20), primary_key=True)
    timeframe: Mapped[str] = mapped_column(String(10), primary_key=True)
    value: Mapped[Optional[float]] = mapped_column(Numeric(4, 3))
    components: Mapped[Optional[Dict[str, object]]] = mapped_column(JSON)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index("idx_orders_status", "status"),
        Index("idx_orders_client_id", "client_order_id", unique=True),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    trading_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    exchange: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'okx'"))
    client_order_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    exchange_order_id: Mapped[Optional[str]] = mapped_column(String(100))
    asset: Mapped[str] = mapped_column(String(20), nullable=False)
    side: Mapped[str] = mapped_column(String(10), nullable=False)
    order_type: Mapped[str] = mapped_column(String(20), nullable=False)
    size: Mapped[Optional[float]] = mapped_column(Numeric(20, 10))
    price: Mapped[Optional[float]] = mapped_column(Numeric(20, 10))
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'pending'"))
    filled_size: Mapped[Optional[float]] = mapped_column(Numeric(20, 10), server_default=text("'0'"))
    avg_fill_price: Mapped[Optional[float]] = mapped_column(Numeric(20, 10))
    fees: Mapped[Optional[float]] = mapped_column(Numeric(20, 10), server_default=text("'0'"))
    stop_loss: Mapped[Optional[float]] = mapped_column(Numeric(20, 10))
    take_profit: Mapped[Optional[List[Dict[str, object]]]] = mapped_column(JSON)
    signal_event_id: Mapped[Optional[str]] = mapped_column(ForeignKey("events.id"))
    policy_snapshot: Mapped[Optional[Dict[str, object]]] = mapped_column(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    signal_event: Mapped[Optional[Event]] = relationship("Event", back_populates="orders")


class Position(Base):
    __tablename__ = "positions"
    __table_args__ = (Index("idx_positions_closed_at", "closed_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    trading_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    asset: Mapped[str] = mapped_column(String(20), nullable=False)
    side: Mapped[str] = mapped_column(String(10), nullable=False)
    entry_price: Mapped[Optional[float]] = mapped_column(Numeric(20, 10))
    exit_price: Mapped[Optional[float]] = mapped_column(Numeric(20, 10))
    size: Mapped[Optional[float]] = mapped_column(Numeric(20, 10))
    leverage: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), server_default=text("'1'"))
    unrealized_pnl: Mapped[Optional[float]] = mapped_column(Numeric(20, 2))
    realized_pnl: Mapped[Optional[float]] = mapped_column(Numeric(20, 2))
    fees_paid: Mapped[Optional[float]] = mapped_column(Numeric(20, 2))
    funding_paid: Mapped[Optional[float]] = mapped_column(Numeric(20, 2))
    max_drawdown: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    holding_time: Mapped[Optional[int]] = mapped_column(Integer)
    risk_consumed: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    signal_wallet_id: Mapped[Optional[str]] = mapped_column(ForeignKey("wallets.id"))

    signal_wallet: Mapped[Optional[Wallet]] = relationship("Wallet", back_populates="signal_positions")


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (Index("idx_reports_period", "period_end"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    report_type: Mapped[str] = mapped_column(String(20), server_default=text("'4h'"))
    summary_markdown: Mapped[Optional[str]] = mapped_column(Text)
    metrics: Mapped[Optional[Dict[str, object]]] = mapped_column(JSON)
    notable_events: Mapped[Optional[List[Dict[str, object]]]] = mapped_column(JSON)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    push_sent: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_timestamp", "timestamp"),
        Index("idx_audit_trace", "trace_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(50))
    entity_id: Mapped[Optional[str]] = mapped_column(String(36))
    old_value: Mapped[Optional[Dict[str, object]]] = mapped_column(JSON)
    new_value: Mapped[Optional[Dict[str, object]]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100))

    user: Mapped[Optional[User]] = relationship("User", back_populates="audit_logs")


__all__ = [
    "User",
    "Wallet",
    "WalletScore",
    "Event",
    "EventAnalysis",
    "BiasSnapshot",
    "Order",
    "Position",
    "Report",
    "AuditLog",
]

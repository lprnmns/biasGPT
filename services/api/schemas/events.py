"""Pydantic schemas for event ingestion."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    tx_hash: str = Field(..., alias="txHash")
    wallet: str
    category: str
    timestamp: datetime
    asset: str | None = None
    amount: Decimal | None = None
    notional_usd: Decimal | None = Field(default=None, alias="notionalUsd")

    def to_worker_dict(self) -> Dict[str, Any]:
        data = self.model_dump(by_alias=True, exclude_none=True)
        data["timestamp"] = self.timestamp.isoformat()
        if self.amount is not None:
            data["amount"] = str(self.amount)
        if self.notional_usd is not None:
            data["notionalUsd"] = str(self.notional_usd)
        data.setdefault("wallet", self.wallet)
        data.setdefault("category", self.category)
        return data


class EventIngestRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    events: List[EventPayload]
    source: str | None = None

    @field_validator("events")
    @classmethod
    def ensure_events(cls, v: List[EventPayload]) -> List[EventPayload]:
        if not v:
            raise ValueError("events must contain at least one item")
        return v


class EventIngestResponse(BaseModel):
    success: bool
    enqueued: int


__all__ = ["EventPayload", "EventIngestRequest", "EventIngestResponse"]

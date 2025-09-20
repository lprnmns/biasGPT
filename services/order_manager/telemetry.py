"""Execution telemetry utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class ExecutionEvent:
    timestamp: datetime
    status: str
    payload: Dict[str, Any]
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TelemetryRecorder:
    """Collects execution events for auditing and monitoring."""

    def __init__(self) -> None:
        self._events: List[ExecutionEvent] = []

    def record_success(self, payload: Dict[str, Any], response: Dict[str, Any]) -> None:
        self._events.append(
            ExecutionEvent(
                timestamp=datetime.now(timezone.utc),
                status="success",
                payload=payload,
                response=response,
            )
        )

    def record_failure(self, payload: Dict[str, Any], error: str) -> None:
        self._events.append(
            ExecutionEvent(
                timestamp=datetime.now(timezone.utc),
                status="failure",
                payload=payload,
                error=error,
            )
        )

    @property
    def events(self) -> List[ExecutionEvent]:
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()


__all__ = ["TelemetryRecorder", "ExecutionEvent"]

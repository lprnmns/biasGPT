"""LLM cost tracking and alerting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


AlertSender = Callable[[str], None]


@dataclass(slots=True)
class LLMBudgetManager:
    daily_limit: float
    current_spend: float = 0.0
    alert_threshold: float = 0.8
    alert_sent: bool = False
    alert_sender: AlertSender | None = None

    def can_call(self, estimated_cost: float) -> bool:
        return (self.current_spend + estimated_cost) < self.daily_limit

    def track_usage(self, cost: float) -> None:
        self.current_spend += cost
        if not self.alert_sent and self.current_spend >= self.daily_limit * self.alert_threshold:
            self.alert_sent = True
            if self.alert_sender:
                self.alert_sender(f"LLM budget at {self.current_spend:.2f}/{self.daily_limit:.2f}")

    def reset(self) -> None:
        self.current_spend = 0.0
        self.alert_sent = False


__all__ = ["LLMBudgetManager"]

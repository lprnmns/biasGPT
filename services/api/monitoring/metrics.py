"""Metrics exposition utilities (Prometheus-like)."""

from __future__ import annotations

from typing import Dict


class MetricsRegistry:
    def __init__(self) -> None:
        self.metrics: Dict[str, float] = {}

    def gauge(self, name: str, value: float) -> None:
        self.metrics[name] = value

    def export(self) -> Dict[str, float]:
        return dict(self.metrics)


registry = MetricsRegistry()


async def get_metrics() -> Dict[str, float]:
    return registry.export()


__all__ = ["registry", "get_metrics"]

"""Risk monitoring utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List


@dataclass(slots=True)
class PositionSnapshot:
    asset: str
    side: str
    size: float
    risk: float
    pnl: float
    drawdown: float
    correlation_bucket: str


@dataclass(slots=True)
class RiskMetrics:
    open_positions: int
    total_exposure: float
    current_drawdown: float
    risk_consumed: float
    correlation_risk: float
    alerts: List[tuple[str, str]] = field(default_factory=list)


class RiskMonitor:
    def __init__(self, drawdown_limits: dict[str, float], correlation_limit: float, risk_limit: float) -> None:
        self.drawdown_limits = drawdown_limits
        self.correlation_limit = correlation_limit
        self.risk_limit = risk_limit

    def get_metrics(self, positions: Iterable[PositionSnapshot]) -> RiskMetrics:
        positions_list = list(positions)
        open_positions = len(positions_list)
        total_exposure = sum(abs(pos.size) for pos in positions_list)
        current_drawdown = max((pos.drawdown for pos in positions_list), default=0.0)
        risk_consumed = sum(pos.risk for pos in positions_list)

        buckets: dict[str, float] = {}
        for pos in positions_list:
            buckets[pos.correlation_bucket] = buckets.get(pos.correlation_bucket, 0.0) + abs(pos.size)
        correlation_risk = max(buckets.values(), default=0.0)

        alerts = self.check_alerts(total_exposure, risk_consumed, current_drawdown, correlation_risk)

        return RiskMetrics(
            open_positions=open_positions,
            total_exposure=float(round(total_exposure, 4)),
            current_drawdown=float(round(current_drawdown, 4)),
            risk_consumed=float(round(risk_consumed, 4)),
            correlation_risk=float(round(correlation_risk, 4)),
            alerts=alerts,
        )

    def check_alerts(
        self,
        exposure: float,
        risk_consumed: float,
        drawdown: float,
        correlation_risk: float,
    ) -> List[tuple[str, str]]:
        alerts: List[tuple[str, str]] = []
        if drawdown > self.drawdown_limits.get("daily", 100.0):
            alerts.append(("CRITICAL", "Daily drawdown limit exceeded"))
        if risk_consumed > self.risk_limit:
            alerts.append(("CRITICAL", "Risk budget exhausted"))
        if correlation_risk > self.correlation_limit:
            alerts.append(("WARNING", "Correlation risk high"))
        if exposure > 1.0:
            alerts.append(("WARNING", "Exposure over 100%"))
        return alerts


__all__ = ["RiskMonitor", "RiskMetrics", "PositionSnapshot"]

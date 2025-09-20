"""Risk policy validation logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Tuple


@dataclass(slots=True)
class ProposedTrade:
    trading_mode: str
    asset: str
    side: str
    size_percent: float
    leverage: float
    rr_ratio: float
    wallet_credibility: float


@dataclass(slots=True)
class PortfolioState:
    open_positions: int
    daily_trades: int
    total_risk: float
    correlation_risk: float
    drawdown_daily: float
    drawdown_weekly: float
    drawdown_monthly: float


class PolicyEngine:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def validate(
        self,
        trade: ProposedTrade,
        portfolio: PortfolioState,
        exposures: Mapping[str, float] | None = None,
    ) -> Tuple[bool, Dict[str, Dict[str, Any]]]:
        checks = {
            "risk_limit": lambda: self._check_risk_limit(trade),
            "drawdown": lambda: self._check_drawdown(portfolio),
            "correlation": lambda: self._check_correlation(portfolio, exposures or {}),
            "frequency": lambda: self._check_frequency(portfolio),
            "wallet_credibility": lambda: self._check_wallet_credibility(trade),
        }
        results: Dict[str, Dict[str, Any]] = {}
        hard_failures = {"risk_limit", "drawdown", "wallet_credibility", "correlation", "frequency"}
        for name, check in checks.items():
            passed, reason = check()
            results[name] = {"passed": passed, "reason": reason}
            if not passed and name in hard_failures:
                return False, results
        soft_failures = [name for name, result in results.items() if not result["passed"]]
        if len(soft_failures) > 2:
            return False, results
        return True, results

    def _pass(self) -> Tuple[bool, str]:  # pragma: no cover - helper
        return True, "not_implemented"

    def _check_risk_limit(self, trade: ProposedTrade) -> Tuple[bool, str]:
        limits = self.config.get("single_position", {})
        if trade.size_percent > limits.get("max_size_percent", 1.0):
            return False, "size_limit"
        if trade.leverage > limits.get("max_leverage", 10):
            return False, "leverage_limit"
        if trade.rr_ratio < limits.get("min_rr_ratio", 1.0):
            return False, "rr_ratio"
        return True, "ok"

    def _check_drawdown(self, portfolio: PortfolioState) -> Tuple[bool, str]:
        limits = self.config.get("drawdown_limits", {})
        breaches = []
        if portfolio.drawdown_daily > limits.get("daily", 100.0):
            breaches.append("daily")
        if portfolio.drawdown_weekly > limits.get("weekly", 100.0):
            breaches.append("weekly")
        if portfolio.drawdown_monthly > limits.get("monthly", 100.0):
            breaches.append("monthly")
        if breaches:
            return False, ",".join(breaches)
        return True, "ok"

    def _check_correlation(
        self,
        portfolio: PortfolioState,
        exposures: Mapping[str, float],
    ) -> Tuple[bool, str]:
        limits = self.config.get("portfolio", {})
        if portfolio.correlation_risk > limits.get("max_correlation_risk", 1.0):
            return False, "portfolio_correlation"
        total_same_direction = sum(value for key, value in exposures.items() if key.endswith("_same"))
        if total_same_direction > self.config.get("correlation_limits", {}).get("same_direction", 1.0):
            return False, "same_direction"
        return True, "ok"

    def _check_frequency(self, portfolio: PortfolioState) -> Tuple[bool, str]:
        limits = self.config.get("portfolio", {})
        if portfolio.open_positions >= limits.get("max_open_positions", 100):
            return False, "too_many_positions"
        if portfolio.daily_trades >= limits.get("max_daily_trades", 100):
            return False, "trade_frequency"
        if portfolio.total_risk > limits.get("max_total_risk", 1.0):
            return False, "total_risk"
        return True, "ok"

    def _check_wallet_credibility(self, trade: ProposedTrade) -> Tuple[bool, str]:
        if trade.wallet_credibility < 3.0:
            return False, "low_wallet_credibility"
        return True, "ok"


__all__ = ["PolicyEngine", "ProposedTrade", "PortfolioState"]

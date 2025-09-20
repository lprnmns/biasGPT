"""Risk policy validation logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple


@dataclass(slots=True)
class ProposedTrade:
    trading_mode: str
    asset: str
    side: str
    size_percent: float
    leverage: float
    rr_ratio: float
    wallet_credibility: float


class PolicyEngine:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def validate(self, trade: ProposedTrade) -> Tuple[bool, Dict[str, Dict[str, Any]]]:
        checks = {
            "risk_limit": self._check_risk_limit,
            "drawdown": self._check_drawdown,
            "correlation": self._pass,
            "frequency": self._pass,
            "wallet_credibility": self._check_wallet_credibility,
        }
        results: Dict[str, Dict[str, Any]] = {}
        hard_failures = {"risk_limit", "drawdown", "wallet_credibility"}
        for name, check in checks.items():
            passed, reason = check(trade)
            results[name] = {"passed": passed, "reason": reason}
            if not passed and name in hard_failures:
                return False, results
        soft_failures = [name for name, result in results.items() if not result["passed"]]
        if len(soft_failures) > 2:
            return False, results
        return True, results

    def _pass(self, trade: ProposedTrade) -> Tuple[bool, str]:
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

    def _check_drawdown(self, trade: ProposedTrade) -> Tuple[bool, str]:
        limits = self.config.get("drawdown_limits", {})
        # Placeholder logic
        return True, "ok"

    def _check_wallet_credibility(self, trade: ProposedTrade) -> Tuple[bool, str]:
        if trade.wallet_credibility < 3.0:
            return False, "low_wallet_credibility"
        return True, "ok"


__all__ = ["PolicyEngine", "ProposedTrade"]

"""Order manager orchestrating policy checks and OKX execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional

from services.api.risk.monitor import PositionSnapshot, RiskMonitor
from services.api.risk.policy import PolicyEngine, PortfolioState, ProposedTrade
from services.order_manager.killswitch import KillSwitch
from services.order_manager.okx_client import OKXClient
from services.order_manager.telemetry import TelemetryRecorder


@dataclass(slots=True)
class TradeSignal:
    trading_mode: str
    asset: str
    side: str
    size_percent: float
    leverage: float
    rr_ratio: float
    wallet_credibility: float
    quantity: float


class OrderManager:
    def __init__(
        self,
        okx_client: OKXClient,
        policy_engine: PolicyEngine,
        risk_monitor: RiskMonitor,
        kill_switch: KillSwitch,
        telemetry: Optional[TelemetryRecorder] = None,
    ) -> None:
        self.okx_client = okx_client
        self.policy_engine = policy_engine
        self.risk_monitor = risk_monitor
        self.kill_switch = kill_switch
        self.telemetry = telemetry or TelemetryRecorder()

    async def submit_order(
        self,
        signal: TradeSignal,
        portfolio: PortfolioState,
        positions: Mapping[str, PositionSnapshot],
        exposures: Mapping[str, float] | None = None,
    ) -> Dict[str, Any]:
        if self.kill_switch.is_active():
            return {"success": False, "reason": "kill_switch_active"}

        trade = ProposedTrade(
            trading_mode=signal.trading_mode,
            asset=signal.asset,
            side=signal.side,
            size_percent=signal.size_percent,
            leverage=signal.leverage,
            rr_ratio=signal.rr_ratio,
            wallet_credibility=signal.wallet_credibility,
        )
        passed, details = self.policy_engine.validate(trade, portfolio, exposures or {})
        if not passed:
            return {"success": False, "reason": "policy_rejected", "details": details}

        metrics = self.risk_monitor.get_metrics(positions.values())
        if any(level == "CRITICAL" for level, _ in metrics.alerts):
            return {"success": False, "reason": "risk_alert", "alerts": metrics.alerts}

        payload = self._build_payload(signal)
        try:
            response = await self.okx_client.create_order(payload)
            self.telemetry.record_success(payload, response)
            return {"success": True, "response": response}
        except Exception as exc:  # pragma: no cover
            self.telemetry.record_failure(payload, str(exc))
            raise

    def _build_payload(self, signal: TradeSignal) -> Dict[str, Any]:
        side = signal.side.lower()
        ord_type = "market"
        return {
            "instId": signal.asset,
            "tdMode": "cross",
            "side": side,
            "ordType": ord_type,
            "sz": str(signal.quantity),
        }


__all__ = ["OrderManager", "TradeSignal"]

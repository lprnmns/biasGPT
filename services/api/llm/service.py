"""LLM analysis service orchestrating Groq client and persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from packages.cache import TTLCache
from packages.scoring.models import WalletStats
from services.api.llm.client import GroqClient, LLMRequest
from services.api.bias.repository import BiasRepository
from services.api.monitoring.llm_budget import LLMBudgetManager


class LLMAnalysisService:
    def __init__(self, client: GroqClient | None = None, budget_manager: LLMBudgetManager | None = None) -> None:
        self.client = client or GroqClient(TTLCache())
        self.repository = BiasRepository()
        self.budget_manager = budget_manager or LLMBudgetManager(daily_limit=10.0)

    async def analyze_events(self, events: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        requests = []
        for event in events:
            cost_estimate = 0.01
            if not self.budget_manager.can_call(cost_estimate):
                continue
            requests.append(LLMRequest(prompt=self._build_prompt(event)))
            self.budget_manager.track_usage(cost_estimate)
        responses = await self.client.batch_generate(requests)
        results: List[Dict[str, Any]] = []
        for event, response in zip(events, responses):
            result = {
                "event": event,
                "analysis": response.text,
                "tokens": response.tokens_used,
                "model": response.model,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            results.append(result)
        return results

    def _build_prompt(self, event: Dict[str, Any]) -> str:
        return f"Analyze event {event.get('tx_hash', '')} with action {event.get('event_type', '')}."


__all__ = ["LLMAnalysisService"]

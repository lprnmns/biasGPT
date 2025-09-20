"""LLM analysis service orchestrating Groq client and persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from packages.cache import TTLCache
from packages.scoring.models import WalletStats
from services.api.llm.client import GroqClient, LLMRequest
from services.api.bias.repository import BiasRepository


class LLMAnalysisService:
    def __init__(self, client: GroqClient | None = None) -> None:
        self.client = client or GroqClient(TTLCache())
        self.repository = BiasRepository()

    async def analyze_events(self, events: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        requests = [LLMRequest(prompt=self._build_prompt(event)) for event in events]
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

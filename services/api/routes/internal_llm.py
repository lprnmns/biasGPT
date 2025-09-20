"""Internal LLM analysis endpoint."""

from __future__ import annotations

from typing import Any, Dict, List

try:  # pragma: no cover - FastAPI optional
    from fastapi import APIRouter, Depends, status
except ModuleNotFoundError:  # pragma: no cover
    class APIRouter:  # type: ignore
        def __init__(self, *_, **__):
            pass

        def post(self, *_args, **_kwargs):
            def decorator(func):
                return func

            return decorator

    class _Status:
        HTTP_200_OK = 200

    status = _Status()  # type: ignore

    def Depends(factory):  # type: ignore
        return factory

from services.api.llm.service import LLMAnalysisService
from services.order_manager.telemetry import TelemetryRecorder

router = APIRouter(prefix="/internal/llm", tags=["internal-llm"])

_service = LLMAnalysisService()


def get_service() -> LLMAnalysisService:
    return _service


@router.post("/analyze", status_code=status.HTTP_200_OK)
async def analyze(events: List[Dict[str, Any]], service: LLMAnalysisService = Depends(get_service)) -> Dict[str, Any]:
    results = await service.analyze_events(events)
    return {"success": True, "results": results}


__all__ = ["router"]

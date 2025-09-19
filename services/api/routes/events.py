"""Event ingestion routes."""

from __future__ import annotations

try:  # pragma: no cover - optional fastapi dependency
    from fastapi import APIRouter, Depends, HTTPException, status
except ModuleNotFoundError:  # pragma: no cover - minimal fallback for environments without FastAPI
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str) -> None:
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class _Status:
        HTTP_400_BAD_REQUEST = 400
        HTTP_202_ACCEPTED = 202

    status = _Status()  # type: ignore[assignment]

    def Depends(dependency):  # type: ignore[override]
        return dependency

    class APIRouter:  # minimal stub for testing without FastAPI
        def __init__(self, *_, **__) -> None:
            pass

        def post(self, *_args, **_kwargs):
            def decorator(func):
                return func

            return decorator

from packages.queue import QueueProducer
from services.api.dependencies import get_queue
from services.api.schemas.events import EventIngestRequest, EventIngestResponse
from workers.ingest.handler import IngestHandler

router = APIRouter(prefix="/internal/events", tags=["events"])


@router.post("/ingest", response_model=EventIngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_events(
    request: EventIngestRequest,
    queue: QueueProducer = Depends(get_queue),
) -> EventIngestResponse:
    handler = IngestHandler(queue, source=request.source or "api")
    payload = {"events": [event.to_worker_dict() for event in request.events]}
    try:
        result = await handler.handle(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return EventIngestResponse(**result)


__all__ = ["router"]

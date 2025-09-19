# FTR-02-ST2

## Summary
- Added queue dependency provider and event ingestion schemas for request/response validation.
- Implemented ingestion endpoint (with FastAPI fallback) delegating to worker normalization logic.
- Created integration tests covering successful ingestion, error handling, and schema validation.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_ingest_worker.py tests/integration/test_event_ingest_api.py`
  - Output:
    ```
    ......                                                                   [100%]
    6 passed in 0.46s
    ```

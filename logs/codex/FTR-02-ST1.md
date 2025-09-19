# FTR-02-ST1

## Summary
- Implemented ingest worker core logic with normalization, dedupe, and queue metadata (`workers/ingest/handler.py`).
- Added queue helper package with in-memory producer for tests (`packages/queue`).
- Created unit tests covering enqueue flow and dedupe behaviour (`tests/unit/test_ingest_worker.py`).

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_ingest_worker.py -q`
  - Output:
    ```
    ...                                                                      [100%]
    ```

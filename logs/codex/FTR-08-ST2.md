# FTR-08-ST2

## Summary
- Added structured logging helper and simple trace ID context utilities.
- Wrote unit tests verifying log emission and trace ID generation per request.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_logging.py tests/unit/test_tracing.py`
  - Output:
    ```
    ...                                                                      [100%]
    3 passed, 1 warning in 0.04s
    ```

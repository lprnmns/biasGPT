# FTR-08-ST1

## Summary
- Added lightweight metrics registry to expose gauges via async helper.
- Unit tests verify registry and async export behaviour.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_metrics.py`
  - Output:
    ```
    ..                                                                       [100%]
    2 passed in 0.93s
    ```

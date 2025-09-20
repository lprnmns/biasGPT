# FTR-04-ST3

## Summary
- Implemented risk monitor producing exposure and drawdown metrics with alert logic.
- Added kill switch controls with state tracking and tests covering activation/deactivation.
- Integration tests validate monitoring outputs and kill switch behavior.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/integration/test_risk_monitor.py tests/unit/test_policy_engine.py tests/unit/test_risk_config.py`
  - Output:
    ```
    .........                                                                [100%]
    9 passed in 0.24s
    ```

# FTR-04-ST1

## Summary
- Added risk configuration loader, policy engine checks, and tests; placeholder risk limits stored as JSON for loader simplicity.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_risk_config.py tests/unit/test_policy_engine.py`
  - Output:
    ```
    .....                                                                    [100%]
    5 passed in 0.27s
    ```

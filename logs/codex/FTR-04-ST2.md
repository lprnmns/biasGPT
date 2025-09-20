# FTR-04-ST2

## Summary
- Enhanced policy engine with portfolio context, correlation/frequency checks, and hard-fail handling.
- Added portfolio state dataclass and expanded unit tests.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_risk_config.py tests/unit/test_policy_engine.py`
  - Output:
    ```
    .......                                                                  [100%]
    7 passed in 0.42s
    ```

# FTR-03-ST1

## Summary
- Implemented wallet scoring engine with multi-factor model, EWMA updater, and data models (`packages/scoring`).
- Added unit tests validating scoring ranges, component behavior, and credibility updates.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_scoring_engine.py`
  - Output:
    ```
    ....                                                                     [100%]
    4 passed in 0.02s
    ```

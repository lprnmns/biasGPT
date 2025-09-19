# FTR-03-ST2

## Summary
- Added bias calculator leveraging wallet scores and credibility weighting.
- Implemented in-memory/DB-friendly bias repository and `/v1/bias` route serializer.
- Integration tests confirm bias computation and route output structure.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_scoring_engine.py tests/integration/test_bias_pipeline.py`
  - Output:
    ```
    ......                                                                   [100%]
    6 passed in 0.47s
    ```

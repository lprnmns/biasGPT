# FTR-06-ST3

## Summary
- Added LLM budget manager with alert thresholding and wired analysis service to respect budgets.
- Tests cover budget enforcement, alert triggering, and analysis output formatting.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_llm_client.py tests/unit/test_llm_budget.py tests/integration/test_llm_analysis.py`
  - Output:
    ```
    .....                                                                    [100%]
    5 passed in 0.72s
    ```

# FTR-06-ST2

## Summary
- Added LLM analysis service wrapping Groq client and exposed `/internal/llm/analyze` endpoint skeleton.
- Integration test validates mocked analyses for event batches.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_llm_client.py tests/integration/test_llm_analysis.py`
  - Output:
    ```
    ...                                                                      [100%]
    3 passed in 1.07s
    ```

# FTR-06-ST1

## Summary
- Implemented Groq LLM client with tiered model selection, caching, and batch helper.
- Added unit tests confirming caching behaviour and batch responses.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_llm_client.py`
  - Output:
    ```
    ..                                                                       [100%]
    2 passed in 1.03s
    ```

# FTR-03-ST3

## Summary
- Added TTL cache utility and LLM trigger logic with pattern detection, basic filters, and rate limiting.
- Created unit tests covering thresholding, dedupe, and cache behaviour.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_llm_triggers.py`
  - Output:
    ```
    .....                                                                    [100%]
    5 passed in 0.38s
    ```

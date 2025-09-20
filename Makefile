PYTHON = .venv/bin/python
PYTEST = .venv/bin/pytest

.PHONY: test lint fmt

test:
	$(PYTHON) -m pytest -q

lint:
	echo "No lint configured"

fmt:
	echo "No formatter configured"

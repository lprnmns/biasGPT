PYTHON ?= python
PYTEST ?= $(PYTHON) -m pytest

.PHONY: test lint fmt

test:
	$(PYTEST) -q

lint:
	echo "No lint configured"

fmt:
	echo "No formatter configured"

PY ?= .venv/Scripts/python

all:
	$(PY) -m tools.build

test:
	$(PY) -m pytest -q

.PHONY: all test

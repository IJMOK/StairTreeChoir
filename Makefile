PY ?= .venv/Scripts/python

all:
	$(PY) -m tools.build

cad:
	$(PY) -m tools.cad

test:
	$(PY) -m pytest -q

.PHONY: all cad test

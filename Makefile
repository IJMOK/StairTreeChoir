PY ?= .venv/Scripts/python

all:
	$(PY) -m tools.build

cad:
	$(PY) -m tools.cad

slice:
	$(PY) -m tools.slice

test:
	$(PY) -m pytest -q

.PHONY: all cad slice test

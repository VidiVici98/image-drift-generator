VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: help setup install test lint format preview run clean

help:
	@echo "Targets: setup install test lint format preview run clean"

setup: $(VENV)/bin/activate
	@echo "Virtualenv ready. Run 'make install' to install dependencies."

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	@touch $(VENV)/bin/activate

install: $(VENV)/bin/activate
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

test: install
	$(PYTHON) -m pytest -q

lint: install
	$(PYTHON) -m flake8 src/ --statistics

format: install
	$(PYTHON) -m black src/
	$(PYTHON) -m isort src/

preview: install
	bash run.sh --preview

run: install
	bash run.sh

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache build dist
	rm -rf output/frames/* output/final/*

VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

.PHONY: help setup install test lint format preview run clean type-check pre-commit-install pre-commit-run docker-build

help:
	@echo "Available targets:"
	@echo "  setup             - Create virtualenv"
	@echo "  install           - Install dependencies (runtime + dev)"
	@echo "  test              - Run unit tests"
	@echo "  lint              - Run flake8 linter"
	@echo "  format            - Auto-format code (black, isort)"
	@echo "  type-check        - Run mypy type checker"
	@echo "  pre-commit-install - Install pre-commit hooks"
	@echo "  pre-commit-run    - Run pre-commit checks manually"
	@echo "  preview           - Generate static preview image"
	@echo "  run               - Full pipeline (generate + encode)"
	@echo "  docker-build      - Build Docker image"
	@echo "  clean             - Remove build artifacts and caches"

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
	$(PYTHON) -m pytest -v --cov=src tests/

lint: install
	$(PYTHON) -m flake8 src/ tests/ --statistics

format: install
	$(PYTHON) -m black src/ tests/
	$(PYTHON) -m isort src/ tests/

type-check: install
	$(PYTHON) -m mypy src/ --ignore-missing-imports || true

pre-commit-install: install
	$(PYTHON) -m pre_commit install
	@echo "Pre-commit hooks installed successfully"

pre-commit-run: install
	$(PYTHON) -m pre_commit run --all-files

preview: install
	bash run.sh --preview

run: install
	bash run.sh

docker-build:
	docker build -t image-drift-generator:latest .
	@echo "Docker image built successfully"

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache build dist
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf output/frames/* output/final/*
	@echo "Clean complete"

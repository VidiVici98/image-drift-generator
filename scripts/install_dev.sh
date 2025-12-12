#!/usr/bin/env bash
set -euo pipefail

# Create venv and install runtime and dev dependencies
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
if [ -f requirements-dev.txt ]; then
  pip install -r requirements-dev.txt
fi

echo "Dev environment ready. Activate with: . .venv/bin/activate"

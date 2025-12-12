#!/usr/bin/env bash
set -euo pipefail

# run.sh
# Usage:
#   ./run.sh          -> full run: create venv, install deps, generate frames, encode webm
#   ./run.sh --preview -> only create static preview and exit

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
source "${REPO_ROOT}/config.sh"

# CLI pass-through: support --preview
PREVIEW_FLAG=""
if [[ "${1-}" == "--preview" ]]; then
  PREVIEW_FLAG="--preview"
fi

VENV_DIR="${REPO_ROOT}/.venv"
PYTHON_BIN="${VENV_DIR}/bin/python"
PIP_BIN="${VENV_DIR}/bin/pip"

echo "Repo root: ${REPO_ROOT}"
echo "Using config: ${REPO_ROOT}/config.sh"
echo "Output dir: ${OUTPUT_DIR}"

# create venv if missing
if [ ! -f "${PYTHON_BIN}" ]; then
  echo "Creating virtualenv in ${VENV_DIR}..."
  python3 -m venv "${VENV_DIR}"
fi

# upgrade pip and install requirements
echo "Ensuring pip and required packages..."
"${PIP_BIN}" install --upgrade pip >/dev/null
"${PIP_BIN}" install -r "${REPO_ROOT}/requirements.txt"

# ensure output directories exist
mkdir -p "${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}/frames"
mkdir -p "${OUTPUT_DIR}/final"

# run generate_frames.py (reads config.sh via env)
echo "Running frame generator (preview flag = ${PREVIEW_FLAG})..."
# export config variables so Python can read them via environment
# (generate_frames.py reads these env vars)
# We already sourced config.sh above, so export any simple UPPERCASE
# variable assignments found in config.sh so child processes inherit them.
VARS=$(grep -E '^[A-Z_][A-Z0-9_]*=' "${REPO_ROOT}/config.sh" | sed -E 's/=.*//' | tr '\n' ' ')
if [ -n "${VARS}" ]; then
  export ${VARS}
fi

"${PYTHON_BIN}" "${REPO_ROOT}/src/generate_frames.py" ${PREVIEW_FLAG}

# If preview requested, exit now.
if [[ "${PREVIEW_FLAG}" == "--preview" ]]; then
  echo "Preview created. Exiting."
  exit 0
fi

# encode to webm (if ffmpeg available)
echo "Running encoder..."
"${PYTHON_BIN}" "${REPO_ROOT}/src/encode_webm.py"

echo "All done. Outputs in ${OUTPUT_DIR}"

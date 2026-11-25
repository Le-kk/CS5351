#!/bin/zsh
set -eu
PROJECT_DIR="${0:A:h:h:h}"
cd "$PROJECT_DIR"
PYTHON_BIN="${CONSOLE_PYTHON:-$PROJECT_DIR/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then PYTHON_BIN="$(command -v python3)"; fi
exec "$PYTHON_BIN" -m demo.console --compact-evidence-handoff --open

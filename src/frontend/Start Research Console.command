#!/bin/zsh
set -eu
FRONTEND_DIR="${0:A:h}"
PROJECT_DIR="${FRONTEND_DIR:h:h}"
cd "$PROJECT_DIR"
PYTHON_BIN="${CONSOLE_PYTHON:-$PROJECT_DIR/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then PYTHON_BIN="$(command -v python3)"; fi
if [[ ! -f "$FRONTEND_DIR/build/index.html" ]]; then
  (cd "$FRONTEND_DIR" && npm ci --ignore-scripts && npm run build)
fi
exec "$PYTHON_BIN" -m demo.console --frontend-dir "$FRONTEND_DIR/build" --compact-evidence-handoff --open

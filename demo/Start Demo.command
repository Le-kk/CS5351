#!/bin/zsh
set -eu
demo_project="$(cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$demo_project"
if [[ -x "$demo_project/.venv/bin/python" ]]; then
  demo_python="$demo_project/.venv/bin/python"
else
  demo_python="$(command -v python3)"
fi
exec "$demo_python" -m demo --open

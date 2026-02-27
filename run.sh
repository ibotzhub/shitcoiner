#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [[ -d .venv ]]; then
  source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null || true
fi
exec python app.py "$@"

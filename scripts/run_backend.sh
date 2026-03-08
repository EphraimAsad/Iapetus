#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH=backend
uvicorn app.main:app --app-dir backend --reload

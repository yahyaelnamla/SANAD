#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Backend tests (pytest)"
python -m pytest tests/ "$@"

echo "==> Frontend tests (vitest)"
cd frontend
npm test

echo "==> All tests passed"

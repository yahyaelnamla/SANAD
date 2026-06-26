#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_FILE="${1:-.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Environment file not found: $ENV_FILE"
  echo "Copy .env.example to .env and configure production secrets."
  exit 1
fi

docker compose -p sanad-prod -f docker-compose.prod.yml --env-file "$ENV_FILE" up -d --build
echo "==> Production stack started. Verify: curl http://127.0.0.1/api/v1/health/ready"

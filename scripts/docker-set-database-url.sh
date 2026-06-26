#!/usr/bin/env bash
# Sets DATABASE_URL with URL-encoded password when POSTGRES_HOST is configured (Docker).
if [[ -n "${POSTGRES_HOST:-}" ]] && [[ -n "${POSTGRES_PASSWORD:-}" ]]; then
  ENC_PASS=$(python3 -c "import urllib.parse, os; print(urllib.parse.quote(os.environ['POSTGRES_PASSWORD'], safe=''))")
  export DATABASE_URL="postgresql+asyncpg://${POSTGRES_USER:-sanad}:${ENC_PASS}@${POSTGRES_HOST}:5432/${POSTGRES_DB:-sanad}"
fi

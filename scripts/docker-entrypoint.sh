#!/usr/bin/env bash
set -euo pipefail

source ./scripts/docker-set-database-url.sh

echo "==> Preparing alembic_version column (widen version_num if needed)"
python3 - <<'PY' || true
import asyncio
import os
import sys

url = os.environ.get("DATABASE_URL", "")
if not url:
    sys.exit(0)

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


async def main() -> None:
    engine = create_async_engine(url)
    try:
        async with engine.begin() as conn:
            exists = await conn.scalar(
                text(
                    "SELECT EXISTS ("
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_name = 'alembic_version'"
                    ")"
                )
            )
            if exists:
                await conn.execute(
                    text(
                        "ALTER TABLE alembic_version "
                        "ALTER COLUMN version_num TYPE VARCHAR(255)"
                    )
                )
                await conn.execute(
                    text(
                        "UPDATE alembic_version SET version_num = '007_financial_refusal' "
                        "WHERE version_num = '007_response_financial_and_refusal'"
                    )
                )
    finally:
        await engine.dispose()


asyncio.run(main())
PY

echo "==> Running database migrations"
alembic upgrade head || {
  echo "==> Alembic upgrade failed; runtime schema patches will run on startup"
}

echo "==> Starting SANAD backend"
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 "$@"

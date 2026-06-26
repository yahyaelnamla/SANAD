#!/usr/bin/env python3
"""Verify Alembic migration chain includes required revisions before deploy."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ROOT / "alembic" / "versions"

REQUIRED_REVISIONS = ("003_session_memory", "004_user_preferences")


def main() -> int:
    if not VERSIONS.is_dir():
        print("ERROR: alembic/versions directory not found", file=sys.stderr)
        return 1

    files = {path.stem for path in VERSIONS.glob("*.py") if path.name != "__init__.py"}
    missing = [rev for rev in REQUIRED_REVISIONS if rev not in files]
    if missing:
        print(f"ERROR: Missing migration files: {', '.join(missing)}", file=sys.stderr)
        return 1

    print("OK: Required Alembic revisions present:", ", ".join(REQUIRED_REVISIONS))
    print("Run before deploy: alembic upgrade head")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Tests for Alembic migration chain and deploy readiness."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSIONS = ROOT / "alembic" / "versions"


def _parse_revision_file(path: Path) -> tuple[str | None, str | None]:
    text = path.read_text(encoding="utf-8")
    rev_match = re.search(r'^revision:\s*str\s*=\s*"([^"]+)"', text, re.MULTILINE)
    down_match = re.search(
        r'^down_revision:.*?=\s*(?:"([^"]+)"|None)\s*$',
        text,
        re.MULTILINE,
    )
    revision = rev_match.group(1) if rev_match else None
    down_revision = down_match.group(1) if down_match and down_match.group(1) else None
    return revision, down_revision


def test_session_memory_migration_exists() -> None:
    path = VERSIONS / "003_session_memory.py"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert 'revision: str = "003_session_memory"' in text
    assert "session_id" in text
    assert "suggested_questions" in text


def test_user_preferences_migration_exists() -> None:
    path = VERSIONS / "004_user_preferences.py"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert 'revision: str = "004_user_preferences"' in text
    assert "preferences" in text
    assert 'down_revision' in text and "003_session_memory" in text


def test_migration_chain_order() -> None:
    revisions: dict[str, str | None] = {}
    for path in VERSIONS.glob("*.py"):
        if path.name == "__init__.py":
            continue
        revision, down_revision = _parse_revision_file(path)
        if revision:
            revisions[revision] = down_revision
    assert revisions.get("004_user_preferences") == "003_session_memory"
    assert revisions.get("003_session_memory") == "002_response_extras"


def test_migration_revision_ids_fit_alembic_version_column() -> None:
    """Alembic stores revision in alembic_version.version_num (widened to 255 on deploy)."""
    for path in VERSIONS.glob("*.py"):
        if path.name == "__init__.py":
            continue
        revision, _ = _parse_revision_file(path)
        if revision:
            assert len(revision) <= 255, f"{path.name}: revision id too long ({len(revision)} chars)"


def test_financial_refusal_migration_exists() -> None:
    path = VERSIONS / "007_response_financial_and_refusal.py"
    assert path.is_file()
    revision, down_revision = _parse_revision_file(path)
    assert revision == "007_financial_refusal"
    assert down_revision == "006_normalize_enum_values"
    text = path.read_text(encoding="utf-8")
    assert "alembic_version" in text
    assert "refused" in text


def test_schema_patches_include_session_and_preferences() -> None:
    text = (ROOT / "backend" / "app" / "config" / "schema_patches.py").read_text(encoding="utf-8")
    assert "SESSION_MEMORY_PATCHES" in text
    assert "USER_PREFERENCES_PATCHES" in text
    assert "session_id" in text
    assert "preferences" in text

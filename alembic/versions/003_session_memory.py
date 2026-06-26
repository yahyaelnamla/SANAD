"""Add session memory and suggested follow-up questions."""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision: str = "003_session_memory"
down_revision: Union[str, None] = "002_response_extras"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("queries", sa.Column("session_id", sa.String(length=64), nullable=True))
    op.create_index(op.f("ix_queries_session_id"), "queries", ["session_id"], unique=False)
    op.add_column(
        "responses",
        sa.Column("suggested_questions", JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
    )


def downgrade() -> None:
    op.drop_column("responses", "suggested_questions")
    op.drop_index(op.f("ix_queries_session_id"), table_name="queries")
    op.drop_column("queries", "session_id")

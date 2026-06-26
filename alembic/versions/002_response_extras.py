"""Add explainability extras to responses."""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision: str = "002_response_extras"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "responses",
        sa.Column("confidence_breakdown", JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.add_column(
        "responses",
        sa.Column("agent_trace", JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
    )
    op.add_column("responses", sa.Column("thinking_trace", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("responses", "thinking_trace")
    op.drop_column("responses", "agent_trace")
    op.drop_column("responses", "confidence_breakdown")

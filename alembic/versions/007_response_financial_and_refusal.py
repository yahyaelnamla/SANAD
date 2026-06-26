"""Add financial context, execution metrics, and refusal columns to responses."""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision: str = "007_financial_refusal"
down_revision: Union[str, None] = "006_normalize_enum_values"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Alembic stores revision ids in version_num (default VARCHAR(32)); widen first.
    op.execute("ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(255)")
    op.execute(
        "ALTER TABLE responses ADD COLUMN IF NOT EXISTS "
        "refused BOOLEAN NOT NULL DEFAULT FALSE"
    )
    op.execute("ALTER TABLE responses ADD COLUMN IF NOT EXISTS refusal_reason TEXT")
    op.execute("ALTER TABLE responses ADD COLUMN IF NOT EXISTS financial_context JSONB")
    op.execute("ALTER TABLE responses ADD COLUMN IF NOT EXISTS execution_metrics JSONB")
    op.execute(
        "ALTER TABLE responses ADD COLUMN IF NOT EXISTS "
        "madhhab_matrix JSONB NOT NULL DEFAULT '[]'::jsonb"
    )


def downgrade() -> None:
    op.drop_column("responses", "madhhab_matrix")
    op.drop_column("responses", "execution_metrics")
    op.drop_column("responses", "financial_context")
    op.drop_column("responses", "refusal_reason")
    op.drop_column("responses", "refused")

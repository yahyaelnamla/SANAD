"""Normalize enum columns that were stored with uppercase member names."""

from typing import Sequence, Union

from alembic import op

revision: str = "006_normalize_enum_values"
down_revision: Union[str, None] = "005_saas_onboarding_billing_sso"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE users SET role = LOWER(role) WHERE role <> LOWER(role)"
    )
    op.execute(
        "UPDATE users SET subscription_tier = LOWER(subscription_tier) "
        "WHERE subscription_tier <> LOWER(subscription_tier)"
    )
    op.execute(
        "UPDATE users SET subscription_status = LOWER(subscription_status) "
        "WHERE subscription_status <> LOWER(subscription_status)"
    )
    op.execute(
        "UPDATE users SET auth_provider = LOWER(auth_provider) "
        "WHERE auth_provider <> LOWER(auth_provider)"
    )
    op.execute(
        "UPDATE queries SET status = LOWER(status) WHERE status <> LOWER(status)"
    )
    op.execute(
        "UPDATE sources SET source_type = LOWER(source_type) "
        "WHERE source_type <> LOWER(source_type)"
    )


def downgrade() -> None:
    pass

"""Add SaaS onboarding, billing, and SSO columns to users."""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "005_saas_onboarding_billing_sso"
down_revision: Union[str, None] = "004_user_preferences"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "password_hash", existing_type=sa.String(length=255), nullable=True)
    op.add_column(
        "users",
        sa.Column(
            "subscription_tier",
            sa.Enum("free", "pro", "enterprise", name="subscription_tier", native_enum=False),
            nullable=False,
            server_default="free",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "subscription_status",
            sa.Enum(
                "active",
                "trialing",
                "canceled",
                "past_due",
                name="subscription_status",
                native_enum=False,
            ),
            nullable=False,
            server_default="active",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "onboarding_completed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "auth_provider",
            sa.Enum("email", "google", "microsoft", name="auth_provider", native_enum=False),
            nullable=False,
            server_default="email",
        ),
    )
    op.add_column(
        "users",
        sa.Column("sso_subject", sa.String(length=255), nullable=True),
    )
    op.execute("UPDATE users SET onboarding_completed = true")


def downgrade() -> None:
    op.drop_column("users", "sso_subject")
    op.drop_column("users", "auth_provider")
    op.drop_column("users", "onboarding_completed")
    op.drop_column("users", "subscription_status")
    op.drop_column("users", "subscription_tier")
    op.alter_column("users", "password_hash", existing_type=sa.String(length=255), nullable=False)

"""Initial SANAD schema with pgvector support."""

from typing import Sequence, Union

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("user", "admin", "reviewer", name="user_role", native_enum=False),
            nullable=False,
        ),
        sa.Column("locale", sa.String(length=5), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "sources",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column(
            "source_type",
            sa.Enum(
                "classical",
                "contemporary",
                "standard",
                "fatwa",
                name="source_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("language", sa.String(length=5), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("is_authenticated", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sources_is_authenticated"), "sources", ["is_authenticated"])
    op.create_index(op.f("ix_sources_source_type"), "sources", ["source_type"])

    op.create_table(
        "source_chunks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("metadata", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_source_chunks_source_id"), "source_chunks", ["source_id"])
    op.execute(
        "CREATE INDEX ix_source_chunks_embedding_hnsw ON source_chunks "
        "USING hnsw (embedding vector_cosine_ops)"
    )

    op.create_table(
        "queries",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=5), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "processing",
                "completed",
                "failed",
                name="query_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_queries_user_id"), "queries", ["user_id"])
    op.create_index("ix_queries_user_id_created_at", "queries", ["user_id", "created_at"])

    op.create_table(
        "responses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("query_id", sa.UUID(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("evidence", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("principles", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("opinions", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("sources", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["query_id"], ["queries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("query_id"),
    )
    op.create_index(op.f("ix_responses_query_id"), "responses", ["query_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource", sa.String(length=255), nullable=False),
        sa.Column("details", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_user_id"), table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index(op.f("ix_responses_query_id"), table_name="responses")
    op.drop_table("responses")
    op.drop_index("ix_queries_user_id_created_at", table_name="queries")
    op.drop_index(op.f("ix_queries_user_id"), table_name="queries")
    op.drop_table("queries")
    op.execute("DROP INDEX IF EXISTS ix_source_chunks_embedding_hnsw")
    op.drop_index(op.f("ix_source_chunks_source_id"), table_name="source_chunks")
    op.drop_table("source_chunks")
    op.drop_index(op.f("ix_sources_source_type"), table_name="sources")
    op.drop_index(op.f("ix_sources_is_authenticated"), table_name="sources")
    op.drop_table("sources")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

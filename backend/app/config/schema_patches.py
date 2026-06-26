"""Idempotent runtime schema patches for columns added after initial deploy."""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)

RESPONSE_COLUMN_PATCHES = (
    "ALTER TABLE responses ADD COLUMN IF NOT EXISTS "
    "confidence_breakdown JSONB NOT NULL DEFAULT '{}'::jsonb",
    "ALTER TABLE responses ADD COLUMN IF NOT EXISTS "
    "agent_trace JSONB NOT NULL DEFAULT '[]'::jsonb",
    "ALTER TABLE responses ADD COLUMN IF NOT EXISTS thinking_trace TEXT",
    "ALTER TABLE responses ADD COLUMN IF NOT EXISTS "
    "refused BOOLEAN NOT NULL DEFAULT FALSE",
    "ALTER TABLE responses ADD COLUMN IF NOT EXISTS refusal_reason TEXT",
    "ALTER TABLE responses ADD COLUMN IF NOT EXISTS "
    "financial_context JSONB",
    "ALTER TABLE responses ADD COLUMN IF NOT EXISTS "
    "execution_metrics JSONB",
    "ALTER TABLE responses ADD COLUMN IF NOT EXISTS "
    "madhhab_matrix JSONB NOT NULL DEFAULT '[]'::jsonb",
)

EMBEDDING_COLUMN_PATCHES = (
    "CREATE EXTENSION IF NOT EXISTS vector",
    "DROP INDEX IF EXISTS ix_source_chunks_embedding_hnsw",
    """
    DO $$
    DECLARE
        has_vectors BOOLEAN;
    BEGIN
        SELECT EXISTS (
            SELECT 1 FROM source_chunks WHERE embedding IS NOT NULL LIMIT 1
        ) INTO has_vectors;
        IF NOT has_vectors THEN
            ALTER TABLE source_chunks
            ALTER COLUMN embedding TYPE vector(3584)
            USING embedding::vector(3584);
            CREATE INDEX IF NOT EXISTS ix_source_chunks_embedding_hnsw
            ON source_chunks USING hnsw (embedding vector_cosine_ops);
        END IF;
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Embedding dimension patch skipped: %', SQLERRM;
    END $$;
    """,
)

QUERY_COLUMN_PATCHES = (
    "ALTER TABLE queries ADD COLUMN IF NOT EXISTS display_title VARCHAR(500)",
    "ALTER TABLE queries ADD COLUMN IF NOT EXISTS archived BOOLEAN NOT NULL DEFAULT FALSE",
    "ALTER TABLE queries ADD COLUMN IF NOT EXISTS folder VARCHAR(120)",
    "ALTER TABLE queries ADD COLUMN IF NOT EXISTS tags JSONB NOT NULL DEFAULT '[]'::jsonb",
)

USER_DOCUMENT_PATCHES = (
    """
    CREATE TABLE IF NOT EXISTS user_documents (
        id UUID PRIMARY KEY,
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        filename VARCHAR(255) NOT NULL,
        page_count INTEGER NOT NULL DEFAULT 0,
        summary TEXT NOT NULL DEFAULT '',
        search_text TEXT NOT NULL DEFAULT '',
        analysis JSONB NOT NULL DEFAULT '{}'::jsonb,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_user_documents_user_id ON user_documents(user_id)",
)

SESSION_MEMORY_PATCHES = (
    "ALTER TABLE queries ADD COLUMN IF NOT EXISTS session_id VARCHAR(64)",
    "CREATE INDEX IF NOT EXISTS ix_queries_session_id ON queries(session_id)",
    "ALTER TABLE responses ADD COLUMN IF NOT EXISTS "
    "suggested_questions JSONB NOT NULL DEFAULT '[]'::jsonb",
)

USER_PREFERENCES_PATCHES = (
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS "
    "preferences JSONB NOT NULL DEFAULT '{}'::jsonb",
)


async def apply_runtime_schema_patches(engine: AsyncEngine) -> None:
    """Ensure newer columns exist without requiring manual SQL.

    Each statement runs in its own transaction so a failing optional patch
    (e.g. embedding dimension upgrade) cannot roll back critical columns.
    """
    statements = (
        *RESPONSE_COLUMN_PATCHES,
        *QUERY_COLUMN_PATCHES,
        *USER_DOCUMENT_PATCHES,
        *SESSION_MEMORY_PATCHES,
        *USER_PREFERENCES_PATCHES,
        *EMBEDDING_COLUMN_PATCHES,
    )
    for statement in statements:
        try:
            async with engine.begin() as conn:
                await conn.execute(text(statement))
        except Exception:
            logger.warning("Schema patch skipped or failed: %s", statement[:80])
    logger.info("Runtime schema patches applied.")

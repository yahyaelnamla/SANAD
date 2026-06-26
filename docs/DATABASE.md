# SANAD — Database Schema

PostgreSQL 16 with the **pgvector** extension. ORM models live in `backend/app/models/`; migrations in `alembic/versions/` (001–007). Runtime schema patches in `backend/app/config/schema_patches.py` align embedding dimensions on startup.

## Extensions

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

## Core tables

### users

| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | User identifier |
| email | VARCHAR UNIQUE | Login email |
| password_hash | VARCHAR | Bcrypt hash (nullable for SSO-only users) |
| role | ENUM | `user`, `admin`, `reviewer` |
| locale | VARCHAR(5) | `ar` or `en` |
| preferences | JSONB | UI and reasoning preferences (migration 004) |
| subscription_tier | ENUM | `free`, `pro`, `enterprise` (migration 005) |
| subscription_status | ENUM | `active`, `trialing`, `canceled`, `past_due` |
| onboarding_completed | BOOLEAN | Onboarding wizard status |
| auth_provider | ENUM | `local`, `google`, `microsoft` |
| sso_subject | VARCHAR | External SSO subject id |
| created_at | TIMESTAMPTZ | Registration time |
| updated_at | TIMESTAMPTZ | Last update |

### sources

| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | Source identifier |
| title | VARCHAR | Source title |
| author | VARCHAR | Scholar or institution |
| source_type | ENUM | `classical`, `contemporary`, `standard`, `fatwa` |
| language | VARCHAR(5) | `ar`, `en` |
| url | TEXT | Optional external link |
| is_authenticated | BOOLEAN | Verified by reviewer/admin before RAG use |
| created_at | TIMESTAMPTZ | Ingestion time |

### source_chunks

| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | Chunk identifier |
| source_id | UUID FK → sources | Parent source |
| content | TEXT | Chunk text |
| embedding | **VECTOR(3584)** | Fanar embedding (`EMBEDDING_DIMENSION` in `source_chunk.py`) |
| chunk_index | INTEGER | Order within source |
| metadata | JSONB | Page, section, etc. |

> Migration 001 created `VECTOR(1536)`; runtime patch and `schema_patches.py` migrate to **3584** to match the Fanar embedding model.

### queries

| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | Query identifier |
| user_id | UUID FK → users | Requesting user |
| question | TEXT | Original question |
| language | VARCHAR(5) | Detected language |
| status | ENUM | `pending`, `processing`, `completed`, `failed` |
| session_id | VARCHAR(64) | Conversation thread (migration 003) |
| display_title | VARCHAR | User-visible title |
| archived | BOOLEAN | Archive flag |
| folder | VARCHAR | Optional folder label |
| tags | JSONB | User tags |
| created_at | TIMESTAMPTZ | Query time |

### responses

| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | Response identifier |
| query_id | UUID FK → queries | Parent query |
| summary | TEXT | Executive summary |
| evidence | JSONB | Evidence bundle |
| principles | JSONB | Applied fiqh principles |
| reasoning | TEXT | Step-by-step analysis |
| opinions | JSONB | Multiple scholarly opinions |
| sources | JSONB | Citation list |
| confidence | FLOAT | 0.0–1.0 confidence score |
| agent_trace | JSONB | Per-step model/latency trace (migration 002) |
| thinking_trace | JSONB | Deep reasoning thinking blocks |
| financial_context | JSONB | Market/financial data used |
| execution_metrics | JSONB | Pipeline timing summary |
| madhhab_matrix | JSONB | Madhhab comparison matrix |
| suggested_questions | JSONB | Follow-up suggestions (migration 003) |
| refused | BOOLEAN | Evidence refusal flag (migration 007) |
| refusal_reason | TEXT | Why the pipeline refused |
| created_at | TIMESTAMPTZ | Response time |

### user_documents

| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | Document identifier |
| user_id | UUID FK → users | Owner |
| filename | VARCHAR | Original filename |
| page_count | INTEGER | Extracted page count |
| summary | TEXT | Document summary |
| search_text | TEXT | Full extracted text for search |
| analysis | JSONB | Structured analysis (riba signals, etc.) |
| created_at | TIMESTAMPTZ | Upload time |

### audit_logs

| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | Log identifier |
| user_id | UUID FK → users | Actor |
| action | VARCHAR | Action type |
| resource | VARCHAR | Affected resource |
| details | JSONB | Action details |
| created_at | TIMESTAMPTZ | Timestamp |

## Indexes

- `source_chunks.embedding` — vector similarity (IVFFlat or HNSW recommended at scale)
- `queries.user_id`, `queries.created_at` — user history
- `queries.session_id` — conversation memory lookup
- `sources.source_type`, `sources.is_authenticated` — filtered RAG retrieval

## Migrations

| Revision | File | Summary |
|----------|------|---------|
| 001 | `001_initial_schema.py` | Core tables + pgvector |
| 002 | `002_response_extras.py` | Agent trace, thinking trace, metrics |
| 003 | `003_session_memory.py` | `session_id`, suggested questions |
| 004 | `004_user_preferences.py` | User preferences JSONB |
| 005 | `005_saas_onboarding_billing_sso.py` | Billing, onboarding, SSO columns |
| 006 | `006_normalize_enum_values.py` | Enum normalization |
| 007 | `007_response_financial_and_refusal.py` | Financial context, refusal fields |

## Running migrations

```bash
# With Docker Postgres running
alembic upgrade head
```

Migrations also run automatically when the backend container starts in Docker Compose.

## Test database

```bash
docker exec -it sanad-postgres psql -U sanad -c "CREATE DATABASE sanad_test;"
export TEST_DATABASE_URL=postgresql+asyncpg://sanad:password@localhost:5433/sanad_test
pytest tests/backend/test_models.py tests/backend/test_repositories.py
```

## Optional: Neo4j knowledge graph

When `NEO4J_URI` is configured, `neo4j_graph_service.py` provides an optional knowledge graph layer. PostgreSQL remains the system of record for users, queries, and RAG chunks.

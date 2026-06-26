# SANAD — API Overview

**Live specification:** `GET http://localhost:8000/api/v1/docs` (Swagger UI)

**Base path:** `/api/v1` (configurable via `API_PREFIX`)

## Authentication

Most endpoints require `Authorization: Bearer <JWT>`.

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Obtain JWT |
| GET | `/auth/me` | Current user profile |
| GET | `/auth/sso/providers` | SSO providers |
| POST | `/auth/sso/start` | Begin OAuth flow |
| POST | `/auth/sso/complete` | Complete OAuth |

## Queries (core chat)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/queries` | Submit question (returns 202 + query_id) |
| GET | `/queries` | List user queries |
| GET | `/queries/{id}` | Get result + agent trace |
| GET | `/queries/{id}/stream` | **SSE** progress + completion |
| GET | `/queries/{id}/export` | Markdown export |
| PATCH | `/queries/{id}` | Update metadata (title, archive) |
| DELETE | `/queries/{id}` | Delete query |

**POST /queries body (key fields):**

```json
{
  "question": "What is the ruling on riba?",
  "language": "ar",
  "session_id": "sess-...",
  "conversation_history": [{"role": "user", "content": "..."}],
  "fanar_model": "auto",
  "advanced_analysis": false
}
```

## Conversations

| Method | Path | Description |
|--------|------|-------------|
| GET | `/conversations` | List threads |
| GET | `/conversations/{session_id}` | Thread messages (user-scoped) |

## Tools

| Method | Path | Description |
|--------|------|-------------|
| POST | `/tools/scanner/company` | AAOIFI company screening |
| POST | `/tools/scanner/portfolio` | Portfolio screening |
| POST | `/tools/zakat/calculate` | Zakat calculator |
| POST | `/tools/documents/analyze` | PDF analysis |
| POST | `/tools/documents/query` | OCR + full chat pipeline |
| POST | `/tools/transcribe` | Fanar STT |
| POST | `/tools/tts` | Fanar TTS |
| POST | `/tools/translate` | Fanar Shaheen |

## Knowledge & sources

| Method | Path | Description |
|--------|------|-------------|
| GET | `/knowledge/sources` | Public source catalog |
| GET | `/knowledge/graph` | Neo4j graph (if configured) |
| GET/POST | `/sources` | Reviewer source management |

## Evaluation (judges)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/evaluation/dashboard` | Evaluation metrics |
| GET | `/evaluation/harness` | 5 reproducible test scenarios |

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health/live` | Liveness |
| GET | `/health/ready` | DB + Redis readiness |
| GET | `/health/metrics` | Runtime metrics |
| GET | `/version` | Build version |

## Platform API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/platform/queries` | API key | External integration |

## RAG (internal)

Backend RAG connector: `backend/app/rag/rag_connector.py` — used by ingestion services, not exposed as public REST in all deployments.

## Related

- [archive/API_SPEC.md](archive/API_SPEC.md) — historical Phase 7 spec (superseded by this doc + OpenAPI)
- [ARCHITECTURE.md](ARCHITECTURE.md) — request lifecycle

# SANAD — API Specification

> **Status**: Phase 7 admin panel implemented. Source management and dashboard stats require admin/reviewer JWT.

## Base URL

```
/api/v1
```

## Authentication

JWT Bearer token. Include in all protected requests:

```
Authorization: Bearer <access_token>
```

Obtain a token via `POST /auth/login` or `POST /auth/register` (register then login).

### Roles

| Role | Description |
|------|-------------|
| `user` | Default role; submit and view own queries |
| `reviewer` | Review access (Phase 7+) |
| `admin` | Administrative access (Phase 7+) |

## Endpoints

### Health & Meta

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Basic service health check |
| GET | `/health/live` | No | Liveness probe |
| GET | `/health/ready` | No | Readiness probe (database + Redis) |
| GET | `/health/metrics` | No | Runtime metrics (uptime, version) |
| GET | `/version` | No | API version info |

### Authentication (Phase 6) — Implemented

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Create a new user account |
| POST | `/auth/login` | No | Authenticate and receive JWT |
| GET | `/auth/me` | Yes | Get current user profile |
| GET | `/auth/admin/ping` | Admin | RBAC probe (admin/reviewer only) |

### Queries (Phase 4) — Implemented

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/queries` | Yes | Submit a Shariah reasoning query |
| GET | `/queries/{id}` | Yes | Get query status and response |
| GET | `/queries` | Yes | List user query history |

### Sources (Phase 7 — Admin) — Implemented

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/sources` | Admin/Reviewer | List sources (optional `is_authenticated`, `source_type` filters) |
| POST | `/sources` | Admin/Reviewer | Add new source |
| PUT | `/sources/{id}` | Admin/Reviewer | Update source metadata or authentication status |
| DELETE | `/sources/{id}` | Admin/Reviewer | Remove source |

### Admin Dashboard (Phase 7 — Implemented)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/admin/stats` | Admin/Reviewer | Dashboard metrics (total, authenticated, pending sources) |

## Request/Response Examples

### POST `/auth/register`

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "locale": "ar"
}
```

### POST `/auth/login`

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Token Response

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### POST `/queries`

```json
{
  "question": "هل تداول البيتكوين حلال؟",
  "language": "ar"
}
```

### Response (Explainability Chain)

```json
{
  "query_id": "uuid",
  "summary": "...",
  "evidence": [{ "text": "...", "source_id": "uuid", "citation": "..." }],
  "principles": [{ "name": "...", "description": "..." }],
  "reasoning": "...",
  "opinions": [
    { "scholar": "...", "position": "...", "rationale": "..." }
  ],
  "sources": [{ "id": "uuid", "title": "...", "url": "..." }],
  "confidence": 0.85
}
```

## Error Responses

| Status | Code | Description |
|--------|------|-------------|
| 400 | `VALIDATION_ERROR` | Invalid request body |
| 401 | `UNAUTHORIZED` | Missing or invalid token |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 422 | `NO_EVIDENCE` | No authenticated sources found |
| 500 | `INTERNAL_ERROR` | Server error |

## OpenAPI

Auto-generated via FastAPI at `/api/v1/docs` and `/api/v1/redoc`.

## Phase 7 Implementation Notes

- **Source Review**: `is_authenticated` toggle controls whether a source enters RAG retrieval (`list_authenticated`).
- **Audit Trail**: All source mutations write to `audit_logs` (create, update, delete).
- **RBAC**: Source and admin routes use `RequireReviewer` (`admin` or `reviewer` roles).
- **Frontend**: `/admin` dashboard with stats cards, source table, and review workflow UI.

## Phase 6 Implementation Notes

- **Security**: `backend/app/auth/security.py` — bcrypt password hashing, JWT encode/decode via `python-jose`.
- **RBAC**: `require_roles()` dependency factory; admin probe at `GET /auth/admin/ping`.
- **Frontend**: Login/register pages, JWT persistence via Zustand, `AuthGuard` on protected routes.
- **No Hallucination Policy**: POST `/queries` returns HTTP 422 with code `NO_EVIDENCE` when no authenticated sources are found.

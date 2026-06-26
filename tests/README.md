# SANAD/tests/

Automated test suite for the SANAD platform: unit, integration, and end-to-end coverage.

## Test Taxonomy

| Tier | Directory | Marker | Purpose |
|------|-----------|--------|---------|
| Unit | `backend/`, `agents/`, `rag/`, `frontend/` | `@pytest.mark.unit` | Isolated component logic |
| Integration | `integration/` | `@pytest.mark.integration` | Cross-layer flows (RAG, admin, explainability) |
| E2E | `e2e/` | `@pytest.mark.e2e` | Full API user/admin journeys |

## Running Tests

### All tests (recommended)

```bash
# Linux / macOS
./scripts/run_tests.sh

# Windows PowerShell
.\scripts\run_tests.ps1
```

### Backend only

```bash
pytest tests/
pytest tests/backend/          # API and service unit tests
pytest tests/integration/      # Integration tests
pytest tests/e2e/              # End-to-end API journeys
pytest -m unit                 # Unit tests only
```

Requires PostgreSQL with pgvector. Set `TEST_DATABASE_URL` or use the default from settings.

```bash
export TEST_DATABASE_URL=postgresql+asyncpg://sanad:sanad@localhost:5432/sanad_test
export FANAR_API_KEY=test-key
export JWT_SECRET=test-jwt-secret
pytest tests/ --cov=backend --cov=agents --cov=rag
```

### Frontend only

```bash
cd frontend
npm test
```

## Shariah Integrity Tests

Critical policy tests verify:

- **No Hallucination Policy** — queries without authenticated evidence return HTTP 422 `NO_EVIDENCE`
- **Explainability chain** — responses include `evidence`, `principles`, `reasoning`, and `summary` with citations
- **Source authentication** — only `is_authenticated=True` sources enter RAG retrieval

See `tests/integration/` and `tests/e2e/` for these scenarios.

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) runs:

1. Ruff lint + pytest with coverage (backend, agents, rag)
2. ESLint + Vitest (frontend)
3. Docker image build

## Shared Fixtures

`tests/conftest.py` provides:

- `db_session` — isolated PostgreSQL session with rollback
- `async_client` — httpx client wired to FastAPI + test DB
- `auth_headers` / `admin_headers` — JWT Bearer headers
- `create_test_user()` / `login_and_get_token()` — helper functions

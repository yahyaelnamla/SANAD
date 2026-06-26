# SANAD — Local Development Guide

## Prerequisites

| Tool | Version |
|------|---------|
| Docker + Compose | 24+ / v2 |
| Python | 3.11+ (local dev without Docker) |
| Node.js | 20+ |
| Fanar API key | Required — [Fanar](https://fanar.qa) |

## Quick start (Docker — recommended)

```bash
git clone <repository-url>
cd SANAD
cp .env.example .env
# Edit .env — set FANAR_API_KEY at minimum
```

**Windows (PowerShell):**

```powershell
.\scripts\start-sanad.ps1
# First build or after dependency changes:
.\scripts\start-sanad.ps1 -Rebuild
```

**Linux/macOS:**

```bash
docker compose up -d
```

| URL | Service |
|-----|---------|
| http://localhost:3000/welcome | Landing |
| http://localhost:3000/chat | Chat (login required) |
| http://localhost:3000/evaluation | Judge dashboard |
| http://localhost:8000/api/v1/docs | OpenAPI |

**Stop:**

```powershell
.\scripts\stop-sanad.ps1
```

**Health check:**

```powershell
.\scripts\verify-sanad.ps1
```

> Use **either** Docker **or** local `uvicorn` + `npm run dev` — not both on ports 3000/8000.

## Local development (without Docker)

### Backend

```bash
cp .env.example .env
# Set DATABASE_URL to local Postgres with pgvector (port 5433 in default .env)
pip install -r requirements.txt
alembic upgrade head
export PYTHONPATH=.
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local` for direct API access.

### Celery (optional)

```bash
celery -A backend.app.workers.celery_app:celery_app worker --loglevel=info
```

Requires Redis (`REDIS_URL` in `.env`).

## Running tests

### Backend

```bash
export PYTHONPATH=.
export FANAR_API_KEY=test-key
export JWT_SECRET=test-secret
export TEST_DATABASE_URL=postgresql+asyncpg://sanad:password@localhost:5433/sanad_test

pytest tests/ -q
# Or:
./scripts/run_tests.sh
```

### Frontend

```bash
cd frontend && npm test
```

### CI parity

Same jobs as `.github/workflows/ci.yml`: ruff, pytest with pgvector service, eslint, vitest, docker build.

## Debugging the agent pipeline

1. Enable trace in UI — **View Execution Trace** on any answer
2. Check backend logs for agent step completion
3. Set `LOG_LEVEL=DEBUG` in `.env`
4. Hit evaluation harness: `GET /api/v1/evaluation/harness`
5. Test Fanar connectivity: `GET /api/v1/health/ready`

## Common issues

| Symptom | Fix |
|---------|-----|
| FanarGuard 0.00 safety | Ensure `FANAR_API_KEY` valid; input guard requires non-empty moderation response |
| Chat timeout | Increase nginx stream timeout; check `MAX_POLL_ATTEMPTS` in frontend |
| Empty RAG results | Ingest authenticated sources via admin/reviewer workflow |
| Cross-user chat history | Clear browser localStorage; ensure latest frontend with `ownerUserId` scoping |

## Related

- [CONFIGURATION.md](CONFIGURATION.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)

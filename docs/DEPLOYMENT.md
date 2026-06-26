# SANAD — Deployment Guide

Production deployment for the SANAD Shariah financial reasoning platform using Docker, Nginx, Redis, and Celery.

## Architecture

```
                    ┌─────────────┐
                    │    Nginx    │ :80
                    └──────┬──────┘
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Frontend │ │ Backend  │ │  Celery  │
        │ Next.js  │ │ FastAPI  │ │  Worker  │
        └──────────┘ └────┬─────┘ └────┬─────┘
                          │            │
                    ┌─────▼─────┐ ┌────▼────┐
                    │ PostgreSQL│ │  Redis  │
                    │ +pgvector │ │         │
                    └───────────┘ └─────────┘
```

## Prerequisites

- Docker 24+ and Docker Compose v2
- Fanar API key (`FANAR_API_KEY`)
- Strong `JWT_SECRET` for production
- Strong `POSTGRES_PASSWORD`

## Local Development

```bash
# Copy environment template
cp .env.example .env

# Start all services (Postgres, Redis, backend, Celery, frontend)
docker compose up -d

# Run migrations manually (also runs on backend container start)
alembic upgrade head

# Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/v1/docs
```

## Production Deployment

### 1. Configure environment

Create a `.env` file in the project root:

```env
POSTGRES_PASSWORD=<strong-password>
JWT_SECRET=<strong-random-secret>
FANAR_API_KEY=<your-fanar-key>
CORS_ORIGINS=["https://your-domain.com"]
NEXT_PUBLIC_API_URL=
NGINX_PORT=80
```

`NEXT_PUBLIC_API_URL` left empty routes API calls through Nginx on the same origin (`/api/v1/...`).

### 2. Start production stack

```bash
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

### 3. Verify health

```bash
curl http://localhost/api/v1/health/live
curl http://localhost/api/v1/health/ready
curl http://localhost/api/v1/health/metrics
```

Readiness returns HTTP 503 until PostgreSQL and Redis are reachable.

### 4. Create admin user

Register via the UI at `/register`, then promote the user to `admin` in PostgreSQL:

```sql
UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';
```

## Monitoring Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/health` | Basic health |
| `GET /api/v1/health/live` | Liveness probe |
| `GET /api/v1/health/ready` | Readiness (DB + Redis) |
| `GET /api/v1/health/metrics` | Uptime and version |

## Celery Workers

Celery uses Redis as broker/backend. The worker runs:

- `sanad.ping` — connectivity health task
- `sanad.process_query_async` — placeholder for future async query processing

Verify worker:

```bash
docker compose exec celery-worker celery -A backend.app.workers.celery_app:celery_app inspect ping
```

## Shariah Integrity in Production

- **Fanar API key** must be set via environment — never baked into images.
- **JWT secret** must be unique per environment.
- **Source authentication** remains a human admin/reviewer gate before sources support reasoning (No Hallucination Policy).
- The explainability chain (Evidence → Principles → Reasoning → Analysis) is enforced by the multi-agent pipeline regardless of deployment environment.

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) runs lint, pytest, Vitest, and Docker build on every push to `main`/`develop`.

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Backend 503 on `/health/ready` | Wait for Postgres/Redis healthchecks; verify `DATABASE_URL` and `REDIS_URL` |
| Frontend cannot reach API | Set `NEXT_PUBLIC_API_URL` empty for same-origin Nginx routing |
| Migrations fail | Check Postgres credentials and `alembic upgrade head` logs |
| Celery not processing | Verify Redis is running and worker container is healthy |

# SANAD — Configuration Reference

Copy `.env.example` to `.env`. **Never commit `.env`.**

## Application

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `SANAD` | Display name |
| `ENVIRONMENT` | `development` | `development` / `production` |
| `DEBUG` | `true` | Debug mode |
| `LOG_LEVEL` | `INFO` | Python log level |
| `API_PREFIX` | `/api/v1` | FastAPI mount prefix |

## Database

| Variable | Description |
|----------|-------------|
| `POSTGRES_USER` | Postgres username |
| `POSTGRES_PASSWORD` | Postgres password |
| `POSTGRES_DB` | Database name |
| `DATABASE_URL` | Async SQLAlchemy URL (`postgresql+asyncpg://...`) |
| `TEST_DATABASE_URL` | Pytest database |

## Fanar AI

| Variable | Default | Description |
|----------|---------|-------------|
| `FANAR_API_KEY` | *(required)* | Fanar API bearer token |
| `FANAR_API_BASE_URL` | `https://api.fanar.qa/v1` | API base |
| `FANAR_ORGANIZATION` | `QCRI-Hackathon` | Organization header |
| `FANAR_GUARD_MIN_SAFETY` | `0.7` | Guard threshold |
| `FANAR_GUARD_MIN_CULTURAL` | `0.7` | Cultural threshold |
| `SKIP_AGENTIC_PLANNER` | `false` | Skip deep JSON planner |
| `FANAR_AGENTIC_MODEL` | `Fanar-Sadiq` | Planner/intent model override |
| `FANAR_REASONING_MODEL` | `Fanar-C-2-27B` | Deep reasoning override |
| `FANAR_VISION_MODEL` | `Fanar-Oryx-IVU-2` | Document OCR override |

## Pipeline tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_EVIDENCE_TOKENS` | `12000` | Pre-knowledge evidence trim |
| `REASONING_MAX_TOKENS_FAST` | `8000` | Fast mode generation cap |
| `REASONING_MAX_TOKENS_STANDARD` | `16000` | Standard mode cap |
| `REASONING_MAX_TOKENS_DEEP` | `32000` | Deep mode cap |
| `MAX_TURN_CHARS` | `100000` | Conversation turn storage |
| `MAX_PROMPT_HISTORY_CHARS` | `200000` | History injected into prompts |
| `ENABLE_CROSS_LANGUAGE_RETRIEVAL` | `false` | ar↔en secondary RAG |
| `SKIP_RESPONSE_SUMMARY_LLM` | `true` | Skip extra summary LLM call |
| `AGENT_SYSTEM_NAME` | `SANAD` | Planner prompt branding |
| `PLANNER_MODEL_DISPLAY_NAME` | `Fanar-Sadiq-Agentic` | Planner display name |

## Authentication

| Variable | Description |
|----------|-------------|
| `JWT_SECRET` | **Required in production** — signing key |
| `JWT_ALGORITHM` | Default `HS256` |
| `JWT_EXPIRE_MINUTES` | Token TTL |

## SSO (optional)

| Variable | Description |
|----------|-------------|
| `SSO_DEMO_MODE` | `true` — demo without OAuth credentials |
| `SSO_REDIRECT_URI` | OAuth callback URL |
| `GOOGLE_CLIENT_ID` / `SECRET` | Google OAuth |
| `MICROSOFT_CLIENT_ID` / `SECRET` | Microsoft OAuth |

## External APIs (optional)

| Variable | Service |
|----------|---------|
| `ALPHA_VANTAGE_API_KEY` | Market data |
| `MASSIVE_API_KEY` | Market data |
| `SERPER_API_KEY` | Web search |
| `TAVILY_API_KEY` | Web search |
| `LANGSEARCH_API_KEY` | Web search |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | Knowledge graph |
| `PLATFORM_API_KEY` | External platform API |

## Frontend

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Empty = same-origin `/api` via Nginx; dev: `http://localhost:8000` |
| `BACKEND_URL` | Next.js rewrite target (default `http://localhost:8000`) |
| `NGINX_PORT` | Production nginx port |

## CORS

| Variable | Example |
|----------|---------|
| `CORS_ORIGINS` | `["http://localhost:3000"]` |

## Redis / Celery

| Variable | Default |
|----------|---------|
| `REDIS_URL` | `redis://localhost:6379/0` |

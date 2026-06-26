# SANAD — System Architecture

SANAD (سند) is a **multi-agent Shariah financial reasoning platform** built on **Fanar** models. The backend orchestrates specialized agents through a **Plan → Execute → Verify** loop; the frontend is a Next.js 14 application with Arabic-first RTL support.

## Design goals

1. **Evidence-first** — refuse to answer without authenticated sources
2. **Explainability** — Evidence → Principles → Reasoning → Final Analysis
3. **Fanar-native** — Arabic fiqh reasoning, Guard moderation, STT/TTS, OCR, translation
4. **Production shape** — Docker, Nginx, PostgreSQL + pgvector, Redis, Celery, CI

## High-level topology

```
                    ┌─────────────┐
                    │   Browser   │
                    │  Next.js 14 │
                    └──────┬──────┘
                           │ HTTPS /api/v1
                    ┌──────▼──────┐
                    │    Nginx    │  (production only)
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Frontend │ │ FastAPI  │ │  Celery  │
        │ :3000    │ │ :8000    │ │  worker  │
        └──────────┘ └────┬─────┘ └────┬─────┘
                          │            │
                    ┌─────▼─────┐ ┌────▼────┐
                    │ PostgreSQL│ │  Redis  │
                    │ + pgvector│ │         │
                    └───────────┘ └─────────┘
```

## Request lifecycle (chat query)

1. **Frontend** — `POST /api/v1/queries` with question, `session_id`, optional `conversation_history`
2. **QueryService** — persists query row, runs pipeline async (or sync in tests)
3. **AgentOrchestrator.process_query**:
   - Conversation memory merge (DB session + validated history)
   - **Fanar-Guard-2** input screening (`moderate_input`)
   - **Planner** — depth-based steps or Fanar-Sadiq-Agentic JSON plan (deep mode)
   - **Execute** — intent → retrieval → knowledge → financial → reasoning
   - **Verify** — rule checks + Fanar-Guard-2 on output
   - **ResponseBuilder** — structured `FinalResponse`
4. **SSE stream** — `GET /api/v1/queries/{id}/stream` polls status + agent trace until complete
5. **Persistence** — response, evidence JSON, agent trace stored in PostgreSQL

## Orchestrator location

| Component | Path |
|-----------|------|
| Orchestrator | `backend/app/agents/agent_orchestrator.py` |
| Fanar HTTP client | `agents/common/fanar_client.py` |
| Pipeline config | `backend/app/services/pipeline_config.py` |
| Query service | `backend/app/services/query_service.py` |
| SSE streaming | `backend/app/services/query_stream.py` |

The orchestrator is **custom Python** (not LangGraph). Each agent is an async class invoked sequentially according to the execution plan.

## Pipeline depth modes

| Depth | Typical use | Reasoning model | Retrieval top-k |
|-------|-------------|-----------------|-----------------|
| `fast` | Simple fiqh facts | Fanar-Sadiq | 5 |
| `standard` | Most chat queries | Fanar-Sadiq / C-2 | 8 |
| `deep` | Madhhab comparison, advanced | Fanar-C-2-27B + thinking | 12 |

Depth is resolved in `pipeline_config.py` from user model preference (`sadiq` / `c2` / `auto`) and the advanced-analysis toggle.

## RAG architecture

| Stage | Module | Technology |
|-------|--------|------------|
| Ingestion | `rag/ingestion/` | PDF, web, structured sources |
| Chunking | `rag/chunking/` | Semantic / structural splits |
| Embeddings | `rag/embeddings/fanar_embedding_model.py` | **Fanar** embedding API |
| Storage | `rag/vectorstore/` | PostgreSQL **pgvector** |
| Retrieval | `rag/retrievers/hybrid_retriever.py` | Vector + keyword hybrid |
| Reranking | `rag/rerankers/` | Cross-encoder + diversity |
| Fanar RAG | `RetrievalPipeline._retrieve_fanar_sadiq` | **Fanar-Sadiq** grounded retrieval |

Retrieval merges **Fanar-Sadiq API results** with **local pgvector** chunks. Only sources marked `is_authenticated=True` pass the metadata filter.

## Memory architecture

| Layer | Implementation |
|-------|----------------|
| Session ID | Client-generated `sess-*`, stored on `queries.session_id` |
| Server memory | `conversation_memory_service.py` loads prior turns from DB per `(user_id, session_id)` |
| Follow-up detection | Regex + optional Fanar rewrite for contextual questions |
| Evidence reuse | Prior response evidence re-injected for “list all adilla” follow-ups |
| Client cache | Zustand + localStorage, **scoped to `ownerUserId`** (no cross-user leak) |

## Security layers

| Layer | Mechanism |
|-------|-----------|
| Authentication | JWT (`python-jose`), bcrypt passwords |
| Authorization | User-scoped queries; reviewer/admin roles |
| Input guard | Fanar-Guard-2 before pipeline |
| Output guard | Fanar-Guard-2 after reasoning + rule checks |
| Fail-closed | Guard API failure → reject (no silent pass) |
| Secrets | `.env` only; `.env.example` template without values |

## Frontend architecture

| Area | Path | Notes |
|------|------|-------|
| App Router | `frontend/src/app/` | Pages: chat, scanner, zakat, documents, evaluation |
| Features | `frontend/src/features/` | Domain UI components |
| API clients | `frontend/src/services/` | `queryService.ts` SSE + poll fallback |
| State | `frontend/src/store/` | Zustand (auth, conversation, settings) |
| i18n | `frontend/src/lib/i18n.ts` | Arabic + English |

Production builds use `output: "standalone"`. API calls use `NEXT_PUBLIC_API_URL` or same-origin `/api` via Nginx.

## External integrations (non-Fanar)

| Service | Purpose | Env keys |
|---------|---------|----------|
| Yahoo Finance / Alpha Vantage | Company & portfolio scanner | `ALPHA_VANTAGE_API_KEY`, `MASSIVE_API_KEY` |
| Serper / Tavily / LangSearch | Optional web retrieval enrichment | `SERPER_API_KEY`, etc. |
| Neo4j | Optional knowledge graph | `NEO4J_*` |
| Google / Microsoft OAuth | SSO (demo mode available) | `GOOGLE_*`, `MICROSOFT_*` |

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`):

- **backend** — ruff lint + pytest with pgvector Postgres service
- **frontend** — eslint + vitest
- **docker-build** — backend image build

## Related documents

- [AGENTS.md](AGENTS.md) — per-agent specification
- [FANAR_INTEGRATION.md](FANAR_INTEGRATION.md) — model mapping
- [DEPLOYMENT.md](DEPLOYMENT.md) — Docker production
- [archive/SYSTEM_ARCHITECTURE.md](archive/SYSTEM_ARCHITECTURE.md) — original architecture doc (archived)

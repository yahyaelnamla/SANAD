# SANAD — Repository Folder Structure

```
SANAD/
├── agents/                    # Multi-agent pipeline (Python packages)
│   ├── common/                # FanarLLMClient, evidence, state, trace
│   ├── intent_agent/
│   ├── retrieval_agent/
│   ├── knowledge_agent/
│   ├── financial_context_agent/
│   ├── reasoning_agent/
│   ├── verification_agent/
│   ├── response_builder/
│   └── voice_agent/
│
├── backend/app/               # FastAPI application
│   ├── main.py                # App factory
│   ├── api/                   # REST routers (queries, auth, tools, …)
│   ├── agents/                # AgentOrchestrator
│   ├── auth/                  # JWT, dependencies
│   ├── config/                # Settings (pydantic-settings)
│   ├── models/                # SQLAlchemy ORM
│   ├── repositories/          # Data access layer
│   ├── schemas/               # Pydantic request/response schemas
│   ├── services/              # Business logic
│   ├── workers/               # Celery app + tasks
│   ├── rag/                   # RAGConnector (backend ↔ rag/)
│   └── tools/                 # Vendored optional tools (docling, …)
│
├── rag/                       # Core RAG pipeline
│   ├── ingestion/
│   ├── chunking/
│   ├── embeddings/            # Fanar embedding client
│   ├── retrievers/
│   ├── rerankers/
│   ├── vectorstore/
│   └── pipelines/             # MainRAGPipeline, RetrievalPipeline
│
├── config/                    # Shared config (fanar_api_keys.py)
│
├── frontend/                  # Next.js 14 UI
│   └── src/
│       ├── app/               # App Router pages
│       ├── features/          # Domain components (chat, scanner, …)
│       ├── services/          # API clients
│       ├── store/             # Zustand state
│       ├── components/        # Shared UI
│       └── lib/               # Utilities, i18n
│
├── alembic/                   # Database migrations
│   └── versions/
│
├── tests/                     # pytest + vitest
│   ├── backend/
│   ├── agents/
│   ├── rag/
│   ├── integration/
│   ├── e2e/
│   └── frontend/
│
├── scripts/                   # start/stop/verify/deploy/test scripts
├── deploy/nginx/              # Production reverse proxy config
├── docs/                      # Documentation (this folder)
│   ├── archive/               # Superseded root docs + internal notes
│   └── reference/             # Fanar OpenAPI export
├── archive/                   # Non-runtime artifacts (stray files, vendored notes)
│
├── docker-compose.yml         # Development stack
├── docker-compose.prod.yml    # Production stack (+ nginx)
├── Dockerfile                 # Backend image
├── pyproject.toml             # Python project config
├── requirements.txt           # Python dependencies
└── README.md                  # Master project document
```

## Key entry points

| Purpose | Path |
|---------|------|
| FastAPI app | `backend/app/main.py` |
| Orchestrator | `backend/app/agents/agent_orchestrator.py` |
| Fanar client | `agents/common/fanar_client.py` |
| RAG pipeline | `rag/pipelines/main_rag_pipeline.py` |
| Frontend entry | `frontend/src/app/page.tsx` |
| Chat UI | `frontend/src/features/chat/` |
| Migrations | `alembic/versions/` |
| CI | `.github/workflows/ci.yml` |

## Intentional split

| Layer A | Layer B | Why |
|---------|---------|-----|
| `agents/` | `backend/app/agents/` | Pure agent logic vs FastAPI orchestration |
| `rag/` | `backend/app/rag/` | Core RAG vs backend connector/schemas |

## Large optional directories

| Path | Status |
|------|--------|
| `backend/app/tools/docling-main/` | Used by `docling_extractor.py` |
| `backend/app/tools/FlagEmbedding-master/` | Not imported — legacy vendored copy |
| `backend/app/tools/Qwen3-Embedding-main/` | Not imported — legacy vendored copy |

See [../archive/README.md](../archive/README.md).

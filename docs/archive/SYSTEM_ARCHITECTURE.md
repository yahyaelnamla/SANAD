# SANAD — System Architecture

## Overview

SANAD is an AI-powered multi-agent platform for evidence-based Shariah financial reasoning. It bridges contemporary financial instruments with classical and contemporary Islamic jurisprudence through a structured pipeline: **Evidence → Principles → Reasoning → Final Analysis**.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend API | FastAPI (Python 3.11+) |
| Frontend | Next.js 14+, Tailwind CSS, Shadcn UI |
| Database | PostgreSQL 16 + pgvector |
| Cache / Queue | Redis, Celery |
| RAG | Custom pipeline (ingestion, chunking, embeddings, vectorstore) |
| Agents | Custom Python orchestrator, Fanar models |
| Deployment | Docker, Nginx, GitHub Actions |

## High-Level Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Frontend   │────▶│  FastAPI     │────▶│  Multi-Agent    │
│  (Next.js)  │◀────│  Backend     │◀────│  Orchestrator   │
└─────────────┘     └──────┬───────┘     └────────┬────────┘
                           │                       │
                    ┌──────▼───────┐        ┌──────▼───────┐
                    │  PostgreSQL  │        │  RAG Pipeline │
                    │  + pgvector  │        │  (retrieval)  │
                    └──────────────┘        └──────────────┘
                           │
                    ┌──────▼───────┐
                    │    Redis     │
                    └──────────────┘
```

## Component Responsibilities

### Backend (`backend/app/`)
- REST API endpoints (Phase 4)
- Request validation via Pydantic schemas
- Service layer orchestrating agents and RAG
- Repository layer for database access

### RAG Pipeline (`rag/`)
- **Ingestion**: PDF, web, database, API sources
- **Chunking**: Semantic and structural text splitting
- **Embeddings**: Fanar embedding models
- **Vectorstore**: pgvector-backed similarity search
- **Retrievers & Rerankers**: Context retrieval and ranking

### Multi-Agent System (`agents/`)
1. Intent Agent — query understanding and entity extraction
2. Retrieval Agent — source search
3. Knowledge Agent — evidence collection
4. Financial Context Agent — modern finance API integration
5. Reasoning Agent — Takyeef Fiqhi (jurisprudential adaptation)
6. Verification Agent — hallucination and citation checks
7. Response Builder — structured output generation

### Frontend (`frontend/src/`)
- Arabic (RTL) and English (LTR) support
- Light/Dark mode
- Chat interface, source citations, opinion display

## Explainability Chain

Every response follows this mandatory structure:

1. **Evidence** — Retrieved sources with citations
2. **Principles** — Applicable fiqh principles (qawa'id, usul)
3. **Reasoning** — Step-by-step jurisprudential analysis
4. **Final Analysis** — Conclusion with confidence score and dissenting opinions

## Security & Integrity

- **No Hallucination Policy**: Refuse to answer without authenticated evidence
- **Mandatory Citations**: Every claim references a traceable source
- **Fanar API keys**: Loaded from `config/fanar_api_keys.py`, never hardcoded
- **RBAC**: JWT-based auth with admin/user roles (Phase 6)

## Data Flow (Query Lifecycle)

1. User submits question via frontend
2. Backend receives request, validates auth
3. Intent Agent classifies query and extracts entities
4. Retrieval Agent searches RAG vectorstore and source DB
5. Knowledge Agent assembles evidence bundle
6. Financial Context Agent enriches with market/asset data
7. Reasoning Agent performs fiqh analysis
8. Verification Agent validates citations and consistency
9. Response Builder formats final output
10. Backend returns structured JSON to frontend

## Phase Implementation Order

See `phases/README.md` for the full roadmap. Each phase must complete tests and documentation before proceeding.

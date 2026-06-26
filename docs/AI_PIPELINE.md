# SANAD — AI Pipeline

End-to-end flow from user question to evidence-backed answer. Configuration: `config/fanar_api_keys.py`. HTTP client: `agents/common/fanar_client.py`.

## Overview

```
User question
    → Fanar-Guard-2 (input)
    → Planner (depth / optional Fanar-Sadiq JSON plan)
    → Intent → Retrieval → Knowledge → Financial → Reasoning
    → Verification + Fanar-Guard-2 (output)
    → Response Builder
    → SSE trace + persisted response
```

Orchestrator: `backend/app/agents/agent_orchestrator.py`

## Agent pipeline

| Step | Agent | Primary model | Output |
|------|-------|---------------|--------|
| 1 | Intent | Fanar-Sadiq | Language, domain, entities |
| 2 | Retrieval | Fanar-Sadiq RAG + pgvector | Evidence chunks |
| 3 | Knowledge | Fanar-Sadiq | Principles + evidence bundle |
| 4 | Financial Context | External APIs | Quotes, AAOIFI ratios |
| 5 | Reasoning | Fanar-C-2-27B (deep) or Sadiq (fast) | Takyeef Fiqhi analysis |
| 6 | Verification | Rules + Fanar-Guard-2 | Citation and safety checks |
| 7 | Response Builder | Fanar-Sadiq (optional summary) | Structured `FinalResponse` |

Depth modes (`fast` / `standard` / `deep`) are resolved in `backend/app/services/pipeline_config.py`.

See [AGENTS.md](AGENTS.md) for agent-level detail.

## RAG retrieval pipeline

Module: `rag/pipelines/retrieval_pipeline.py`

| Stage | Module | Technology |
|-------|--------|------------|
| 1. Ingest | `rag/ingestion/` | PDF, web, structured sources (reviewer-authenticated only) |
| 2. Chunk | `rag/chunking/` | Semantic splits (~800 tokens, 120 overlap) |
| 3. Embed | `rag/embeddings/fanar_embedding_model.py` | Fanar `POST /v1/embeddings` → **3584-dim** vectors |
| 4. Store | `rag/vectorstore/pgvector_client.py` | PostgreSQL pgvector cosine search |
| 5. Retrieve (dual path) | Fanar-Sadiq API + `HybridRetriever` | API grounded Islamic content + local vector/keyword |
| 6. Rerank | `rag/rerankers/cross_encoder_reranker.py` | Lexical overlap + retrieval score fusion |
| 7. Diversity | `rag/rerankers/diversity_reranker.py` | Reduce redundant chunks |
| 8. Filter | `rag/retrievers/metadata_filter.py` | `authenticated_only=True` |

If no authenticated evidence remains after filtering, the pipeline **refuses** with an explicit reason.

## Memory

| Layer | Implementation |
|-------|----------------|
| Session | Client `session_id` on `POST /queries`; stored on `queries.session_id` |
| Server turns | `conversation_memory_service.py` loads prior Q&A for `(user_id, session_id)` |
| Follow-ups | Regex + optional Fanar query rewrite |
| Document context | `document_memory_service.py` injects OCR'd upload text into retrieval |
| Client cache | Zustand `conversationStore` scoped to `ownerUserId` |

Limits: `MAX_EVIDENCE_TOKENS`, `MAX_TURN_CHARS`, `MAX_PROMPT_HISTORY_CHARS` (see [CONFIGURATION.md](CONFIGURATION.md)).

## External services (non-Fanar)

| Service | Purpose | Used by |
|---------|---------|---------|
| Yahoo Finance / Alpha Vantage | Live quotes | Company/portfolio scanner, zakat prices |
| Serper / Tavily / LangSearch | Optional web enrichment | Retrieval agent (when keys set) |
| Neo4j | Optional knowledge graph | `/knowledge/graph` |
| Docling (local) | PDF text fallback | `docling_extractor.py` before Fanar-Oryx-IVU |

## Fanar model map

See [FANAR_INTEGRATION.md](FANAR_INTEGRATION.md) and [../FANAR_INSIGHTS.md](../FANAR_INSIGHTS.md).

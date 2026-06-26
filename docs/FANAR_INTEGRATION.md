# SANAD — Fanar Integration

SANAD is built **entirely on Fanar models** for AI capabilities. Configuration lives in `config/fanar_api_keys.py`; HTTP calls are centralized in `agents/common/fanar_client.py`.

**API base:** `https://api.fanar.qa/v1` (override with `FANAR_API_BASE_URL`)

## Model registry

| Config key | Default model ID | Purpose |
|------------|------------------|---------|
| `embedding` | `Fanar` | Vector embeddings for pgvector RAG |
| `generation_ar` | `Fanar-Sadiq` | Arabic generation, fast reasoning, RAG |
| `agentic` | `Fanar-Sadiq` | Intent, planner, knowledge extraction |
| `reasoning` | `Fanar-C-2-27B` | Deep Takyeef Fiqhi analysis |
| `guard` | `Fanar-Guard-2` | Safety + cultural awareness |
| `rag` | `Fanar-Sadiq` | Grounded Islamic content retrieval |
| `translation` | `Fanar-Shaheen-MT-1` | ar/en/fr/ur/tr/ms translation |
| `stt` | `Fanar-Aura-STT-1` | Speech-to-text |
| `tts` | `Fanar-Aura-TTS-2` | Text-to-speech |
| `vision` | `Fanar-Oryx-IVU-2` | PDF/image OCR & vision |

Overrides: `FANAR_AGENTIC_MODEL`, `FANAR_REASONING_MODEL`, `FANAR_VISION_MODEL`

## Where each model is used

### Fanar-Sadiq

| Feature | File(s) |
|---------|---------|
| Intent classification | `agents/intent_agent/agent.py` |
| RAG retrieval (`/chat/completions` + `islamic_content_only`) | `fanar_client.retrieve_knowledge`, `rag/pipelines/retrieval_pipeline.py` |
| Knowledge principle extraction | `agents/knowledge_agent/agent.py` |
| Fast/standard reasoning | `agents/reasoning_agent/agent.py` |
| Response formatting | `agents/response_builder/agent.py` |
| Follow-up query rewrite | `conversation_memory_service.py` |
| Suggested questions (deep) | `suggested_questions_service.py` |
| Zakat AI explanations | `zakat_ai_service.py` |
| Company/portfolio scan narrative | `company_scanner_ai.py` |

**Inputs:** chat messages, retrieval queries  
**Outputs:** text, JSON, reference objects with Quran/Hadith/fatwa excerpts  
**Limitation:** No native SSE streaming in current integration (polling UX)

### Fanar-C-2-27B

| Feature | File(s) |
|---------|---------|
| Deep reasoning | `agents/reasoning_agent/agent.py` |
| Verification thinking (deep, warnings) | `agents/verification_agent/agent.py` |

**Inputs:** evidence bundle + financial context + fiqh system prompt  
**Outputs:** JSON with `analysis`, `reasoning_steps`, `opinions`, `madhhab_matrix`  
**Why chosen:** Native Arabic fiqh terminology and Chain-of-Thought  
**Limitation:** Higher latency; uses `enable_thinking` on deep path

### Fanar-Guard-2

| Feature | File(s) |
|---------|---------|
| Input screening | `agent_orchestrator.process_query` → `moderate_input` |
| Output moderation | `verification_agent`, `output_guard_service.py` |

**Endpoint:** `POST /v1/moderations`  
**Inputs:** `prompt` + `response` (non-empty response required — input guard uses placeholder)  
**Outputs:** `safety`, `cultural_awareness` scores  
**Thresholds:** `FANAR_GUARD_MIN_SAFETY`, `FANAR_GUARD_MIN_CULTURAL` (default 0.7)  
**Behavior:** Fail-closed after 3 retries if API unavailable

### Fanar (embeddings)

| Feature | File(s) |
|---------|---------|
| Query/document embeddings | `rag/embeddings/fanar_embedding_model.py` |
| Hybrid retrieval | `rag/retrievers/hybrid_retriever.py` |

**Endpoint:** `POST /v1/embeddings`  
**Note:** Persistent HTTP client for connection pooling

### Fanar-Shaheen-MT-1

| Feature | File(s) |
|---------|---------|
| UI translation | `translation_service.py`, `/tools/translate` |
| Evidence language align (deep) | `evidence_language_service.py` |
| Cross-language RAG (optional) | `retrieval_agent/agent.py` if `ENABLE_CROSS_LANGUAGE_RETRIEVAL=true` |

### Fanar-Aura-STT-1 / TTS-2

| Feature | File(s) |
|---------|---------|
| Voice chat | `agents/voice_agent/agent.py`, `ChatInterface` |
| API | `POST /tools/transcribe`, `/tools/tts` |

### Fanar-Oryx-IVU-2

| Feature | File(s) |
|---------|---------|
| Document upload OCR | `fanar_client.extract_document_text` |
| Document query pipeline | `retrieval_agent.retrieve_from_document`, `/tools/documents/query` |

**Fallback:** Local Docling PDF extraction (`docling_extractor.py`) when Fanar vision unavailable

## Fanar client design

`FanarLLMClient` (`agents/common/fanar_client.py`):

- Shared async `httpx.AsyncClient` with lock (no connection leaks)
- Retries with exponential backoff
- `complete`, `complete_json`, `complete_with_thinking`
- `retrieve_knowledge`, `moderate`, `translate_text`, `count_tokens`
- Raises `ValueError` if `FANAR_API_KEY` missing

Orchestrator passes **one shared client** to `RetrievalAgent` → `RetrievalPipeline` → `RAGConnector`.

## Why Fanar (vs general LLMs)

| Need | Fanar advantage observed in SANAD |
|------|-----------------------------------|
| Arabic fiqh vocabulary | C-2 + Sadiq use correct *Takyeef*, *Qawa'id*, madhhab framing |
| Grounded Islamic RAG | Sadiq returns citable Quran/Hadith/fatwa excerpts |
| Cultural moderation | Guard-2 scores *cultural_awareness* — less false positives on fiqh terms |
| Arabic STT | Aura handles Islamic finance vocabulary |
| RTL document OCR | Oryx-IVU for financial PDF tables |

See [../FANAR_INSIGHTS.md](../FANAR_INSIGHTS.md) for detailed strengths and **feature requests** for future Fanar versions.

## External models (non-Fanar)

SANAD does **not** use OpenAI/Anthropic for core reasoning. External services:

| Service | Role | Why external |
|---------|------|--------------|
| Yahoo Finance / Alpha Vantage | Live stock fundamentals | Real-time market data not in Fanar |
| Serper / Tavily | Web search enrichment | Optional retrieval expansion |
| Cross-encoder reranker | Local Python reranking | Lightweight; no Fanar rerank API used |
| Docling (optional local) | PDF text extraction fallback | Offline path before Oryx |

## Recommendations for Fanar team

From production integration (see FANAR_INSIGHTS.md):

1. Native SSE streaming from Fanar-Sadiq
2. Structured fiqh JSON schema for C-2 madhhab matrices
3. Fanar-Guard batch moderation API
4. Citation-preserving Shaheen translation
5. Agentic native tool calls for market data APIs

## Reference

- OpenAPI export: `docs/reference/fanar-openapi.json` (Fanar `/v1` spec)
- Cursor integration notes: `fanar_api_cursor.md` (repo root)

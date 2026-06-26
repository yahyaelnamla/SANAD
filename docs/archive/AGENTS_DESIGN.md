# SANAD — Multi-Agent Design

## Design Principles

- **Evidence-first**: No agent may generate jurisprudential claims without retrieved evidence
- **Separation of concerns**: Each agent has a single, well-defined responsibility
- **Explainability**: Output chain is Evidence → Principles → Reasoning → Final Analysis
- **Transparency**: Multiple scholarly opinions must be presented when sources disagree

## Agent Pipeline

```
User Query
    │
    ▼
┌─────────────┐
│ Intent Agent│  Extract intent, entities, domain
└──────┬──────┘
       ▼
┌─────────────┐
│ Retrieval   │  Search RAG + source DB
│ Agent       │
└──────┬──────┘
       ▼
┌─────────────┐
│ Knowledge   │  Assemble evidence bundle
│ Agent       │
└──────┬──────┘
       ▼
┌─────────────┐
│ Financial   │  Enrich with market/asset context
│ Context     │
│ Agent       │
└──────┬──────┘
       ▼
┌─────────────┐
│ Reasoning   │  Takyeef Fiqhi analysis
│ Agent       │  (Fanar-C-2-27B for complex cases)
└──────┬──────┘
       ▼
┌─────────────┐
│ Verification│  Citation check, hallucination guard
│ Agent       │  (Fanar-Guard-2)
└──────┬──────┘
       ▼
┌─────────────┐
│ Response    │  Format final output (AR/EN)
│ Builder     │  (Fanar-Sadiq)
└─────────────┘
```

## Agent Specifications

### 1. Intent Agent (`agents/intent_agent/`)
- **Input**: Raw user query (Arabic or English)
- **Output**: `IntentResult` — intent type, entities, domain, language
- **Model**: Fanar-Sadiq-Agentic

### 2. Retrieval Agent (`agents/retrieval_agent/`)
- **Input**: IntentResult + query embedding
- **Output**: Ranked list of source chunks with metadata
- **Dependencies**: RAG vectorstore, pgvector

### 3. Knowledge Agent (`agents/knowledge_agent/`)
- **Input**: Retrieved chunks
- **Output**: Structured evidence bundle with citations
- **Rule**: Reject chunks without valid source metadata

### 4. Financial Context Agent (`agents/financial_context_agent/`)
- **Input**: Entity list (asset type, ticker, etc.)
- **Output**: Financial context (price, sector, Shariah screening data)
- **Dependencies**: External financial APIs (Phase 4+)

### 5. Reasoning Agent (`agents/reasoning_agent/`)
- **Input**: Evidence bundle + financial context
- **Output**: Jurisprudential analysis with principles cited
- **Model**: Fanar-C-2-27B for complex multi-opinion cases

### 6. Verification Agent (`agents/verification_agent/`)
- **Input**: Full draft response
- **Output**: Validated response or rejection with reasons
- **Checks**: Citation presence, source authenticity, contradiction detection
- **Model**: Fanar-Guard-2

### 7. Response Builder (`agents/response_builder/`)
- **Input**: Verified analysis
- **Output**: Structured JSON — summary, evidences, opinions, sources, confidence
- **Model**: Fanar-Sadiq (Arabic generation)

## Inter-Agent Communication

Agents communicate via typed Pydantic models defined in each agent's `models.py`. The orchestrator (LangGraph) manages state transitions and error handling.

## Error Handling

| Condition | Behavior |
|-----------|----------|
| No evidence found | Return refusal with explanation |
| Citation missing | Verification Agent blocks response |
| Conflicting sources | Present all major opinions |
| API failure | Retry with backoff; degrade gracefully |

## Fanar Model Mapping

| Agent | Model | Purpose |
|-------|-------|---------|
| Intent | Fanar-Sadiq-Agentic | Planning, entity extraction |
| Reasoning | Fanar-C-2-27B | Long-chain fiqh reasoning |
| Verification | Fanar-Guard-2 | Safety and validation |
| Response Builder | Fanar-Sadiq | Arabic/English generation |
| Embeddings | Fanar Embedding | Vector generation |

## Testing Strategy (Phase 3+)

- Unit tests per agent (`agents/*/tests.py`)
- Integration tests for full pipeline (`tests/agents/`)
- Mock Fanar API responses for deterministic tests

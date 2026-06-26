# SANAD — Multi-Agent Pipeline

SANAD implements a **Plan → Execute → Verify** agentic loop in `backend/app/agents/agent_orchestrator.py`.

## Execution plan

Default steps (deep mode):

```
intent → retrieval → knowledge → financial → reasoning → verification → response
```

Fast/standard modes may skip the agentic planner and use `plan_for_depth()` from `backend/app/services/query_depth.py`.

Set `SKIP_AGENTIC_PLANNER=true` in `.env` to disable the Fanar JSON planner on deep queries.

## Agent reference

| # | Agent | Directory | Input | Output | Fanar model |
|---|-------|-----------|-------|--------|-------------|
| 1 | **Intent** | `agents/intent_agent/` | User query + conversation | `IntentResult` (language, entities, domain) | Fanar-Sadiq |
| 2 | **Retrieval** | `agents/retrieval_agent/` | Intent | Ranked `EvidenceItem` chunks | Fanar-Sadiq RAG + local pgvector |
| 3 | **Knowledge** | `agents/knowledge_agent/` | Retrieval result | `EvidenceBundle` + fiqh principles | Fanar-Sadiq (principle extraction) |
| 4 | **Financial** | `agents/financial_context_agent/` | Intent entities | `FinancialContext` (Yahoo/Alpha Vantage) | Tooling + optional Fanar |
| 5 | **Reasoning** | `agents/reasoning_agent/` | Bundle + financial context | `ReasoningResult` (Takyeef Fiqhi) | **Fanar-C-2-27B** (deep) |
| 6 | **Verification** | `agents/verification_agent/` | Reasoning + bundle | `VerificationResult` | Fanar-Guard-2 + rules |
| 7 | **Response Builder** | `agents/response_builder/` | Verified reasoning | `FinalResponse` | Optional Fanar-Sadiq summary |
| — | **Voice** | `agents/voice_agent/` | Audio bytes | Transcript / TTS | Fanar-Aura STT/TTS |

## Plan phase

`_plan()` in the orchestrator:

- **fast/standard** — fixed step list from `query_depth.py`
- **deep** — optional Fanar-Sadiq-Agentic JSON planner (`complete_json`) returning custom `steps` and `requires_financial_context`

Planner prompt is built **at runtime** from `AGENT_SYSTEM_NAME` and `PLANNER_MODEL_DISPLAY_NAME` env vars.

## Execute phase

Private methods in `AgentOrchestrator`:

| Method | Responsibility |
|--------|----------------|
| `_run_intent` | Language detection, preferred language override (6 Fanar langs) |
| `_run_retrieval` | RAG + document memory + session evidence reuse |
| `_run_knowledge` | Token trim (`MAX_EVIDENCE_TOKENS`) then assemble bundle |
| `_run_financial` | Market data enrichment |
| `_run_reasoning` | Takyeef Fiqhi JSON analysis |

## Verify phase

`VerificationAgent.verify()`:

1. Deterministic checks — citations, empty analysis, hallucination heuristics
2. Optional **Fanar thinking** second opinion (deep mode, non-blocking warnings only)
3. **Fanar-Guard-2** moderation on full analysis text

## Trace & observability

Each step records:

- Agent name, Fanar model, phase (`plan` / `execute` / `verify` / `response`)
- Token estimates via Fanar `/tokens` endpoint
- Live SSE updates via `query_trace_cache.py`

Frontend: **View Execution Trace** on chat answers.

## Integrity rules (enforced in code)

1. **No evidence → refuse** — `RetrievalAgentResult.refused` propagates to `build_refusal_response`
2. **Mandatory citations** — verification checks grounding against bundle
3. **Guard always** — input + output moderation
4. **Authenticated sources only** — RAG metadata filter `authenticated_only=True`

## Configuration knobs

| Env var | Effect |
|---------|--------|
| `SKIP_AGENTIC_PLANNER` | Skip deep JSON planner |
| `MAX_EVIDENCE_TOKENS` | Pre-knowledge chunk trim (default 12000) |
| `REASONING_MAX_TOKENS_*` | Per-depth generation limits |
| `ENABLE_CROSS_LANGUAGE_RETRIEVAL` | Arabic↔English secondary RAG (default off) |
| `SKIP_RESPONSE_SUMMARY_LLM` | Skip extra summary LLM call (default on) |

## Related

- [FANAR_INTEGRATION.md](FANAR_INTEGRATION.md)
- [archive/AGENTS_DESIGN.md](archive/AGENTS_DESIGN.md) — original design doc (archived)

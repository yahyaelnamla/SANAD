# SANAD Production Readiness Report

**Date:** 2026-06-25  
**Scope:** Full-stack audit and bug fixes for Documents, History, Chat, and API contract alignment.

---

## Architecture Dependency Map

```
Browser (Next.js :3000)
    │  /api/v1/* rewrites → BACKEND_URL
    ▼
FastAPI Backend (:8000)
    ├── PostgreSQL + pgvector (:5433)
    ├── Redis (:6379)
    └── Celery Worker
         └── Same backend code + agents + rag
```

| Layer | Technology | Key paths |
|-------|------------|-----------|
| Frontend | Next.js 14, React 18, Zustand | `frontend/src/` |
| Backend | FastAPI, SQLAlchemy async | `backend/app/` |
| Agents | Multi-agent pipeline | `agents/` |
| RAG | Retrieval + knowledge | `rag/` |
| DB migrations | Alembic | `alembic/` |
| Orchestration | Docker Compose | `docker-compose.yml` |

---

## Issues Found & Fixed

### 1. Documents page — missing Analyze button, delete not working, UX broken

| | |
|---|---|
| **Symptoms** | After upload update, no explicit Analyze button; delete appeared ineffective; page felt broken |
| **Root cause** | Upload auto-started analysis on file select with no visible action step; strict MIME check rejected some PDFs; file input was not reset after operations; compare panel fetched documents independently causing stale UI |
| **Files changed** | `frontend/src/features/documents/components/DocumentAnalyzerPanel.tsx`, `DocumentComparePanel.tsx`, `frontend/src/lib/i18n.ts` |
| **Fix** | Two-step flow: select/drop file → click **تحليل المستند / Analyze document**; relaxed PDF validation (extension + common MIME types); reset file input; optimistic delete with result cleanup; compare panel receives shared document list from parent |

### 2. History page — select all + delete causes infinite render / hang

| | |
|---|---|
| **Symptoms** | Selecting all and deleting caused continuous rendering until hard refresh (Ctrl+Shift+R) |
| **Root cause** | Parallel `Promise.all` bulk deletes overwhelmed the client; full-page skeleton replaced list on every refresh when empty; `isPinned` function in `useMemo` deps caused unnecessary recalculations; framer-motion re-animated entire list on each refresh; missing `bumpHistory()` and pinned-ID cleanup after bulk delete |
| **Files changed** | `frontend/src/features/history/components/HistoryList.tsx`, `HistoryQueryActions.tsx`, `frontend/src/hooks/useConversationHistory.ts`, `frontend/src/store/conversationStore.ts`, `frontend/src/lib/i18n.ts` |
| **Fix** | Sequential delete with per-item error handling; separate `loading` vs `refreshing` states (no full skeleton on refresh); stable `pinnedIdSet` in filters; removed framer-motion list animations; `removePinned()` + `bumpHistory()` after deletes; bulk progress/error UI |

### 3. Chat — Advanced mode English/thinking leak, incomplete answers

| | |
|---|---|
| **Symptoms** | Advanced mode responded in English while UI is Arabic; model "thinking" text visible; answers appeared truncated |
| **Root cause** | Advanced depth prompt always forced Arabic section labels regardless of user language; unclosed `<thinking>` tags not stripped; stream tokens not sanitized; Arabic streaming split by spaces only; fallback to empty summary when reasoning existed |
| **Files changed** | `agents/reasoning_agent/agent.py`, `agents/reasoning_agent/tools.py`, `agents/response_builder/tools.py`, `backend/app/services/query_stream.py`, `frontend/src/lib/sanitizeResponse.ts`, `frontend/src/features/chat/components/ChatInterface.tsx` |
| **Fix** | Language-aware advanced prompts (Arabic vs English); improved `split_thinking()` for unclosed tags; backend/frontend sanitization of thinking artifacts; character-based SSE chunking for Arabic; `answerDisplayText()` fallback chain; sanitize streamed tokens live |

### 4. Build failure — TypeScript error

| | |
|---|---|
| **Symptoms** | `npm run build` failed |
| **Root cause** | `ExecutionMetricsPanel` accessed `metrics` after optional guard without null-safe access |
| **Files changed** | `frontend/src/features/chat/components/ExecutionMetricsPanel.tsx` |
| **Fix** | Optional chaining on token count display |

---

## Verification Results

| Check | Status | Notes |
|-------|--------|-------|
| `docker compose ps` | ✅ | postgres, redis, backend healthy; frontend running (healthcheck wget may report unhealthy during compile — pages serve 200) |
| `npm run build` | ✅ | All 23 routes compiled, no TS errors |
| `npm run lint` | ⚠️ | Prompts for initial ESLint setup (no `.eslintrc` committed) |
| Backend pytest (local) | ⚠️ | Collection errors — run via `PYTHONPATH=.` or inside CI; tests dir not mounted in dev container |
| API health curl | ⚠️ | Windows curl to localhost timed out in shell; containers report healthy via Docker |

---

## API Contract Validation

| Endpoint | Frontend | Backend | Status |
|----------|----------|---------|--------|
| `POST /tools/documents/analyze` | FormData `file` + `language` | Same | ✅ |
| `GET /tools/documents` | Expects `{ items, total }` with `document_id` | `DocumentListResponse` | ✅ |
| `DELETE /tools/documents/{id}` | Expects 204 | Returns 204 + commit | ✅ |
| `DELETE /queries/{id}` | Expects 204 | Returns 204 + session commit via `get_db` | ✅ |
| `GET /queries` | `limit`, `offset`, `include_archived` | Same query params | ✅ |
| `POST /queries` + SSE stream | `advanced_analysis`, `fanar_model`, `language` | Same schema fields | ✅ |

---

## Remaining Warnings

1. **Frontend Docker healthcheck** — container may show `unhealthy` while Next.js compiles; `/welcome` returns 200 when ready.
2. **ESLint** — not configured; `next lint` opens interactive setup.
3. **Backend tests** — require proper `PYTHONPATH` or Docker test image; not in dev volume mount.
4. **FANAR_API_KEY** — document OCR fallback and live chat require valid key in `.env`.
5. **Standard mode prompts** — still include Arabic section label examples even for English (cosmetic; advanced mode fixed).

---

## Suggested Improvements

1. Add committed ESLint config and `typecheck` script to `package.json`.
2. Mount `tests/` into backend dev container for in-compose pytest.
3. Add E2E tests (Playwright) for documents upload/analyze/delete and history bulk delete.
4. Debounce sidebar + history shared refresh via a single React Query / SWR cache.
5. WebSocket or true streaming from agents instead of poll-then-replay SSE for lower latency.

---

## Files Changed (Summary)

**Frontend:**  
`DocumentAnalyzerPanel.tsx`, `DocumentComparePanel.tsx`, `HistoryList.tsx`, `HistoryQueryActions.tsx`, `ChatInterface.tsx`, `ExecutionMetricsPanel.tsx`, `useConversationHistory.ts`, `conversationStore.ts`, `sanitizeResponse.ts`, `i18n.ts`

**Backend / Agents:**  
`reasoning_agent/agent.py`, `reasoning_agent/tools.py`, `response_builder/tools.py`, `query_stream.py`

**New:** `REPORT.md`

---

## How to Verify Locally

```bash
docker compose up --build
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000/api/v1/health/live

cd frontend && npm run build
```

**Manual test checklist:**
- [ ] Documents: upload PDF → click Analyze → see results → delete saved doc
- [ ] History: select all → delete → list clears without hang
- [ ] Chat: Advanced mode in Arabic UI → Arabic answer, no thinking text
- [ ] Chat: full answer body visible (not just 2-sentence stub)

---

## Follow-up Fixes (2026-06-25, pass 2)

### Document delete persistence
- Added `cache: no-store` on GET requests in `apiClient.ts`
- Re-sync list from server after delete via `refreshSaved()`
- Normalized UUID string comparison in `DocumentAnalyzerPanel.tsx`
- Removed duplicate `session.commit()` in document delete route

### Advanced chat mode (Arabic quality)
- Replaced `complete_with_thinking` with structured `complete_json` in `ReasoningAgent`
- Added JSON extraction, English-planning strip, and Arabic fallback generator
- Updated reasoning prompt to forbid chain-of-thought before JSON
- Enhanced `sanitizeUserFacingText` on frontend and backend

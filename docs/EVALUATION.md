# SANAD — Evaluation Guide (Hackathon Judges)

SANAD includes a built-in evaluation harness for reproducible judging.

## Judge dashboard

**URL:** http://localhost:3000/evaluation

Features:

- Interactive demo scenarios with Fanar product badges
- One-click sample queries
- Links to execution trace and evidence chain

## API harness

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/evaluation/harness
```

Returns **5 scenarios** with:

- Prompt text (Arabic and English variants)
- Expected capabilities (RAG, Guard, C-2 reasoning, etc.)
- Scoring rubric fields

## What to evaluate

### 1. Evidence integrity

- Every answer must cite authenticated sources
- Refusal when no evidence: *"No authenticated sources found"*
- Evidence panel shows source title, author, citation, score

### 2. Explainability chain

Click **View Execution Trace** on any answer:

| Step | What to verify |
|------|----------------|
| Planner | Steps match query complexity |
| Intent | Correct language detection |
| Retrieval | Fanar-Sadiq + local RAG chunks |
| Reasoning | Model = Fanar-C-2-27B on deep queries |
| Verification | Fanar-Guard-2 pass/fail |
| Response | Structured summary + reasoning |

### 3. Fanar model coverage

| Scenario | Expected model |
|----------|----------------|
| Fast fiqh question | Fanar-Sadiq |
| Deep madhhab analysis | Fanar-C-2-27B |
| Voice input | Fanar-Aura-STT-1 |
| PDF upload | Fanar-Oryx-IVU-2 |
| Translation | Fanar-Shaheen-MT-1 |
| All outputs | Fanar-Guard-2 |

### 4. Financial tools (non-agent fast path)

| Tool | Path | Fanar usage |
|------|------|-------------|
| Company scanner | `/scanner/company` | 1 short Fanar JSON call after AAOIFI rules |
| Portfolio scanner | `/scanner/portfolio` | 1 short Fanar JSON call |
| Zakat | `/tools/zakat` | Optional Fanar explanation |

These are **faster** than full chat because they skip the 7-agent pipeline.

### 5. Security

- Register user A → ask question → logout
- Register user B → **must not** see user A's chat history
- Guard rejects unsafe inputs with clear message

## Sample judge queries

| Query | Mode | Expected behavior |
|-------|------|-------------------|
| Is riba haram in Islam? | fast | Quranic evidence, Guard pass |
| Compare scholarly opinions on Bitcoin staking | deep | Madhhab matrix, C-2 reasoning |
| ما حكم تأخير الزكاة؟ | standard/deep | Arabic Chain-of-Thought |
| Is Tesla Shariah compliant? | standard | Financial context + fiqh |
| Upload PDF → ask about riba signals | document | Oryx OCR + RAG |

## Metrics per query

Available in execution trace / `execution_metrics`:

- `pipeline_depth` — fast / standard / deep
- `tokens_total` — Fanar token usage
- Per-step latency (ms)
- `fanar_model_preference` — user model selector
- Guard scores (`safety`, `cultural_awareness`)

## Reproducible test run

```bash
cp .env.example .env
# Set FANAR_API_KEY
docker compose up -d
./scripts/verify-sanad.ps1   # Windows
pytest tests/integration/ -q  # Backend integration
```

## Fanar feedback

See [../FANAR_INSIGHTS.md](../FANAR_INSIGHTS.md) for structured feature requests based on real integration experience.

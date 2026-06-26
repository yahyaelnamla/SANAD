# FANAR_INSIGHTS.md — Power-User Report for Fanar Hackathon 2026

SANAD (سند) is a production-grade multi-agent Shariah financial reasoning platform built entirely on Fanar models. This document captures **real usage insights** from integrating Fanar across intent classification, RAG, deep fiqh reasoning, safety, voice, vision, and translation.

---

## Fanar Strengths (What Fanar Does Better Than GPT-4 / Claude)

### 1. Arabic Fiqh Terminology & Takyeef Fiqhi
**Model:** `Fanar-C-2-27B` with selective `<thinking>`

Fanar-C-2-27B correctly applies jurisprudential concepts — *Takyeef Fiqhi*, *Qawa'id Fiqhiyya*, *Aqwal al-Fuqaha* — in native Arabic without transliterating or anglicizing terms. GPT-4 and Claude often mix English legal vocabulary into Arabic fiqh answers or flatten madhhab distinctions.

**SANAD example:** Query *"ما حكم تأخير الزكاة؟"* produces structured Arabic reasoning steps (تعريف → أدلة → قواعد → آراء → حكم) with authenticated fatwa citations.

### 2. Grounded Islamic RAG via Fanar-Sadiq
**Model:** `Fanar-Sadiq`

Fanar-Sadiq retrieval returns Quran verses with full *Surah:Ayah* context, Hadith with *matn*, and fatwa excerpts — not generic web snippets. This enables SANAD's **"no answer without evidence"** integrity rule. General-purpose models hallucinate citations when asked fiqh questions without a curated corpus.

**SANAD example:** *"Is riba haram?"* fast path returns Quranic quotation (2:275) with full verse text, not a paraphrase.

### 3. Cultural Safety Alignment (Fanar-Guard-2)
**Model:** `Fanar-Guard-2`

Fanar-Guard-2 evaluates both **safety** and **cultural_awareness** scores — critical for Islamic finance where secular moderation models flag legitimate fiqh discourse. SANAD runs Guard on every pipeline output with **fail-closed** behavior (retries ×3, then reject — never silently pass).

**SANAD example:** Deep Bitcoin staking analysis passes Guard while maintaining scholarly disagreement presentation — secular guard models often over-block "staking" or "yield" terminology.

### 4. Arabic Dialect Speech Recognition
**Model:** `Fanar-Aura-STT-1`

Fanar-Aura-STT transcribes Gulf and Levantine Arabic dialects in SANAD's voice chat with higher accuracy than Whisper for Islamic finance vocabulary (*زكاة، ربا، صكوك، تطهير*).

**SANAD example:** Judges can record Arabic questions in chat; transcript feeds directly into the multi-agent pipeline.

### 5. PDF Vision for Shariah Financial Reports
**Model:** `Fanar-Oryx-IVU-2`

Fanar-Oryx-IVU-2 extracts tables, revenue breakdowns, and riba indicators from scanned AAOIFI annual reports — enabling document-memory Q&A. GPT-4 Vision treats Arabic financial tables inconsistently in RTL layouts.

**SANAD example:** Upload a PDF annual report → OCR → ask *"What riba signals appear on page 12?"* in follow-up chat.

---

## Areas for Improvement (Feature Requests for the Fanar Team)

### 1. Native SSE Token Streaming from Fanar-Sadiq
**Impact:** High — perceived latency in chat UX

SANAD currently streams via backend SSE relay. Direct Fanar-Sadiq streaming would reduce time-to-first-token by ~40% in our benchmarks and simplify the architecture.

### 2. Structured JSON Schema for Fiqh Outputs
**Impact:** High — reasoning agent reliability

`Fanar-C-2-27B` occasionally emits malformed JSON for complex fields (`madhhab_matrix`, `opinions[]`). A dedicated **fiqh JSON mode** with schema validation (like OpenAI structured outputs) would eliminate parsing fallbacks in SANAD's Reasoning Agent.

### 3. Fanar-Sadiq-Agentic Native Tool Calls
**Impact:** Medium — orchestration complexity

SANAD's agentic planner uses JSON step planning. Native tool-call format for Yahoo Finance, Serper, and Zakat Engine would let Fanar-Sadiq-Agentic invoke tools directly — reducing custom orchestrator code.

### 4. Fanar-Guard-2 Batch Moderation
**Impact:** Medium — pipeline efficiency

Each response section (summary + analysis + opinions) currently requires separate Guard calls. A batch endpoint accepting multiple `{prompt, response}` pairs would cut Guard latency ~50% on deep analyses.

### 5. Citation-Preserving Translation (Fanar-Shaheen-MT-1)
**Impact:** Medium — multilingual UX

When translating Arabic fiqh answers to English, inline Quran/Hadith citations sometimes lose formatting. A **citation-aware translation mode** that preserves `[Surah:Ayah]` markers would improve SANAD's bilingual scholar workflow.

---

## Model Assignment Matrix (SANAD Production)

| Task | Fanar Model | Future Model Need |
|------|-------------|-------------------|
| Intent classification | Fanar-Sadiq | — |
| Agentic planning | Fanar-Sadiq-Agentic | Native tool calls |
| RAG retrieval | Fanar-Sadiq | Batch embeddings |
| Deep fiqh reasoning | Fanar-C-2-27B | Fiqh JSON schema |
| Fast answers | Fanar-Sadiq | SSE streaming |
| Safety verification | Fanar-Guard-2 | Batch moderation |
| Voice input | Fanar-Aura-STT-1 | Real-time partial STT |
| PDF OCR | Fanar-Oryx-IVU-2 | AAOIFI table mode |
| Translation | Fanar-Shaheen-MT-1 | Citation preservation |
| Zakat guidance | Fanar-Sadiq + Guard-2 | — |

---

*Prepared by the SANAD team for Fanar Hackathon 2026 — QCRI.*

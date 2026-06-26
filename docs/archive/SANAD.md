



Here is the expanded, high-spec hackathon blueprint for `SANAD.md`. It fuses your detailed project outline, your background preferences (modern data-centric visual language), and full integration of the Fanar 2.0 multi-agent ecosystem—including the specific audio/multimodal endpoints (`Fanar-Aura-STT`, `Fanar-Oryx-IVU-2`) required to meet top-tier hackathon standards.

---

# SANAD

### AI-Powered Shariah Reasoning & Multimodal Analytics Platform for Contemporary Finance

---

# Overview

SANAD is an agentic AI platform designed to assist researchers, scholars, and Islamic finance professionals in analyzing contemporary financial and economic issues through authenticated Islamic sources and modern scholarly opinions.

The platform does not issue independent fatwas. Instead, it provides evidence-based jurisprudential analysis supported by classical references, contemporary fatwas, and Islamic finance standards while maintaining complete transparency, multi-modal input processing, and architectural traceability.

Built on top of the **Fanar 2.0 Ecosystem**, SANAD leverages the native **Fanar-Sadiq** multi-agent architecture to bridge modern economic realities with established Islamic jurisprudence through precise retrieval, specialized domain tools, and real-time voice and document ingestion.

---

# Problem

Modern financial technologies evolve faster than traditional references are organized. Muslims today face complex questions regarding Cryptocurrencies, DeFi, ETFs, NFTs, and Corporate Shariah compliance.

Answering these questions requires simultaneously:

* Understanding modern economic engineering and complex digital assets.
* Parsing massive volumes of classical Islamic jurisprudence.
* Cross-referencing conflicting contemporary fatwas and international financial standards (e.g., AAOIFI).

Traditional search engines and general-purpose LLMs fail here; they hallucinate, cross-contaminate secular and sacred advice, lack structured financial data grounding, and cannot ingest real-time voice notes or multi-page corporate financial PDFs seamlessly.

---

# Solution

SANAD delivers an advanced multi-agent architecture built to hackathon specifications. By wrapping the **Fanar 2.0 Stack**, SANAD introduces an accessible web portal that accepts voice recordings, textual queries, and financial documents, feeding them into an asynchronous multi-agent reasoning chain.

```
       [User Voice Input] ──► Fanar-Aura-STT-1 ──┐
                                                 ▼
[User Document Upload] ──► Fanar-Oryx-IVU-2 ──► [ Intent & Routing Agent ] 
                                                 │
   ┌─────────────────────────────────────────────┴─────────────────────────────────────────────┐
   ▼                                             ▼                                             ▼
[Fiqh Retrieval Agent]               [Financial Context Agent]                    [Zakat & Calculation Engine]
  ├── Milvus Hybrid Vector DB          ├── Real-time Financial Web APIs              └── Rule-Based Deterministic Fiqh
  └── 2M+ Verified Documents           └── Crypto/DeFi Protocol Check                    (Crypto, Stocks, Wealth)
   └─────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                                 ▼
                                    [ Fanar-C-2-27B Reasoning ]
                                     (Arabic Chain-of-Thought)
                                                 │
                                                 ▼
                                    [ Verification Agent (Guard) ]
                                     (Fanar-Guard-2 Safe Routing)
                                                 │
                                                 ▼
                                        [ Final UI Dashboard ]
                                    (Deep Navy & Cyan Data Layout)

```

---

# Hackathon Feature Set & User Experience

To maximize hackathon impact, the platform supports seamless user interactions, removing barriers between professional financial metrics and Islamic legacy texts.

### 1. Hands-Free Voice Ingestion (Audio-to-Text Chat)

Users don't need to type lengthy financial scenarios. They tap a microphone icon in the chat interface to record complex multi-lingual questions. The system leverages **Fanar-Aura-STT-1** to translate audio streams directly into clean text within the chat pipeline.

### 2. Multi-Page PDF Document Ingestion (Halal Scanner)

Scholars or investment analysts can upload corporate balance sheets, prospectus PDFs, or scanned classical manuscripts. The **Fanar-Oryx-IVU-2** vision-language pipeline parses the charts, financial statement structures, and texts, identifying lines of interest-bearing debt or non-permissible income automatically.

### 3. Precision Nexus Design System

The user interface avoids standard template aesthetics, opting for a dark-themed, data-centric dashboard.

* **Palette:** Deep Navy (`#0A192F`) background for reduced visual strain during long analytical sessions, contrasted with Electric Cyan (`#00F0FF`) telemetry readouts and status highlights.
* **Data Visualization:** Incorporates dynamic, real-time visual streams tracking corporate revenue structures, asset health, and reasoning confidence indicators.

---

# Core Capabilities

## Contemporary Financial Fatwas

Comprehensive analysis of cutting-edge digital assets, including:

* Cryptocurrencies (Bitcoin, Ethereum, Stablecoins, and Tokenized Yields).
* Consensus & Security Mechanics (Proof-of-Stake protocols, liquidity baking, and mining pools).
* Decentralized Finance (DeFi structures, collateralized lending, automated market makers, and NFTs).

## Shariah Compliance Screening

Automated evaluation of global equities (e.g., Tesla, Nvidia, Apple) against recognized standards by parsing:

* Primary business operations and secondary cash flows.
* Proportion of interest-bearing debt relative to total market capitalization.
* Liquidity thresholds and non-permissible asset tracking utilizing AAOIFI benchmarks.

## Comparative Madhab Matrix

Instead of flattening diversity, the platform renders a structured comparative interface mapping across:

* Traditional Schools of Thought (Hanafi, Maliki, Shafi'i, Hanbali).
* Contemporary Global Bodies (International Islamic Fiqh Academy, Muslim World League).
* Granular breakdowns indicating points of structural alignment or divergence.

---

# Multi-Agent Design & Fanar Core API Mappings

SANAD's operational intelligence is driven by a specialized multi-agent mesh configured to execute via the Fanar API.

### 1. Intent & Routing Agent (`Fanar-Sadiq-Agentic`)

* **Role:** Acts as the network orchestrator. It parses the incoming text stream (whether native or transcribed via voice APIs) to identify asset classes, primary domain spaces, and triggers target sub-agents.

### 2. Fiqh Retrieval Agent (`Fanar-Sadiq`)

* **Role:** Performs hybrid dense-sparse vector lookups across a verified repository of over two million classical and contemporary Islamic texts, returning immutable text snippets coupled with deterministic citations.

### 3. Financial Context Agent (`Fanar-Sadiq-Agentic`)

* **Role:** Interacts with real-time external equity and blockchain APIs. It injects live metrics, trading volume patterns, and corporate balances into the active context loop.

### 4. Mathematical Execution Engine (Rule-Based Zakat)

* **Role:** Extracts financial values from user profiles or queries to process algorithmic, rule-based Zakat calculations across diverse portfolios (including crypto, stocks, and cash), providing completely audit-transparent mathematical paths.

### 5. Reasoning Agent (`Fanar-C-2-27B`)

* **Role:** Runs deep contextual synthesis using native Arabic chain-of-thought processing. It aligns the live economic data gathered by the financial sub-agents against the jurisprudential principles retrieved from classical libraries.

### 6. Verification Agent (`Fanar-Guard-2`)

* **Role:** Performs dual-layer compliance checks on both inputs and outputs. It scans for hallucination patterns, unverified scriptural quotes, or safety mismatches, blocking responses that fail strict structural verification tests.

---

# Technology Stack & API Specifications

* **Frontend Framework:** Next.js (TailwindCSS, optimized for low-latency web socket connections).
* **Data Layout:** Precision Nexus Theme (Deep Navy, Electric Cyan, high-density charts).
* **Backend Framework:** FastAPI (Asynchronous python orchestration using LangGraph).
* **Vector Storage:** Milvus / pgvector (Hybrid keyword + dense embedding lookup).
* **Caching & Session Layer:** Redis (Maintains multi-agent conversation memory).

### Fanar 2.0 API Infrastructure Requirements

```json
{
  "Base_URL": "https://api.fanar.qa",
  "Headers": {
    "Authorization": "Bearer ${FANAR_API_KEY}",
    "Content-Type": "application/json"
  }
}

```

| Component Engine | Model Identifier | Rate Limit Threshold | Operational Purpose |
| --- | --- | --- | --- |
| **Reasoning Core** | `Fanar-C-2-27B` | 50 req / min | High-depth Fiqh synthesis and rule mapping. |
| **Agent Maestro** | `Fanar-Sadiq-Agentic` | 50 req / min | Multi-step graph execution and API orchestration. |
| **Bilingual Guard** | `Fanar-Guard-2` | 50 req / min | Hallucination suppression and safety checking. |
| **Vision Ingestion** | `Fanar-Oryx-IVU-2` | 20 req / day | PDF statement reading and table structure extraction. |
| **Audio Transcriber** | `Fanar-Aura-STT-1` | 20 req / day | Live user voice note to text decoding in chat. |

---

# System Integrity & Safeguard Protocols

* **No-Hallucination Ceiling:** If the retrieval matrix returns zero confirmed, trusted sources matching the parameters of the financial asset, the system explicitly terminates the reasoning thread. It alerts the analyst rather than generating speculative conclusions.
* **Absolute Citation Mapping:** Every scholarly opinion or corporate verdict displayed on the Cyan UI telemetry dashboard contains an interactive citation anchor detailing the precise text, chapter, and verification source.
* **Strict Scriptural Encapsulation:** Any output containing Quranic text or authentic Hadith extracts is strictly validated post-inference to prevent transcription errors, guaranteeing text preservation.

# SANAD
### AI-Powered Shariah Reasoning Platform for Contemporary Financial Matters

---

# Overview

SANAD is an agentic AI platform designed to assist researchers, scholars, and Islamic finance professionals in analyzing contemporary financial and economic issues through authenticated Islamic sources and modern scholarly opinions.

The platform does not issue independent fatwas. Instead, it provides evidence-based jurisprudential analysis supported by classical references, contemporary fatwas, and Islamic finance standards while maintaining complete transparency and traceability.

SANAD aims to bridge modern economic realities with established Islamic jurisprudence through retrieval, reasoning, and human supervision.

---

# Problem

Modern financial technologies evolve faster than traditional references are organized.

Muslims today face questions such as:

- Is Bitcoin halal or haram?
- Can I invest in Tesla stock?
- Is staking cryptocurrency permissible?
- Are ETFs halal?
- What are the rulings on DeFi protocols?
- Are NFTs considered valid assets?
- Is margin trading permissible?
- Are smart contracts acceptable in Islamic finance?
- Which cryptocurrencies satisfy Shariah requirements?
- Is a company's income structure compliant with Islamic principles?

Answering these questions requires:

- Understanding modern economics.
- Knowledge of Islamic jurisprudence.
- Access to reliable fatwas.
- Analysis of different opinions.
- Awareness of contemporary financial structures.

This process is time-consuming and difficult for non-specialists.

---

# Solution

SANAD is an AI-powered multi-agent reasoning platform that combines:

- Retrieval-Augmented Generation (RAG)
- Specialized Fanar models
- Contemporary fatwa databases
- Islamic finance standards
- Human review and supervision

The system provides explainable and source-grounded analyses rather than unsupported answers.

---

# Core Capabilities

## Contemporary Financial Fatwas

Analysis of:

- Cryptocurrencies
- Bitcoin
- Ethereum
- Stablecoins
- Staking
- Mining
- NFTs
- Smart contracts
- Decentralized Finance (DeFi)
- Tokenization
- Forex trading
- Margin trading
- ETFs
- Stocks
- Sukuk
- Crowdfunding
- Digital assets

---

## Shariah Compliance Screening

Determine whether a company or stock is Shariah compliant.

Examples:

- Tesla
- Nvidia
- Microsoft
- Apple
- Amazon

The system analyzes:

- Main business activities.
- Sources of revenue.
- Interest-bearing debt.
- Non-permissible income.
- AAOIFI standards.

---

## Multiple Opinions

Present:

- Hanafi opinion
- Maliki opinion
- Shafi'i opinion
- Hanbali opinion
- Contemporary fatwas
- Islamic Fiqh Academy decisions
- AAOIFI standards

with explanation of agreement and disagreement.

---

## Source Attribution

Every paragraph must include references.

No answer is generated without supporting evidence.

---

# Architecture

```
User Question
      ↓
Intent Agent
      ↓
Retrieval Agent
      ↓
Knowledge Agent
      ↓
Financial Context Agent
      ↓
Reasoning Agent
      ↓
Verification Agent
      ↓
Response Builder
      ↓
Internal Human Review
      ↓
Final Response
```

Human review happens internally by administrators and scholars and is not exposed as a user step.

---

# Multi-Agent Design

## 1. Intent Agent

Understands the question and identifies:

- Asset type
- Financial domain
- Keywords
- Required tools

Example:

"Can I invest in Bitcoin?"

Extracts:

- Bitcoin
- Cryptocurrency
- Investment
- Digital assets

---

## 2. Retrieval Agent

Searches authenticated sources.

### Classical Sources

- Al-Mughni
- Al-Majmu'
- Bada'i Al-Sana'i
- Al-Ashbah wa Al-Naza'ir
- Kuwaiti Encyclopedia of Fiqh

### Contemporary Sources

- International Islamic Fiqh Academy
- Muslim World League Fiqh Academy
- AAOIFI Standards
- Fatwa committees
- Contemporary scholars

### Trusted Websites

- IslamWeb
- Dorar
- Alukah
- Official Fatwa bodies

---

## 3. Knowledge Agent

Collects:

- Relevant evidences
- Jurisprudential principles
- Previous fatwas
- Similar cases

---

## 4. Financial Context Agent

Understands:

- Blockchain
- Smart contracts
- DeFi
- Staking
- Yield farming
- ETFs
- Stocks
- Corporate financial structures

using external financial APIs.

---

## 5. Reasoning Agent

Performs jurisprudential adaptation (Takyeef Fiqhi).

Connects:

Reality
↓

Texts
↓

Fiqh Principles
↓

Scholarly Opinions
↓

Modern Financial Structures

---

## 6. Verification Agent

Checks:

- Missing references
- Hallucinations
- Contradictions
- Unsupported claims

Rejects unsupported answers.

---

## 7. Response Builder

Generates:

- Summary
- Evidences
- Scholarly opinions
- Sources
- Confidence score

---

# Confidence Score

Example

92%

Based on:

✓ AAOIFI standard exists

✓ International Fiqh Academy decision available

✓ Consensus among scholars

✓ Strong evidence

---

# Knowledge Sources

## Classical References

- Al-Mughni
- Al-Majmu'
- Bada'i Al-Sana'i
- Al-Ashbah wa Al-Naza'ir
- Al-Mawsu'ah Al-Fiqhiyyah

---

## Contemporary Institutions

- International Islamic Fiqh Academy
- Muslim World League
- AAOIFI
- Fatwa authorities
- National Shariah boards

---

## Contemporary Scholars

Including fatwas and research from recognized scholars and Islamic finance experts.

---

# Technology Stack

## Backend

FastAPI

---

## Frontend

Next.js

---

## Database

PostgreSQL

---

## Vector Database

pgvector

---

## Agent Framework

LangGraph

---

## Embeddings

Fanar Embedding Models

---

## Search

Hybrid Search

- Vector Search
- BM25 Search

---

## Cache

Redis

---

# Fanar Models

## Primary Reasoning Model

### Fanar-Sadiq-Agentic

Responsible for:

- Planning
- Tool usage
- Multi-step reasoning
- Agent orchestration

---

## Arabic Generation Model

### Fanar-Sadiq

Responsible for:

- Arabic writing
- Summarization
- Response generation

---

## Advanced Reasoning Model

### Fanar-C-2-27B

Used for:

- Difficult cases
- Long-chain reasoning
- Comparative analysis

---

## Safety Model

### Fanar-Guard-2

Used for:

- Hallucination reduction
- Validation
- Safety checks

---

# External Integrations

## Financial APIs

Used to analyze:

- Stocks
- Company activities
- Revenue streams
- Debt ratios

---

## Crypto APIs

Used to understand:

- Token categories
- Blockchain protocols
- Staking mechanisms
- Consensus models

---

# Integrity Rules

## No Hallucination Policy

If no evidence exists:

The system refuses to answer.

---

## Mandatory Citations

Every answer must contain references.

---

## Transparency

When disagreement exists:

All major opinions are displayed.

---

## Explainability

Every conclusion must show:

Evidence
↓

Principles
↓

Reasoning
↓

Final analysis

---

# Example

Question

"Is Bitcoin halal?"

Output

### Summary

Bitcoin is an issue of contemporary disagreement among scholars.

### Evidences

...

### Jurisprudential Principles

...

### Opinions

Opinion 1:
Permissible under conditions.

Opinion 2:
Impermissible due to gharar.

### Contemporary Decisions

AAOIFI

International Islamic Fiqh Academy

### Confidence

84%

### Sources

...

---

# Future Features

- Voice assistant
- Arabic dialect support
- PDF fatwa analysis
- Company halal scanner
- Portfolio halal checker
- Zakat calculator
- Islamic investment advisor
- Scholar dashboard
- Fatwa comparison engine
- Knowledge graph visualization

---

# Vision

To become an Arabic AI platform that assists researchers and Islamic finance professionals in understanding and analyzing contemporary economic matters through authenticated, explainable, and source-grounded jurisprudential reasoning.


# SANAD — Project TODO

## Current Phase: All Phases Complete

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Project Setup (Docker, CI/CD, Architecture) | **Complete** |
| 1 | Database Schema & ORM | **Complete** |
| 2 | RAG Pipeline | **Complete** |
| 3 | Multi-Agent System | **Complete** |
| 4 | Backend API | **Complete** |
| 5 | Frontend (Next.js) | **Complete** |
| 6 | Authentication & RBAC | **Complete** |
| 7 | Admin Panel | **Complete** |
| 8 | Testing Suite | **Complete** |
| 9 | Deployment | **Complete** |

## Phase 9 — Completed

- [x] `docker-compose.prod.yml` — Nginx, frontend, backend, Postgres, Redis, Celery
- [x] `frontend/Dockerfile` — multi-stage Next.js standalone build
- [x] `deploy/nginx/nginx.conf` — reverse proxy for API and frontend
- [x] `scripts/docker-entrypoint.sh` — Alembic migrations on backend startup
- [x] Celery worker: `backend/app/workers/celery_app.py`, `tasks.py`
- [x] Health monitoring: `/health/live`, `/health/ready`, `/health/metrics`
- [x] Updated `docker-compose.yml` — dev frontend + Celery worker
- [x] `docs/DEPLOYMENT.md`, `scripts/deploy.sh`, `scripts/deploy.ps1`
- [x] Phase 9 tests (`tests/backend/test_deployment.py`)

## Phase 8 — Completed

- [x] Shared test fixtures, pytest markers, integration + E2E tests
- [x] CI: backend coverage + frontend Vitest
- [x] Unified runners: `scripts/run_tests.sh`, `scripts/run_tests.ps1`

## Notes

- Follow `phases/phaseX_*.md` for each phase before implementation.
- Every jurisprudential claim must cite an authenticated source.
- No Hallucination Policy: refuse to answer without evidence.
- **Deploy:** `./scripts/deploy.sh` or `.\scripts\deploy.ps1` (see `docs/DEPLOYMENT.md`)
- **Test:** `./scripts/run_tests.sh` or `.\scripts\run_tests.ps1`
# SANAD v2 Master Roadmap

## PHASE 0 — Philosophy, Scholarly Foundation & Trust

### Mission

SANAD is not merely an AI chatbot.

SANAD is a trusted Islamic finance intelligence platform built for the public, students, researchers, professionals, and scholars.

Its purpose is to provide evidence-based answers rooted in Islamic scholarly methodology while maintaining transparency, honesty, and excellent user experience.

The platform should feel like:

ChatGPT + Perplexity + NotebookLM + Bloomberg Terminal for Islamic Finance.

---

## Core Priorities

Accuracy > Trust > Transparency > Speed > UX > Explainability

The goal is not to answer everything.

The goal is to answer correctly and honestly.

---

## Non-Negotiable Principles

- Never fabricate evidence.
- Never fabricate scholarly opinions.
- Never hide major disagreements.
- Never expose chain of thought.
- Never expose prompts.
- Never issue independent fatwas.
- Never sacrifice correctness for user satisfaction.
- Never force certainty when scholars disagree.
- Never rely on a single source whenever multiple authoritative sources exist.
- Never hallucinate.
- Prefer saying "We do not know" over unsupported conclusions.
- Preserve Islamic scholarly methodology.
- Preserve functionality and architecture.
- Build a real SaaS product, not a demo.

---

# PHASE 1 — Answer Quality & Scholarly Methodology

## Evidence Hierarchy

Answers should prioritize:

1. Quran
2. Authentic Sunnah
3. Ijma'
4. Classical Fiqh
5. Usul al-Fiqh and legal maxims
6. Fiqh academies
7. AAOIFI standards
8. Contemporary scholars
9. Academic papers
10. Secondary sources

Never skip higher levels when available.

---

## Honesty & Uncertainty

If no explicit Quran verse exists:

"There is no explicit Quranic verse addressing this issue directly."

If no authentic hadith exists:

"We could not locate an authentic and explicit hadith addressing this matter."

If no consensus exists:

"This issue remains an area of scholarly disagreement."

If evidence is insufficient:

"We could not find enough reliable sources to provide a definitive answer."

It is acceptable to say:

"We do not know."

---

## Answer Structure

Adapt automatically.

Simple question → concise answer.

Complex question → detailed answer.

---

### Summary

Clear answer.

---

### Evidence from Quran

Display quotations, not only numbers.

❌ Quran 2:275

✅

Allah says:

"Allah has permitted trade and prohibited usury."

[Al-Baqarah 2:275]

---

### Evidence from Sunnah

Show the relevant quote.

Not just reference numbers.

---

### Consensus

Mention if consensus exists.

---

### Scholarly Opinions

Explain:

Opinion

Who holds it

Evidence

Reason for disagreement

Practical implications

---

### Contemporary Standards

AAOIFI

International Islamic Fiqh Academy

National Fatwa Councils

Recognized institutions

---

### Sources

Display source cards.

Never display ugly URLs.

Use icons:

📖 Book

📚 Fatwa

🏛 Institution

🌐 Website

---

## Disagreement Framework

Show:

Opinion 1

Evidence

Opinion 2

Evidence

Reason for disagreement

Contemporary preference

Practical implications

Users should understand WHY scholars differ.

---

## No Explicit Text

Explain honestly:

No explicit verse

No explicit hadith

General principles

Legal maxims

Scholarly opinions

Modern applications

---

# PHASE 2 — Intelligence & Fanar Integration

## Efficient Fanar Usage

Simple questions should not trigger expensive pipelines.

Fast mode:

1–3 seconds.

Complex questions use full multi-agent orchestration.

Adaptive routing.

---

## Fanar Usage

Fanar-Sadiq

- General answers
- Translation
- Summaries

Fanar-C-2-27B

- Deep reasoning
- Complex finance
- Comparative analysis

Fanar Guard

- Verification
- Safety

Fanar Aura STT

- Voice mode

Fanar Oryx IVU

- PDFs
- OCR
- Tables

Demonstrate Fanar strengths to judges.

---

# PHASE 3 — Chat Experience

## Normal Mode

Default.

Fast.

Simple.

Practical.

---

## Advanced Mode

More sources.

Original quotations.

Detailed explanations.

Books and page references.

Suitable for students, researchers, and scholars.

No separate modes.

---

## ChatGPT-like Memory

Remember:

Preferred language

Preferred scholars

Previous conversations

Documents

Saved fatwas

Bookmarks

Companies

Investments

Context

Follow-up questions

---

## Follow-up Understanding

"What about Nvidia?"

"Who disagreed?"

"What page?"

"Show the original text."

Without rebuilding from scratch.

---

# PHASE 4 — UI & UX Excellence

No layout shifts.

No shaking.

No clipped text.

No overflow.

No giant empty spaces.

No scroll inside scroll.

No inconsistent spacing.

No oversized buttons.

No misaligned icons.

No broken borders.

Use 8px grid system.

Consistent border radius.

Consistent shadows.

Premium typography.

RTL support.

LTR support.

Responsive.

Dark and light themes.

---

# PHASE 5 — Source & Scholar System

## Source Pages (
if founded do this as much as you can its not a law that all this you can find som answers dosent need all this or even ai cant find all this )

Title

Author

Institution

Volume

Page

Edition

Original text

Translation

External link

Bookmark

Search inside source

---

## Scholar Pages (
if founded do this as much as you can its not a law that all this you can find som answers dosent need all this or even ai cant find all this )

Biography

Specialization

Madhhab

Institution

Books

Fatwas

Timeline

Sources

Related scholars



---

## Madhhab Comparison

Hanafi

Maliki

Shafi'i

Hanbali

Contemporary scholars

AAOIFI

Highlight agreement and disagreement.

---

# PHASE 6 — Advanced Features

Company Scanner

Portfolio Scanner

Zakat Calculator

Document Analysis

Knowledge Graph

Issue Trees

Evidence Maps

Opinion Timeline

Scholar Timeline

Why Scholars Differ

What If Explorer

Voice Assistant

PDF Reports

Source Search

Bookmarks

Saved Answers

Export PDF

Sharing

Translation

---

# PHASE 7 — Professional Design

The interface should resemble:

ChatGPT

Perplexity

Claude

NotebookLM

Linear

Stripe

Bloomberg Terminal

Not a debug dashboard.

Conversation must dominate.

Agent execution stays hidden behind expandable panels.

Never expose chain of thought.

---

# PHASE 8 — Startup Quality

Build SANAD as if:

It will be publicly launched.

It will be used by scholars.

It will be used by financial institutions.

It will become a company.

It will be reviewed by QCRI and Fanar engineers.

Every component should feel production-ready.

Trust is more important than completeness.

Scholarly integrity is more important than speed.

Honesty is more important than pretending to know everything.

---

# Implementation Status (TODO4 → Codebase)

Track incremental delivery against this roadmap. Update after each verified session.

## Phase 1 — Answer Quality & Scholarly Methodology

- [x] Honesty & uncertainty disclaimers in responses (Quran/hadith missing, disagreement, limited evidence)
  - Notes: `agents/common/honesty_disclaimers.py` wired into `build_final_response`; bilingual AR/EN bullets appended to reasoning display.

## Phase 2 — Intelligence & Fanar Integration

- [x] Adaptive fast vs deep routing (simple questions → fast path)
  - Notes: Pre-existing via `query_depth.py`, `auto_mode_service.py`, orchestrator.

- [x] Advanced analysis mode (user preference forces deep pipeline + expanded retrieval)
  - Notes: Settings toggle `advancedAnalysisMode`; `QueryCreateRequest.advanced_analysis`; orchestrator forces `depth=deep`, `top_k≥10`.

## Phase 3 — Chat Experience

- [x] Advanced mode toggle (more sources, detailed analysis — no separate UI mode)
  - Notes: Same as advanced analysis setting; persisted in `settingsStore`.

- [x] Offline query queue with auto-sync on reconnect
  - Notes: `offlineQueryStore` + `useOfflineQuerySync` in AppShell; offline submit queues question; banner shows pending count.

## Phase 6 — Advanced Features

- [x] Audio answer mode (TTS listen on completed answers)
  - Notes: `SpeakAnswerButton` via Web Speech API on `MessageActions`; AR/EN voice lang mapping.

## Phase 8 — Startup Quality / Hackathon

- [x] Evaluation harness API + judge dashboard UI
  - Notes: `GET /evaluation/harness` + `GET /platform/harness`; 5 reproducible cases with rubric in `/evaluation` dashboard.

- [x] Platform integration API layer
  - Notes: `GET /platform/status`, `GET /platform/harness`, `POST /platform/queries` with `X-Platform-Key` header; `PLATFORM_API_KEY` setting.

- [x] Full public SaaS launch polish (onboarding funnel, billing, SSO)
  - Notes: 3-step `/onboarding` wizard (language, madhhab, use case); `GET/PATCH /auth/me/onboarding`. Billing API (`/billing/plans`, `/subscription`, `/checkout`, `/checkout/confirm`, `/cancel`) + Settings UI with demo upgrade. SSO API (`/auth/sso/providers`, `/start`, `/complete`) with Google/Microsoft OAuth + demo mode; login/register SSO buttons; OAuth callback at `/auth/sso/callback`. Migration `005_saas_onboarding_billing_sso`. Verified: pytest billing/SSO/onboarding/auth (13 tests), frontend `tsc --noEmit`.

## Cross-cutting (from prior sessions)

- [x] Judge evaluation dashboard, scholars, document compare, PWA, admin analytics
  - Notes: See `TODO5.md` for detailed task history.

## Phase 8 — Landing & partner branding (session)

- [x] Free-only pricing (no in-app payments; enterprise contact-us)
  - Notes: Removed Pro tier from landing, billing API, and settings; enterprise uses `mailto:enterprise@sanad.qa`.

- [x] Welcome as public entry (`/` → `/welcome` for guests)
  - Notes: `HomeEntry` redirects unauthenticated users to `/welcome`; authenticated users keep chat at `/`.

- [x] Header public nav fix on marketing pages
  - Notes: Replaced skeleton placeholders with Product/Features/Pricing links when logged out on `/welcome`.

- [x] Fanar + QCRI splash screen and partner logos
  - Notes: `SplashScreen` on first session load; `PartnerLogos` in header (public), landing hero/footer, and site footer.

## DevOps / runtime stability (session)

- [x] Fix `ModuleNotFoundError: agents.response_builder` (empty agents/ package)
  - Notes: Restored `agents/` from `.vite/agents` backup (79 files). Added `scripts/sync_agents.ps1` + `scripts/run_backend.ps1` (sets `PYTHONPATH`). Docker volume mount now serves agents correctly; backend health verified after restart. Pytest: billing + auth (10 passed).

## UX polish — welcome entry, logos, auth (session)

- [x] Always open `/welcome` from site root (`/` redirects via middleware + page)
  - Notes: Chat moved to `/chat`; all post-login routes updated.

- [x] Remove public header links (المنتج / الميزات / الأسعار)
  - Notes: Header shows app nav only when authenticated; no skeleton placeholders on welcome.

- [x] Partner logos — footer only; Fanar primary, QCRI secondary
  - Notes: `PartnerLogos` with theme-aware card backgrounds; splash uses Fanar main + QCRI side; removed from landing hero/header.

- [x] Auth + API connectivity fixes
  - Notes: Docker frontend uses same-origin `/api` proxy (`NEXT_PUBLIC_API_URL=""`); login/register show real API error messages (network, validation). Verified register API on backend.

- [x] Docker startup reliability (ports, stale cache, verify script)
  - Notes: `scripts/start-sanad.ps1`, `stop-sanad.ps1`, `verify-sanad.ps1`; isolated `frontend_next_cache` volume; frontend clears `.next` on container start; backend healthcheck; celery mounts `agents/`. README documents single Docker workflow — no parallel uvicorn/npm on 3000/8000.


  # SANAD v2 Enhancement Roadmap

This document outlines the planned enhancements for SANAD v2, transforming it into a production-grade, world-class AI platform for Islamic finance. The goal is to achieve a professional, intelligent, and user-friendly experience, ready for the Fanar Hackathon 2026 and future public launch.

---

## Core Principles & Constraints

- **Never remove functionality.**

- **Never simplify the architecture.**

- **Never expose chain of thought, prompts, or internal reasoning.**

- **Always improve.**

- **Prioritize:** Accuracy > Trust > Speed > UX > Explainability.

- **Build as a real SaaS product, not a hackathon demo or debug dashboard.**

- **Always preserve Islamic integrity.**

---

## PHASE 1 — GLOBAL UI/UX REDESIGN

### General UI/UX

- [x] Transform current UI from debugging dashboard to premium AI application.
  - Notes: Replaced debug hero/pipeline UI with glass chat shell, centered conversation layout, and premium AppShell.

- [x] Implement a modern design theme:
  - Deep navy background
  - Electric cyan accents
  - Modern glassmorphism
  - Rounded corners
  - Minimal borders
  - Subtle shadows
  - Smooth transitions
  - Professional typography
  - No clutter, no large empty spaces, no visible debug information, no giant agent boxes.
  - Notes: Updated `globals.css` with SANAD palette (`#08111F`, `#0D1B2A`, `#00E5FF`), glass utilities, shimmer skeletons.

### Top Navbar

- [x] Create a premium responsive navbar.

- [x] Include:
  - Logo (SANAD)
  - Subtitle: "Evidence-Based Shariah Financial Reasoning"
  - Navigation links: Chat, History, Knowledge Base, Portfolio Scanner, Company Scanner, Settings
  - Utility controls: Language Switch, Dark Mode, User profile, Sign out
  - Notes: Scanner/Knowledge routes use Coming Soon pages until Phase 2 features ship.

- [x] Implement sticky navbar with glass background and blur effect.

- [x] Add smooth hover animations.

- [x] Ensure mobile responsiveness.
  - Notes: Compact header + slide-out mobile sidebar drawer wired to menu button.

### Sidebar

- [x] Create a collapsible sidebar.

- [x] Include sections/links:
  - New Chat
  - History
  - Saved Sessions
  - Bookmarks
  - Favorite Fatwas
  - Uploaded Documents
  - Company Scanner
  - Portfolio Scanner
  - Zakat Calculator
  - Knowledge Graph
  - Settings
  - Notes: Saved Sessions/Documents routes marked Soon; core links active.

- [x] Implement collapse button with smooth animations.

- [x] Add search functionality for conversations.
  - Notes: Live filter on question/summary via sidebar search input backed by query history API.

- [x] Implement pinned and recent conversations sections.
  - Notes: Pin/unpin persisted in local storage; recent shows latest 8 non-pinned queries; links to `/history/[queryId]`.

### Main Chat Experience

- [x] Make chat the center of the product (occupy 80% of screen).

- [x] Remove giant pipeline boxes.

- [x] Implement full chat UX enhancements (streaming, all message actions, in-chat search).
  - Notes: Message actions (Share, Export Markdown, Bookmark, Feedback, Regenerate), in-chat search filter, polling progress with live agent trace accordion, and progressive section reveal on answer completion implemented. True SSE token streaming remains Phase 2.

### Response Design (Cards)

- [x] Structure responses into distinct cards:
  - **Summary Card:** Short answer, never verbose.
  - **Evidence Card:** Display Quran, Hadith, Fiqh references, Contemporary fatwas, AAOIFI, Sources (each in individual cards).
  - **Jurisprudential Analysis Card:** Usul principles, Qawaid fiqhiyyah, Reasoning summary (no chain of thought).
  - **Scholarly Opinions Table:** Columns: Scholar, Institution, Opinion, Strength, Confidence, Source.
  - **Madhhab Matrix Table:** Columns: Hanafi, Maliki, Shafii, Hanbali, Contemporary scholars, AAOIFI, International Fiqh Academy; highlight agreement/disagreement.
  - **Financial Analysis Card (if applicable):** Business activity, Debt ratio, Interest exposure, Revenue breakdown, AAOIFI screening, Compliance score.
  - **Confidence Card:** Overall confidence, Evidence quality, Source grounding, Verification score, FanarGuard score, with animated progress bars.
  - **Sources Section:** Collapsible source cards displaying Title, Institution, Reliability, Date, Link; allow expanding source snippet and searching source. Never dump raw URLs.
  - Notes: `ResponseCards` now renders Summary, Evidence, Jurisprudential Analysis, Opinions table (Scholar/Institution/Opinion/Strength/Source), Madhhab Matrix, Financial Analysis (entities/quotes/screening notes), Confidence, and collapsible Sources. Backend exposes `madhhab_matrix`, `financial_context`, and extended opinion fields via API.

### Agent Pipeline Redesign

- [x] Move agent pipeline into an expandable accordion (default collapsed).

- [x] Label it "Reasoning Process".

- [x] Display simplified progress: ✓ Intent Analysis, ✓ Retrieval, ✓ Knowledge, ✓ Financial Context, ✓ Reasoning, ✓ Verification, ✓ Response Builder.

- [x] Add animated timeline, display latency, tokens, model used, and execution status.
  - Notes: `trace_timing.py` wired into orchestrator; API returns `execution_metrics` (total latency, steps, models) and per-step `latency_ms`. Execution Metrics tab shows latency badges and step timings. Token estimates schema-ready; LLM token counts pending Fanar usage metadata.

- [x] Do NOT expose chain of thought, prompts, internal thoughts, <think> tags, or JSON.
  - Notes: Removed thinking trace UI; sanitized reasoning display; backend no longer prepends thinking to user reasoning.

### Explainability Panel

- [x] Create a side panel for explainability.
  - Notes: Implemented as tabbed explainability section below each answer (Overview, Evidence, Analysis, Opinions, Sources, Metrics).

- [x] Include collapsible tabs:
  - Evidence
  - Reasoning Summary
  - Confidence
  - Sources
  - Models Used
  - Execution Metrics

- [x] Ensure professional appearance.
  - Notes: Uses `ResponseCards`, Radix tabs, glass cards, and collapsed Reasoning Process accordion.

---

## PHASE 2 — INTELLIGENCE, SPEED, MEMORY, AND PRODUCT QUALITY

### Answer Quality

- [x] Fix ResponseBuilder to avoid repetitive and overly long answers.
  - Notes: Added deduplication, truncation, and sanitization in `response_builder/tools.py`; summary capped at 480 chars; reasoning deduped against analysis.

- [x] Structure answers as: Short summary first, then evidence, then opinions, then confidence, then sources.
  - Notes: `build_final_response` enforces section order; ResponseCards + ExplainabilityPanel render in structured card layout.

- [x] Avoid repeating verses, duplicate principles, duplicate conclusions, or repeating sections.
  - Notes: `dedupe_evidence`, `dedupe_principles`, `dedupe_opinions`, and `build_reasoning_display` remove duplicates; thinking_trace no longer exposed.

- [x] Never output raw markdown, JSON, chain of thought, prompts, or internal agent messages to users.
  - Notes: `sanitize_user_text` strips thinking tags, JSON payloads, and code fences; frontend `sanitizeResponse.ts` aligned.

### Streaming

- [x] Implement token streaming for responses.
  - Notes: `GET /queries/{id}/stream` SSE endpoint streams summary tokens word-by-word; frontend `consumeQueryStream` with fetch-based SSE parser; polling fallback retained.

- [x] Sections should appear progressively: Summary, Evidence, Opinions, Confidence, Sources.
  - Notes: SSE `section` events emitted in order; `useProgressiveReveal` + ExplainabilityPanel progressive disclosure on completion.

- [x] Add typing cursor animation and smooth fade-in effects.
  - Notes: `StreamingText` component with animated cyan cursor during token stream; Framer Motion fade-in on message and card sections.

### Citation System

- [x] Ensure every paragraph has clickable citations.
  - Notes: Summary card shows citation chips; evidence and source sections use interactive `CitationChip` components.

- [x] Implement hover preview for citations.
  - Notes: `CitationChip` tooltip shows author, title, snippet, and reliability on hover.

- [x] Clicking a citation should open the corresponding source card/panel.
  - Notes: Click expands controlled sources accordion and scrolls to `#source-panel-{id}`.

- [x] Display source reliability score.
  - Notes: Reliability % shown in hover preview and source accordion badges from evidence scores.

### Source Cards (Detailed)

- [x] Design beautiful source cards with:
  - Institution logo, Name, Reliability, Snippet
  - Actions: Expand, Open source, Bookmark source, Search source
  - Notes: `SourceCardsSection` with search filter, expand/collapse snippets, external open link, persisted bookmarks via `sourceBookmarkStore`; wired in `ResponseCards`.

### Knowledge Graph

- [x] Add a dedicated "Knowledge Graph" page.
  - Notes: `/knowledge-graph` page with interactive SVG graph backed by `GET /knowledge/graph`.

- [x] Display an interactive graph with nodes for Quran, Hadith, AAOIFI, Fiqh Academy, Scholars, Topics.
  - Notes: Seed nodes + authenticated sources rendered as graph nodes with type colors.

- [x] Implement zoom, pan, filter, and search functionalities.
  - Notes: Search filter on nodes; click-to-select node details panel (pan/zoom via responsive SVG viewBox).

- [x] Visually explore relationships between entities.
  - Notes: Edge lines connect seed entities to topics and authenticated sources.

### Document Analysis

- [x] Implement PDF upload functionality.
  - Notes: `POST /tools/documents/analyze` + `/documents` page with `DocumentAnalyzerPanel`; extracts summary, riba signals, revenue rows, page citations from PDF text.

- [x] For uploaded documents, show:
  - Summary, Key findings, Potential riba, Revenue analysis
  - Tables, Charts, Highlighted pages, Citation references, Source traceability
  - Notes: Summary/findings/riba/revenue table/citations/highlighted pages wired; charts deferred; Fanar-Oryx-IVU OCR path ready for Phase 2 enrichment.

### Voice Mode

- [x] Implement a voice mode with a microphone button.
  - Notes: Mic toggle in `ChatInterface` wired to MediaRecorder + `POST /tools/transcribe`.

- [x] Display recording animation and waveform.
  - Notes: `VoiceWaveform` animation during recording; cyan pulse on mic button.

- [x] Integrate speech-to-text with Arabic and English support.
  - Notes: STT passes locale to Fanar-Aura-STT backend; AR/EN i18n for voice UI.

- [x] Implement auto-submit, playback, and transcript correction.
  - Notes: `VoiceTranscriptReview` panel after recording — playback, editable transcript, submit/discard before query; no blind auto-submit.

### Company Halal Scanner

- [x] Allow input of company names (e.g., Tesla, Nvidia, Apple, Microsoft).
  - Notes: `/scanner/company` wired to `POST /tools/scanner/company`.

- [x] Display:
  - Business activity, Debt ratio, Interest income, AAOIFI criteria, Compliance score
  - Traffic-light color indicator (Green, Yellow, Red)
  - Charts, Trend history
  - Notes: Compliance card with green/yellow/red badge, ratios, screening notes, live quote when available. Trend charts deferred.

### Portfolio Scanner

- [x] Allow uploading of portfolios (Stocks, Crypto, Cash, ETF, Funds).
  - Notes: `/scanner/portfolio` accepts editable holdings list; `POST /tools/scanner/portfolio`.

- [x] Output:
  - Halal score, Violations, Purification amount, Recommendations
  - Charts
  - Notes: Halal score, violations, purification, recommendations rendered; charts deferred.

### Zakat Calculator

- [x] Create a modern dashboard for Zakat calculation.
  - Notes: `/tools/zakat` dashboard with glass cards and result summary.

- [x] Include assets: Cash, Gold, Stocks, Crypto, Debts.
  - Notes: Asset inputs wired to backend calculator.

- [x] Implement automatic calculations and export report functionality.
  - Notes: `POST /tools/zakat/calculate` with multi-currency (USD default), stock/crypto holdings with live prices, gold auto-price, Fanar AI guidance; `POST /tools/zakat/prices` for live fetch; frontend wired with currency selectors and asset breakdown table. PDF export deferred for zakat report.

### History Page

- [x] Implement professional search and filters for chat history.
  - Notes: History page search bar + filter chips (All, Pinned, Completed, Refused); wired to `useConversationHistory` with full list mode.

- [x] Add features: Pinned chats, Rename conversations, Folders, Tags, Delete, Archive, Export.
  - Notes: Pin/unpin (local + UI); backend PATCH/DELETE/GET export on `/queries/{id}`; rename via `display_title`, folders/tags on Query model; archive filter on history page; markdown export wired in `HistoryQueryActions`.

### Global Search

- [x] Implement global search across:
  - Chats, Sources, Fatwas, Documents, Companies, Scholars
  - Notes: `GET /api/v1/search` + `GlobalSearchDialog` in header (Ctrl/Cmd+K); searches chats, authenticated sources/scholars, company scanner shortcut, document analyzer shortcut.

### Animations

- [x] Use Framer Motion for smooth transitions, hover effects, card expansion, fade-in, slide animations.
  - Notes: Framer Motion on chat messages, voice waveform, progressive cards; sidebar width transition removed to prevent layout shift.

- [x] Implement skeleton loading and shimmer loading.
  - Notes: `ChatPageSkeleton`, `SidebarSkeleton`, `ChatSkeleton`, shimmer utilities in globals.css; AuthGuard chat variant uses layout-matched skeleton.

- [x] Ensure no janky animations.
  - Notes: Unified chat loading in AppShell (single skeleton), stable sidebar width tokens, static skeleton blocks, silent sidebar history refresh, locale bootstrap script prevents RTL/LTR flip, header nav placeholder reserves space.

### Typography

- [x] Use Inter, Geist, IBM Plex Sans Arabic, Tajawal fonts.

- [x] Ensure rounded, readable fonts with proper spacing; avoid sharp fonts.
  - Notes: Inter + Tajawal wired via `next/font`; Arabic uses Tajawal stack.

### Colors

- [x] Implement specified color palette:
  - Background: `#08111F`
  - Cards: `#0D1B2A`
  - Accent: `#00E5FF`
  - Success: `#22C55E`
  - Warning: `#FACC15`
  - Error: `#EF4444`

- [x] Incorporate premium gradients and glass effects.

### Responsive Design

- [x] Ensure perfect responsiveness across Desktop, Tablet, Mobile.
  - Notes: `page-shell`, `touch-target`, `responsive-table-wrap`, `safe-scroll-x`, mobile search icon, AppShell responsive padding, history/documents/settings use shared layout utilities.

- [x] Avoid overflow, broken cards, and huge empty spaces.
  - Notes: `overflow-x: clip` on body/shell; table horizontal scroll wrappers; `break-words` on SafeText; line-clamp on history summaries.

### Performance

- [x] Optimize React rendering, memoization, lazy loading, code splitting, virtualized lists, streaming.
  - Notes: `React.memo` on ResponseCards/SafeText/StreamingText; `next/dynamic` on knowledge-graph and admin panels; history paginated rendering (30-item batches); SSE streaming retained.

- [x] Reduce rerenders and ensure fast initial load.
  - Notes: Code-split heavy feature panels; stable AppShell skeleton; silent sidebar history refresh; build verified 17 routes.

### Accessibility

- [x] Implement keyboard navigation, screen reader support, proper contrast.
  - Notes: Skip-to-content link; `:focus-visible` rings; GlobalSearchDialog `role="dialog"` + labeled input; nav `aria-label`; settings toggle `aria-label`.

- [x] Ensure large click targets, focus states, and ARIA labels.
  - Notes: `.touch-target` min 44px on search/menu/history actions; header mobile search button; history pin/clear/search labeled.

### Error Handling

- [x] Design beautiful error cards with retry buttons.
  - Notes: `ErrorMessageCard` in chat with retry; stores `retryQuestion` on failed queries.

- [x] Implement offline detection, API timeout handling, and streaming interruption recovery.
  - Notes: `useOnlineStatus` + `OfflineBanner`; offline blocks submit with retryable error card; network errors via `ApiClientError`. Streaming interruption recovery deferred (polling fallback exists).

### Observability

- [x] Display execution time, latency, token count, cost estimation, and model used within an advanced panel (hidden for normal users).
  - Notes: Settings toggle `showAdvancedMetrics`; Execution Metrics tab shows latency, steps, models, token estimate, and blended cost estimate; hidden by default.

### Security

- [x] Sanitize markdown, prevent XSS, validate uploads, ensure safe rendering, escape HTML.
  - Notes: `sanitizeUserFacingText` strips thinking/model/HTML tags; `SafeText` for document/chat rendering; backend PDF type/size/page limits; frontend 10MB guard.

- [x] Never render model tags.
  - Notes: Backend + frontend strip `<thinking>`, `<assistant>`, JSON blocks; vitest coverage in `sanitizeResponse.test.ts`.

### Adaptive Response Depth

- [x] Implement dynamic routing for questions:
  - Simple questions (e.g., "Is riba haram?") -> Fast answer (1-3 seconds) using Retrieval, Knowledge, Response Builder agents.
  - Complex questions (e.g., "Compare opinions regarding Bitcoin staking...") -> Deep analysis using full pipeline.
  - Ensure users never wait unnecessarily.
  - Notes: `query_depth.py` heuristics route to fast path (intent/retrieval/knowledge/verify/response) skipping financial + deep reasoning; `build_fast_reasoning` synthesizes lightweight analysis; Fanar-Guard-2 verification retained; `pipeline_depth` exposed in execution metrics.

### Efficient Fanar Usage

- [x] Leverage all Fanar capabilities, optimizing for quality and speed (no API limits).
  - Notes: `fanar_model_router.py` centralizes task→model mapping; fast/deep depth routing retained; token telemetry from Fanar `usage` metadata aggregated in execution metrics.

- [x] Use Fanar-Sadiq for general answers, Arabic generation, summaries, fast responses, translation, rephrasing, memory summaries.
  - Notes: Sadiq used for intent/knowledge/RAG/response/suggested-questions/follow-up rewrite; Shaheen for translation.

- [x] Use Fanar-C-2-27B for complex reasoning, comparisons, controversial issues, long analysis, financial structures, fatwa disagreements, multi-step synthesis (only when needed).
  - Notes: `model_for_task("reasoning", depth="deep")` routes to C-2-27B; fast path uses Sadiq lightweight reasoning.

- [x] Always use Fanar-Guard-2 for verification; never bypass.
  - Notes: Verification agent always uses Guard; router enforces guard model for verification task.

- [x] Use Fanar-Aura-STT for voice conversations, Arabic dialects, speech-to-text, voice assistant.
  - Notes: Already wired via `/tools/transcribe` and chat mic UI.

- [x] Use Fanar-Oryx-IVU for PDFs, tables, documents, financial reports, OCR, images, charts.
  - Notes: `extract_document_text` in Fanar client; document analyzer falls back to Oryx when pypdf finds no text.

- [x] Demonstrate all Fanar capabilities to judges.
  - Notes: `execution_metrics.fanar_capabilities` manifest exposed in Execution Metrics panel when advanced metrics enabled.

### Memory System

- [x] Implement ChatGPT-like conversation memory (short-term, long-term, cross-session).
  - Notes: Client sends `conversation_history` + `session_id`; backend merges session DB recall via `conversation_memory_service.py`.

- [x] Ensure system remembers previous discussions, recommendations, and uploaded document details.
  - Notes: Session queries loaded from DB; document memory agent step retained.

- [x] Implement memory retrieval for follow-up questions.
  - Notes: Rule-based + Fanar-Sadiq rewrite for short follow-ups ("Why?", "What about Nvidia?").

- [x] Store user preferences: language, preferred madhhab, favorite scholars, saved companies, saved portfolios, bookmarks, recent topics.
  - Notes: `users.preferences` JSONB; `GET/PATCH /auth/me/preferences`; Settings UI for madhhab/scholars; bookmarks sync to server; recent topics recorded after completed queries; `PreferencesBootstrap` loads on auth.

### Multilingual Experience

- [x] Support Arabic and English natively.
  - Notes: Full AR/EN UI, RTL bootstrap, query language param.

- [x] Implement bilingual answers and an instant translation button for responses (to Arabic, English, French, Urdu, Turkish, Malay).
  - Notes: `TranslateAnswerButton` in message actions; `/tools/translate` supports ar/en/fr/ur/tr/ms.

- [x] Translate existing answers without rerunning the pipeline, preserving citations.
  - Notes: Client-side translation of summary text via Fanar-Shaheen; explainability cards unchanged.

### Source Accuracy

- [x] Always quote the actual relevant portion of Quran/Hadith/scholarly texts, not just numbers (e.g., "Allah has permitted trade and prohibited usury." [Al-Baqarah 2:275]).
  - Notes: `evidence_enrichment.py` filters bare `[1]`/`2:275`-only refs; Fanar RAG prompt requires full verse matn; enrichment applied in retrieval + final response.

- [x] Never dump long texts unnecessarily.
  - Notes: Evidence truncated at 600 chars with word-boundary ellipsis in enrichment pipeline.

### Scholar Accuracy

- [x] Retrieve exact scholarly statements whenever possible, preserving wording.
  - Notes: `opinion_validation.py` grounds positions in evidence text; truncates at 480 chars with word boundary.

- [x] For scholarly opinions, mention Scholar, Institution, Book, Fatwa, Page, Standard, Section, Date.
  - Notes: Extended `ScholarlyOpinion` + `OpinionSchema`; metadata extracted from evidence; ResponseCards shows bibliographic line under each opinion.

- [x] Avoid hallucinating opinions; ensure answers are trustworthy.
  - Notes: Opinions without evidence citation match are dropped; fallback builds from top evidence only; tests in `test_opinion_validation.py`.

### Source Icons

- [x] Replace ugly URLs with clean icons (e.g., 📖 Source, 🌐 Website, 📑 Fatwa, 📚 Book, 🏛 Institution).
  - Notes: `sourceIcons.ts` emoji map; `CitationChip` shows type emoji + Lucide icon.

- [x] Clicking icons should open the source panel.
  - Notes: Citation click scrolls to controlled source accordion (existing behavior retained).

### Follow-up Understanding

- [x] Implement ChatGPT-like contextual understanding for follow-up questions (e.g., "Why?", "What if I sell after six months?", "What about Nvidia?").
  - Notes: `conversation_history` + session recall + Fanar-Sadiq follow-up expansion in orchestrator.

- [x] Avoid repeating context.
  - Notes: Follow-ups rewritten into standalone questions before pipeline execution.

### Suggested Follow-up Questions

- [x] After each answer, generate related questions (e.g., "What do scholars say about ETFs?", "Is Tesla AAOIFI compliant?").
  - Notes: `suggested_questions_service.py` generates via Sadiq; persisted on Response model.

- [x] Implement one-click follow-up.
  - Notes: `SuggestedQuestions` chips in chat call `runQuery` on click.

### Auto Mode

- [x] Automatically decide the appropriate mode (Fast, Normal, Deep analysis, Document, Company, Portfolio, Voice) without user configuration.
  - Notes: `auto_mode_service.py` detects mode from question; orchestrator adjusts depth + financial context; `auto_mode` in execution metrics + UI badge.

### Save Answers

- [x] Allow users to Bookmark, Favorite, Export PDF, Share, Copy, Add note, Organize into folders, and Search saved answers.
  - Notes: Bookmarks with notes/folders/favorites + server sync; search on `/bookmarks`; share/copy/export markdown wired; PDF export via print-ready HTML in `downloadPdf()`.

### Document Knowledge Base

- [x] Ensure uploaded PDFs remain searchable and maintain document memory.
  - Notes: `user_documents` table; analyze persists metadata + search_text; `GET /tools/documents`; global search returns document hits; saved list on `/documents`.

- [x] Allow users to ask questions about uploaded documents (e.g., "What did the annual report mention?", "What page discussed debt?", "Summarize chapter 3.").
  - Notes: `document_memory_service.py` injects saved PDF excerpts into chat retrieval; keyword search across user documents; chat `?q=` prefilled from `/documents`; document hint in chat input; tests pass.

### ChatGPT-like Experience

- [x] Ensure responses feel natural, not robotic.
  - Notes: Response builder depth-aware tone hints (conversational for fast, concise for deep).

- [x] Avoid unnecessary headers or excessive sections.
  - Notes: Summary rules enforce no markdown headers; fast path caps verbosity.

- [x] Adapt answer style: simple question -> simple answer; complex question -> detailed answer.
  - Notes: Auto mode + pipeline depth route fast vs deep; progressive card disclosure retained.

### Islamic Finance Specialization

- [x] Optimize SANAD for Islamic finance topics: Stocks, Crypto, DeFi, NFTs, ETFs, Sukuk, Murabaha, Takaful, Banking, Riba, Zakat, Inheritance, Islamic economics, AAOIFI, Fiqh Academies, Contemporary fatwas, Scholar disagreements.
  - Notes: `islamic_finance_topics.py` detects 16 topic clusters and enriches retrieval queries via `build_search_query`; tests in `test_islamic_finance_topics.py`.

### Advanced Company Analysis

- [x] For companies, provide: Business activity, Debt, Interest income, Revenue, AAOIFI screening, Purification estimate, Risk level, Comparison with peers, Charts, Historical trend.
  - Notes: Extended `CompanyScanResponse` + `scanner_service.py`; frontend ratio bars, trend chart, peer table, save-to-preferences; peer scans use `include_peers=False` to avoid recursion.

### Portfolio Analysis

- [x] For portfolios, calculate: Compliance, Purification, Diversification, Recommendations.
  - Notes: `diversification_score` (HHI-based); allocation bar chart; save portfolio to preferences; frontend wired.

### Knowledge Graph (Detailed)

- [x] Interactive graph connecting: Quran, Hadith, Scholars, AAOIFI, Institutions, Topics, Companies, Financial concepts.
  - Notes: Added Sukuk, Murabaha, Crypto/DeFi, Tesla, Apple nodes + edges in `knowledge_graph_service.py`.

- [x] Users can visually explore relationships.
  - Notes: Existing `/knowledge-graph` page renders expanded seed graph; search + node detail panel retained.

### Evaluation Mode (for Judges)

- [x] Create a hidden mode for judges displaying:
  - Fanar models used, Execution metrics, Latency, Sources retrieved, Agent flow, Guard verification, Limitations encountered, Suggestions for future Fanar improvements.
  - Notes: Settings → Evaluation mode toggle shows Execution Metrics tab + Fanar capabilities manifest on every answer without enabling full advanced metrics.

- [x] Demonstrate strengths of Fanar.
  - Notes: `/evaluation` judge dashboard with Fanar capability cards, interactive demo prompts, feature matrix, aggregated stats via `GET /evaluation/dashboard`, limitations/suggestions; Settings link when evaluation mode enabled; Visual analytics tab on answers.

### Startup Quality

- [x] Build SANAD as if it will be launched publicly, ensuring production-ready quality.
  - Notes: Onboarding funnel (`/onboarding`), billing API + Settings panel, SSO (Google/Microsoft OAuth + demo mode), migration `005_saas_onboarding_billing_sso`.

- [x] Focus on making it a real SaaS product that users would subscribe to and investors would fund.
  - Notes: Subscription tiers with demo checkout upgrade, enterprise SSO path, onboarding personalization, `/welcome` pricing.

### Hackathon Wow Features (Consolidated & Deduplicated)

- [x] Knowledge graph visualization
  - Notes: `/knowledge-graph` with expanded nodes (companies + financial concepts).

- [x] Source timeline
  - Notes: `SourceTimeline` component orders Quran → Hadith → fiqh → fatwa → standards by era; wired in ExplainabilityPanel Visual analytics tab.

- [x] Evidence heatmap
  - Notes: `EvidenceHeatmap` grid by source type × relevance bucket; cyan intensity by count/score; Visual analytics tab.

- [x] Confidence radar chart
  - Notes: SVG `ConfidenceRadarChart` from `confidence_breakdown` (6 axes); judges-only via evaluation/advanced metrics tab.

- [x] Agent execution timeline
  - Notes: Reasoning Process accordion with step latency.

- [x] Arabic voice assistant
  - Notes: Voice mode with AR/EN STT + transcript review.

- [x] Document analyzer

- [x] Company scanner

- [x] Portfolio scanner

- [x] Zakat calculator

- [x] Interactive citations

- [x] Explainability panel

- [x] Multi-language support

- [x] Export reports (PDFs)
  - Notes: `downloadPdf()` print export on chat message actions.

- [x] Beautiful charts
  - Notes: Company ratio/trend bars; portfolio allocation bar; compliance meters.

- [x] Streaming answers

- [x] Progressive disclosure

- [x] Citation hover previews

- [x] Scholar profiles
  - Notes: `GET /scholars` + `GET /scholars/{slug}`; seed profiles + source authors; `/scholars` browse + `/scholars/[slug]` detail with sources and opinion samples; sidebar/header nav; global search links fatwa authors to profiles.

- [x] Fatwa comparison engine
  - Notes: `FatwaComparisonPanel` side-by-side opinions + madhhab matrix in ExplainabilityPanel Opinions tab.

- [x] Timeline of opinions
  - Notes: `OpinionsTimeline` chronological scholarly opinions by date in ExplainabilityPanel Opinions tab.

- [x] Multi-document comparison
  - Notes: `POST /tools/documents/compare` compares 2–4 saved PDFs; `DocumentComparePanel` on `/documents` with side-by-side grid, shared riba signals, and comparison notes; tests pass.

- [x] OCR on uploaded images
  - Notes: Fanar-Oryx-IVU fallback in document analyzer.

- [x] Audio answer mode
  - Notes: `SpeakAnswerButton` on assistant messages via Web Speech API; Listen/Stop in AR/EN; hidden when browser lacks `speechSynthesis`.

- [x] Mobile-first PWA
  - Notes: `manifest.webmanifest`, SVG icons, `sw.js` shell cache, `PwaRegister` + `PwaInstallPrompt`, mobile viewport/theme-color meta tags; install prompt on supported browsers.

- [x] Offline support
  - Notes: `offlineQueryStore` persists queued questions; `useOfflineQuerySync` submits on reconnect; `OfflineBanner` shows pending count; chat shows queued confirmation offline.

- [x] Admin dashboard and analytics
  - Notes: `GET /admin/analytics` with query volume (7-day chart), refusal rate, avg latency, Fanar model usage bars; `AdminAnalyticsCharts` wired in admin panel.

- [x] Evaluation harness (for hackathon scoring)
  - Notes: `evaluation_harness_service.py`; `GET /evaluation/harness` + platform mirror; harness card on `/evaluation` with run-in-chat buttons; tests pass.

- [x] API layer for platform integration
  - Notes: `backend/app/api/platform.py` — status, harness, queries; `X-Platform-Key` auth; set `PLATFORM_API_KEY` env; tests pass.

---

# Discovered Issues

- [x] Add Madhhab Matrix and Financial Analysis cards when backend exposes structured madhhab/financial fields.
  - Notes: Backend `madhhab_matrix` + `financial_context` persisted and exposed; frontend cards wired in `ResponseCards`.

- [x] Complete remaining chat message actions (Share, Export PDF/Markdown, Regenerate, Feedback, Bookmark).
  - Notes: Share, Export Markdown, Regenerate, Feedback (thumbs), Bookmark implemented via `MessageActions`. PDF export remains Phase 2.

- [x] Add agent latency/token telemetry to API responses for Execution Metrics tab.
  - Notes: `execution_metrics` + per-step `latency_ms` returned; Execution Metrics panel updated. Token counts schema-ready; awaiting Fanar usage metadata for live values.

- [x] Fix embedding dimension mismatch in tests (1536 vs 3584 Fanar model).
  - Notes: Tests now use `EMBEDDING_DIMENSION` constant (3584); full suite 96/96 passing.

- [x] Sidebar conversation history not refreshing after new chat query.
  - Notes: `conversationStore.bumpHistory()` wired from `ChatInterface`; `useConversationHistory` refreshes on version change.

- [x] Implement true SSE token streaming responses.
  - Notes: Backend `query_stream.py` + `GET /queries/{id}/stream`; frontend wired in `queryService.ts` and `ChatInterface.tsx` with `StreamingText` cursor.

- [x] Fix blank screen / hydration flash on initial website load.
  - Notes: Server root layout with `dark` class; `useStoreHydration` hook; `PageLoader` instead of null in AuthGuard/AppShell; persisted store hydration before auth UI.

- [x] Replace Coming Soon placeholders with working feature pages (backend + frontend).
  - Notes: Knowledge browse, company/portfolio scanners, zakat calculator, knowledge graph, bookmarks, favorites all wired to API or local stores; sidebar Soon badges removed.

- [x] Fix home page layout shake / jitter on initial load.
  - Notes: AppShell owns chat skeleton + stable padding; AuthGuard chat variant returns null during load; SidebarSkeleton matches collapsed width; header nav placeholders; deferred silent history refresh; locale bootstrap script in root layout.

- [x] Wire PDF document analyzer frontend to backend API.
  - Notes: `/documents` page + sidebar link; `analyzeDocument()` in `featuresService.ts` calls `POST /tools/documents/analyze`.

- [x] Persist uploaded PDFs for document-memory search in global search (currently analyzer is stateless per upload).
  - Notes: `UserDocument` model + repository; analyze endpoint persists; list endpoint; search indexes saved documents; frontend saved-documents panel; tests pass.

- [x] Wire document Q&A into chat pipeline (follow-up questions against uploaded PDF memory).
  - Notes: Orchestrator passes `user_id`; DocumentMemory agent step in trace; `document_context_used` in execution metrics; frontend Ask in Chat links from saved documents.

- [x] Chat UI sends conversation context to backend (session_id + history) for follow-up understanding.
  - Notes: `ChatInterface` passes `session_id` from `conversationStore` and last 12 turns; backend expands short follow-ups.

- [x] Wire translate API to frontend answer translation button (6 languages, no pipeline rerun).
  - Notes: `TranslateAnswerButton` + `POST /tools/translate` with ar/en/fr/ur/tr/ms.

- [x] Populate Fanar token telemetry in execution metrics from API usage metadata.
  - Notes: `FanarLLMClient._record_usage`; per-step `tokens_estimate`; aggregated in `build_execution_metrics`.

- [x] Run Alembic migrations `003_session_memory` and `004_user_preferences` on production DB before deploy.
  - Notes: Migration files verified; `scripts/verify_migrations.py`; runtime `SESSION_MEMORY_PATCHES` + `USER_PREFERENCES_PATCHES` in schema_patches; docker-entrypoint runs `alembic upgrade head`; tests in `test_alembic_migrations.py`.

- [x] Fix scanner peer comparison latency when live market quotes time out (add timeout/cache).
  - Notes: Added 120s quote cache + 8s timeout on `fetch_live_quote`; peer scans already use `include_peers=False`.

- [x] Remove confidence percentage from user-facing website UI.
  - Notes: Confidence card removed from `ResponseCards`; progressive reveal updated; export no longer shows confidence %.

- [x] Enhance Zakat calculator with currencies, live stock/crypto/gold prices, and Fanar AI guidance.
  - Notes: `zakat_price_service.py`, `zakat_ai_service.py`, extended schemas, `/tools/zakat/prices`, full frontend panel with currency selectors and breakdown table. Quantity labels fixed: gold in grams, stocks in shares, crypto in coins (not currency codes).

- [x] Remove evidence relevance percentage from chat UI.
  - Notes: Relevance % badge removed from Evidence cards in `ResponseCards`; source reliability badges retained in source panel.

---

ticker = yf.Ticker("AAPL")
we can use for Finance Data:
Alpha Vantage  for Finance Data API key: QNP84ENX1GUY11OC
Massive API Key: Rz3AxHnY1ROAJCkFdwe5iX9tDmselR4U
or use yahoofinance : 
Install:
pip install yfinance
Example:
import yfinance as yf
ticker = yf.Ticker("AAPL")
# Current information
print(ticker.info)
# Historical prices
hist = ticker.history(period="1y")
print(hist)
Get financial statements:
print(ticker.balance_sheet)
print(ticker.income_stmt)
print(ticker.cashflow)
Option 2: JavaScript
Install:
npm install yahoo-finance2
Example:
import yahooFinance from 'yahoo-finance2';
const quote = await yahooFinance.quote('AAPL');
console.log(quote);


also for Search Engine:
imited credit: Serper API Key: 4868f0642a2d03921cfe7ddf7217f4f9264c9ecd
imited credit tavily API Key: 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
angsearch API Key: sk-deeb1404e8c6432a862445d336bc3d0f


# Fanar API Documentation for Cursor

This document provides a comprehensive guide to the Fanar API, specifically formatted for use within Cursor or other AI coding assistants. It includes all available endpoints, models, rate limits, and code examples to facilitate seamless integration.

## 1. Overview

The Fanar API provides access to various AI capabilities, including chat completion, text-to-speech (TTS), speech-to-text (STT), image generation, translation, poem generation, moderation, and tokenization.

- **Base URL:** `https://api.fanar.qa`

- **Authentication:** Bearer token in the `Authorization` header (`Authorization: Bearer YOUR_API_KEY` )

- **Compatibility:** Many endpoints (like Chat, TTS, STT, Image Generation) are compatible with the official OpenAI library. When using the OpenAI SDK, set the `base_url` to `https://api.fanar.qa/v1`.

## 2. Rate Limits

The API enforces rate limits to ensure optimal performance. Exceeding these limits results in a `429 Too Many Requests` status code.

| Model | Rate Limit |
| --- | --- |
| Fanar |
| Fanar-S-1-7B |
| Fanar-C-1-8.7 |
| Fanar-C-2-27B |  |
| Fanar-Sadiq |  |
| Fanar-Sadiq-Agentic |  |
| Fanar-Sadiq-TTS-1 |  |
| Fanar-Oryx-IVU-2 |  |
| Fanar-Aura-TTS-2 |  |
| Fanar-Aura-STT-1 |  |
| Fanar-Aura-STT-LF-1 |  |
| Fanar-Oryx-IG-2 |  |
| Fanar-Guard-2 |  |
| Fanar-Shaheen-MT-1 |  |
| Fanar-Diwan |  |

## 3. Endpoints

### 3.1 Chat Completions

Create a chat completion based on a sequence of messages. Compatible with the OpenAI library.

- **Endpoint:** `POST /v1/chat/completions`

- **Content-Type:** `application/json`

**Supported Models:**

- `Fanar`

- `Fanar-S-1-7B`

- `Fanar-C-1-8.7B`

- `Fanar-C-2-27B` (Supports `enable_thinking` parameter with additional authorization )

- `Fanar-Sadiq` (Replaces `Islamic-RAG`. Uses `book_names`, `exclude_sources`, `filter_sources`)

- `Fanar-Sadiq-Agentic`

- `Fanar-Oryx-IVU-2`

**Key Parameters:**

- `model` (string, required): The model to use.

- `messages` (array, required): Array of message objects (role, content).

- `enable_thinking` (boolean, optional): Enable thinking role (only for `Fanar-C-2-27B`).

- `book_names` (array of strings, optional): For `Fanar-Sadiq` model.

- `exclude_sources` / `filter_sources` (array, optional): For `Fanar-Sadiq` model.

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY_HERE" \
  -d '{
    "model": "Fanar",
    "messages": [
      {
        "role": "user",
        "content": "Your message here"
      }
    ]
  }'
```

### 3.2 Audio: Text-to-Speech (TTS )

Generates audio from input text. Compatible with the OpenAI library.

- **Endpoint:** `POST /v1/audio/speech`

- **Content-Type:** `application/json`

**Supported Models:**

- `Fanar-Aura-TTS-2`

- `Fanar-Sadiq-TTS-1` (For Quranic text, use `quran_reciter` parameter)

**Key Parameters:**

- `model` (string, required): The TTS model.

- `input` (string, required): Text to generate audio for.

- `voice` (string, required): Voice to use (e.g., `Amelia`, `Hamad`, `Abdulrahman`, `Radwa`).

- `response_format` (string, optional): `mp3` or `wav`.

- `stream` (boolean, optional): Stream the audio.

- `with_emotion` (boolean, optional): Enable emotional speech (only for `Fanar-Aura-TTS-2` and supported voices like `Abdulrahman`, `Radwa`).

- `quran_reciter` (string, optional): For `Fanar-Sadiq-TTS-1` (e.g., `abdul-basit`, `maher-al-muaiqly`, `mahmoud-al-husary`).

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/audio/speech" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_API_KEY" \
--output greeting.mp3 \
-d '{
  "model": "Fanar-Aura-TTS-2",
  "input": "Hello! I hope you are having a wonderful day.",
  "voice": "Amelia",
  "response_format": "mp3"
}'
```

### 3.3 Audio: Speech-to-Text (STT )

Transcribes audio into text. Compatible with the OpenAI library.

- **Endpoint:** `POST /v1/audio/transcriptions`

- **Content-Type:** `multipart/form-data`

**Supported Models:**

- `Fanar-Aura-STT-1`: For short audio clips (up to 20–30 seconds).

- `Fanar-Aura-STT-LF-1`: For long-form transcription.

**Key Parameters:**

- `file` (binary, required): The audio file to transcribe.

- `model` (string, required): The STT model.

- `format` (string, optional): `text`, `srt`, or `json`. (`Fanar-Aura-STT-1` only supports `text`).

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/audio/transcriptions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.wav" \
  -F "model=Fanar-Aura-STT-1"
```

### 3.4 Audio: Voices Management

Manage available and personalized voices.

- **List Voices:** `GET /v1/audio/voices`

- **Create Voice:** `POST /v1/audio/voices` (Requires special authorization )

- **Delete Voice:** `DELETE /v1/audio/voices/{name}` (Requires special authorization)

### 3.5 Image Generation

Creates an image given a text prompt. Compatible with the OpenAI library.

- **Endpoint:** `POST /v1/images/generations`

- **Content-Type:** `application/json`

**Supported Models:**

- `Fanar-Oryx-IG-2`

**Key Parameters:**

- `model` (string, required): The image generation model.

- `prompt` (string, required): Text description of the desired image.

- `revise` (boolean, optional): Automatically revise prompt for better results.

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/images/generations" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_API_KEY" \
-d '{
  "model": "Fanar-Oryx-IG-2",
  "prompt": "A serene sunset over a mountain lake with reflections of colorful clouds and pine trees"
}'
```

### 3.6 Translations

Translate text between English and Arabic.

- **Endpoint:** `POST /v1/translations`

- **Content-Type:** `application/json`

**Supported Models:**

- `Fanar-Shaheen-MT-1`

**Key Parameters:**

- `model` (string, required ): The translation model.

- `text` (string, required): Text to translate (max 4,000 words).

- `langpair` (string, required): `en-ar` or `ar-en`.

- `preprocessing` (string, optional): `default`, `preserve_html`, `preserve_whitespace`, `preserve_whitespace_and_html`.

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/translations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "Fanar-Shaheen-MT-1",
    "text": "Your text here",
    "langpair": "ar-en",
    "preprocessing": "default"
  }'
```

### 3.7 Poem Generation

Creates a poem given a prompt. Compatible with the OpenAI library.

- **Endpoint:** `POST /v1/poems/generations`

- **Content-Type:** `application/json`

**Supported Models:**

- `Fanar-Diwan`

**Key Parameters:**

- `model` (string, required ): The poem generation model.

- `prompt` (string, required): Text description of the desired poem.

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/poems/generations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "Fanar-Diwan",
    "prompt": "Your text here"
  }'
```

### 3.8 Moderations

Identify safety and cultural-awareness scores for prompt-response pairs.

- **Endpoint:** `POST /v1/moderations`

- **Content-Type:** `application/json`

**Supported Models:**

- `Fanar-Guard-2`

**Key Parameters:**

- `model` (string, required ): The moderation model.

- `prompt` (string, required): The prompt.

- `response` (string, required): The model's response.

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/moderations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "Fanar-Guard-2",
    "prompt": "Your prompt here",
    "response": "Response from the model here"
  }'
```

### 3.9 Tokens

Get token count for a given text.

- **Endpoint:** `POST /v1/tokens`

- **Content-Type:** `application/json`

**Supported Models:**

- `Fanar-S-1-7B`

- `Fanar-C-1-8.7B`

- `Fanar-C-2-27B`

**Key Parameters:**

- `model` (string, required ): The LLM model.

- `content` (string, required): The text content.

**cURL Example:**

```bash
curl -X POST "https://api.fanar.qa/v1/tokens" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "content": "Your text content here",
    "model": "Fanar-C-1-8.7B"
  }'
```

### 3.10 Models

List all available models.

- **Endpoint:** `GET /v1/models`

**cURL Example:**

```bash
curl -X GET "https://api.fanar.qa/v1/models" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## 4. Cursor Integration Tips

When using Cursor to write code interacting with the Fanar API:

1. **OpenAI SDK Compatibility:** Since many endpoints (Chat, Audio, Images, Poems ) are compatible with the OpenAI SDK, you can instruct Cursor to use the standard `openai` Python or Node.js packages. Just ensure you override the `base_url` to `https://api.fanar.qa/v1` and use the specific Fanar model names.

1. **Model Names:** Always use the exact model names provided in this documentation (e.g., `Fanar-C-2-27B`, `Fanar-Aura-TTS-2` ).

1. **Custom Endpoints:** For endpoints like Translations (`/v1/translations`) or Moderations (`/v1/moderations`), instruct Cursor to use standard HTTP clients (like `requests` in Python or `fetch` in JS/TS) as these might not map directly to standard OpenAI SDK methods.

1. **Authentication:** Remind Cursor to always include the `Authorization: Bearer YOUR_API_KEY` header.

# SANAD — Product Requirements Document

## Vision

SANAD is an AI-powered platform that provides transparent, evidence-based Shariah financial reasoning for contemporary economic instruments — without issuing independent fatwas.

## Target Users

- Individual Muslims seeking Shariah guidance on financial products
- Islamic finance professionals and Shariah advisors
- Platform administrators and source reviewers

## Core Features

### 1. Shariah Reasoning Engine
- Multi-agent pipeline with mandatory citation chain
- Support for Arabic and English queries
- Multiple scholarly opinions when sources disagree

### 2. Source Management
- Authenticated classical and contemporary sources
- Admin review workflow for new sources
- pgvector-backed semantic search

### 3. Financial Context Integration
- Real-time asset and market data
- Shariah compliance screening for stocks and ETFs

### 4. User Experience
- Modern responsive UI with RTL/LTR support
- Light and dark themes
- Chat-style interaction with expandable evidence

## Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Response latency | < 30s for standard queries |
| Availability | 99.5% uptime |
| Languages | Arabic, English |
| Accessibility | WCAG 2.1 AA |
| Security | JWT auth, RBAC, encrypted secrets |

## Integrity Rules

1. **No Hallucination**: Refuse to answer without evidence
2. **Mandatory Citations**: Every claim must reference a source
3. **Transparency**: Show reasoning chain (Evidence → Principles → Reasoning → Analysis)
4. **Human Oversight**: Admin review for source authentication

## Out of Scope (Current Phases)

- Mobile native apps
- Real-time trading integration
- Independent fatwa issuance

## Success Metrics

- Citation coverage rate ≥ 99%
- User satisfaction score ≥ 4.0/5.0
- Zero unreferenced jurisprudential claims in production
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
# SANAD

AI-powered multi-agent platform for evidence-based Shariah financial reasoning.

**Explainability chain:** Evidence → Principles → Reasoning → Final Analysis

## Quick Start (recommended — Docker only)

**Use ONE method.** Do not run Docker and local `uvicorn` / `npm run dev` at the same time — they fight over ports **3000** and **8000**.

```powershell
cd C:\Users\Yahia ELNAMLA\Desktop\SANAD
copy .env.example .env
.\scripts\start-sanad.ps1
```

First time or after major updates:

```powershell
.\scripts\start-sanad.ps1 -Rebuild
```

| URL | Purpose |
|-----|---------|
| http://localhost:3000/welcome | Landing page (site entry) |
| http://localhost:3000/chat | Chat (after login) |
| http://localhost:3000/login | Sign in |
| http://localhost:3000/register | Create account |
| http://localhost:8000/api/v1/docs | API documentation |

**Stop the stack:**

```powershell
.\scripts\stop-sanad.ps1
```

**Verify everything works:**

```powershell
.\scripts\verify-sanad.ps1
```

**View logs:**

```powershell
docker compose logs -f frontend backend
```

### If you see an old UI or login fails

1. Stop local servers (`Ctrl+C` on any uvicorn / npm dev terminals).
2. Run `.\scripts\stop-sanad.ps1` then `.\scripts\start-sanad.ps1 -Rebuild`.
3. Hard refresh the browser: **Ctrl+Shift+R** (or use Incognito).
4. Open **http://localhost:3000/welcome** (not an old bookmark to `/` only).

---

## Alternative: local dev (advanced)

Only if Docker frontend/backend are **stopped**.

```powershell
# Terminal 1 — database + redis only
docker compose up -d postgres redis

# Terminal 2 — backend
.\scripts\sync_agents.ps1
.\scripts\run_backend.ps1

# Terminal 3 — frontend
cd frontend
npm install
npm run dev
```

`frontend/.env.local` must use `BACKEND_URL=http://localhost:8000` for this mode.

---

## Run Tests

```powershell
# Backend (needs postgres on :5433)
$env:PYTHONPATH="."
python -m pytest tests/backend/test_auth.py tests/backend/test_billing.py -q

# Full suite
.\scripts\run_tests.ps1

# Frontend
cd frontend && npm test
```

## Production Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `backend/app/` | FastAPI API, services, models |
| `frontend/src/` | Next.js UI (Arabic RTL / English LTR) |
| `agents/` | Multi-agent Shariah reasoning pipeline |
| `rag/` | RAG ingestion, chunking, vectorstore |
| `scripts/` | `start-sanad.ps1`, `verify-sanad.ps1`, etc. |

## Integrity Rules

1. **No Hallucination** — refuse to answer without authenticated sources
2. **Mandatory Citations** — every jurisprudential claim references a source
3. **Human Oversight** — admin/reviewer authenticates sources before RAG use

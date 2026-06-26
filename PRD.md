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

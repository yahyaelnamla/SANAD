# Archive Directory

This folder holds **non-runtime** artifacts moved out of the repository root to keep the hackathon submission clean.

## Policy

- Nothing here is imported by SANAD at runtime unless explicitly documented below.
- Do not delete without checking references across the repo first.
- Prefer `archive/` over deletion when uncertain.

## Contents

| Path | Description |
|------|-------------|
| `artifacts/` | Accidental empty files created at repo root (stray npm/docker CLI artifacts) |
| `vendored/` | Reserved for unused third-party trees if relocated from `backend/app/tools/` |

### artifacts/

| File | Origin |
|------|--------|
| `11.17.0` | Stray npm artifact |
| `next` | Stray npm artifact |
| `sanad-frontend@0.1.0` | Stray npm artifact |
| `[frontend` | Stray npm artifact |
| `docker` | Stray empty file (not the Docker config folder) |

## Active vendored dependency (NOT archived)

**Docling** remains at `backend/app/tools/docling-main/` because `backend/app/services/docling_extractor.py` imports it for optional local PDF text extraction before Fanar-Oryx-IVU.

## Unused vendored copies (still in tree)

| Path | Status |
|------|--------|
| `backend/app/tools/FlagEmbedding-master/` | Not imported — SANAD uses Fanar embeddings API |
| `backend/app/tools/Qwen3-Embedding-main/` | Not imported |

SANAD embeddings: `rag/embeddings/fanar_embedding_model.py` → Fanar API.

## Optional cleanup (manual)

Judges cloning this repo may exclude large folders via sparse checkout:

- `backend/app/tools/docling-main/`
- `backend/app/tools/FlagEmbedding-master/`
- `backend/app/tools/Qwen3-Embedding-main/`

## Archived documentation

Superseded markdown moved to [docs/archive/](../docs/archive/) — see that README for the index.

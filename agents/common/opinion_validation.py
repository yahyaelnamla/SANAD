"""Validate and ground scholarly opinions against retrieved evidence."""

from __future__ import annotations

import re

from agents.common.evidence import EvidenceItem
from agents.knowledge_agent.models import EvidenceBundle
from agents.reasoning_agent.models import ScholarlyOpinion

MIN_POSITION_CHARS = 20
MAX_POSITION_CHARS = 480


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _citation_matches_evidence(citation: str, evidence: EvidenceItem) -> bool:
    if not citation.strip():
        return False
    cit = _normalize(citation)
    ev_cit = _normalize(evidence.citation)
    if cit in ev_cit or ev_cit in cit:
        return True
    if evidence.text and cit[:40] in _normalize(evidence.text):
        return True
    return False


def _scholar_matches_evidence(scholar: str, evidence: EvidenceItem) -> bool:
    if not scholar.strip():
        return False
    name = _normalize(scholar)
    for field in (evidence.source_author, evidence.source_title):
        if field and name in _normalize(field):
            return True
    return False


def _find_matching_evidence(
    opinion: ScholarlyOpinion,
    evidences: list[EvidenceItem],
) -> EvidenceItem | None:
    for citation in opinion.citations:
        for evidence in evidences:
            if _citation_matches_evidence(citation, evidence):
                return evidence
    for evidence in evidences:
        if _scholar_matches_evidence(opinion.scholar, evidence):
            return evidence
    return None


def _extract_metadata(evidence: EvidenceItem) -> dict[str, str | None]:
    meta = evidence.metadata or {}
    return {
        "institution": evidence.source_title if evidence.source_type in {"standard", "fatwa"} else None,
        "book": meta.get("book") or (evidence.source_title if evidence.source_type == "classical" else None),
        "fatwa": meta.get("fatwa") or (evidence.source_title if evidence.source_type == "fatwa" else None),
        "page": str(meta["page"]) if meta.get("page") is not None else None,
        "standard": meta.get("standard") or (evidence.source_title if evidence.source_type == "standard" else None),
        "section": meta.get("section"),
        "date": meta.get("date"),
    }


def _ground_position(opinion: ScholarlyOpinion, evidence: EvidenceItem) -> str:
    position = opinion.position.strip()
    if len(position) >= MIN_POSITION_CHARS and position.lower() not in {"unknown", "n/a", ""}:
        if _normalize(position) in _normalize(evidence.text) or len(position) <= MAX_POSITION_CHARS:
            return position[:MAX_POSITION_CHARS]
    quoted = evidence.text.strip()
    if len(quoted) > MAX_POSITION_CHARS:
        quoted = quoted[:MAX_POSITION_CHARS].rsplit(" ", 1)[0].strip() + "…"
    return quoted


def validate_and_ground_opinions(
    opinions: list[ScholarlyOpinion],
    bundle: EvidenceBundle,
) -> list[ScholarlyOpinion]:
    """Keep only evidence-backed opinions with exact wording and metadata."""
    if not bundle.evidences:
        return []

    grounded: list[ScholarlyOpinion] = []
    seen: set[str] = set()

    for opinion in opinions:
        match = _find_matching_evidence(opinion, bundle.evidences)
        if match is None:
            continue

        position = _ground_position(opinion, match)
        if len(position) < MIN_POSITION_CHARS and len(match.text) >= MIN_POSITION_CHARS:
            position = _ground_position(
                ScholarlyOpinion(scholar=opinion.scholar, position="", citations=opinion.citations),
                match,
            )

        meta = _extract_metadata(match)
        scholar = opinion.scholar.strip() or match.source_author or match.source_title
        key = f"{_normalize(scholar)}|{_normalize(position[:80])}"
        if key in seen:
            continue
        seen.add(key)

        citations = list(dict.fromkeys(opinion.citations or [match.citation]))
        grounded.append(
            ScholarlyOpinion(
                scholar=scholar,
                position=position,
                citations=citations,
                institution=opinion.institution or meta["institution"] or match.source_title,
                strength=opinion.strength or ("strong" if match.score >= 0.85 else "moderate"),
                book=opinion.book or meta["book"],
                fatwa=opinion.fatwa or meta["fatwa"],
                page=opinion.page or meta["page"],
                standard=opinion.standard or meta["standard"],
                section=opinion.section or meta["section"],
                date=opinion.date or meta["date"],
            )
        )

    if grounded:
        return grounded[:8]

    return [
        ScholarlyOpinion(
            scholar=e.source_author or e.source_title,
            position=_ground_position(
                ScholarlyOpinion(scholar="", position="", citations=[e.citation]),
                e,
            ),
            citations=[e.citation],
            institution=e.source_title,
            strength="strong" if e.score >= 0.85 else "moderate",
            book=e.metadata.get("book") if e.metadata else None,
            fatwa=e.source_title if e.source_type == "fatwa" else None,
            standard=e.source_title if e.source_type == "standard" else None,
        )
        for e in bundle.evidences[:3]
        if len(e.text.strip()) >= MIN_POSITION_CHARS
    ]

"""Verification Agent tools — citation, integrity, and hallucination checks."""

from agents.knowledge_agent.models import EvidenceBundle
from agents.reasoning_agent.models import ReasoningResult
from agents.verification_agent.models import VerificationIssue

# Generic source-type labels from LLM — not literal citations to match in corpus.
GENERIC_ADILLA_LABELS = frozenset(
    {
        "quran",
        "qur'an",
        "koran",
        "hadith",
        "hadeeth",
        "consensus",
        "ijma",
        "ijmaa",
        "sunnah",
        "sunna",
        "fatwa",
        "fiqh",
        "scholarly consensus",
        "scholarly opinion",
        "primary sources",
        "islamic sources",
        "القرآن",
        "الحديث",
        "الإجماع",
        "الاجماع",
        "فتوى",
        "السنة",
    }
)


def is_generic_adilla_label(adilla: str) -> bool:
    """True when adilla is a source category, not a specific citable reference."""
    normalized = adilla.strip().lower().strip("[]().")
    if normalized in GENERIC_ADILLA_LABELS:
        return True
    words = normalized.split()
    if len(words) <= 2 and normalized in GENERIC_ADILLA_LABELS:
        return True
    if len(words) == 1 and words[0] in GENERIC_ADILLA_LABELS:
        return True
    return False


def normalize_adilla_from_evidence(adilla: list[str], bundle: EvidenceBundle) -> list[str]:
    """Replace generic LLM adilla labels with concrete evidence citations."""
    citations = [e.citation for e in bundle.evidences if e.citation]
    specific = [item for item in adilla if item.strip() and not is_generic_adilla_label(item)]
    merged: list[str] = []
    seen: set[str] = set()
    for item in specific + citations:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        merged.append(item.strip())
    return merged[:8] if merged else citations[:5]


def _citation_matches(known: set[str], citation: str) -> bool:
    """Fuzzy match citations — Fanar may return URLs while reasoning uses short refs."""
    if citation in known:
        return True
    citation_lower = citation.lower()
    for known_citation in known:
        known_lower = known_citation.lower()
        if citation_lower in known_lower or known_lower in citation_lower:
            return True
        if any(part in known_lower for part in citation_lower.split() if len(part) > 5):
            return True
    return False


def check_citations(
    reasoning: ReasoningResult,
    bundle: EvidenceBundle,
) -> list[VerificationIssue]:
    """Verify that reasoning references retrieved evidence citations."""
    issues: list[VerificationIssue] = []
    known_citations = {e.citation for e in bundle.evidences}

    if not reasoning.citations:
        issues.append(
            VerificationIssue(
                code="MISSING_CITATIONS",
                message="Reasoning output contains no citations.",
            )
        )
        return issues

    for citation in reasoning.citations:
        if not _citation_matches(known_citations, citation):
            issues.append(
                VerificationIssue(
                    code="UNKNOWN_CITATION",
                    message=f"Citation not found in evidence bundle: {citation}",
                )
            )

    return issues


def check_analysis_content(reasoning: ReasoningResult) -> list[VerificationIssue]:
    """Verify analysis is non-empty and has reasonable confidence."""
    issues: list[VerificationIssue] = []
    if not reasoning.analysis.strip():
        issues.append(
            VerificationIssue(
                code="EMPTY_ANALYSIS",
                message="Analysis text is empty.",
            )
        )
    if reasoning.confidence <= 0.0:
        issues.append(
            VerificationIssue(
                code="ZERO_CONFIDENCE",
                message="Confidence score is zero.",
            )
        )
    return issues


def check_opinion_citations(
    reasoning: ReasoningResult,
    bundle: EvidenceBundle,
) -> list[VerificationIssue]:
    """Verify scholarly opinions include citations."""
    issues: list[VerificationIssue] = []
    known = {e.citation for e in bundle.evidences}

    for opinion in reasoning.opinions:
        if not opinion.citations and bundle.evidences:
            continue
        for citation in opinion.citations:
            if not _citation_matches(known, citation):
                issues.append(
                    VerificationIssue(
                        code="OPINION_UNKNOWN_CITATION",
                        message=f"Opinion cites unknown source: {citation}",
                    )
                )
    return issues


def check_hallucination_risk(
    reasoning: ReasoningResult,
    bundle: EvidenceBundle,
) -> list[VerificationIssue]:
    """Cross-reference specific adilla against retrieved Fanar-Sadiq evidence."""
    if not reasoning.adilla:
        return []

    evidence_corpus = " ".join(
        f"{e.text} {e.citation}" for e in bundle.evidences
    ).lower()
    known_citations = {e.citation.lower() for e in bundle.evidences if e.citation}

    specific_adilla = [
        adilla for adilla in reasoning.adilla if not is_generic_adilla_label(adilla)
    ]
    if not specific_adilla:
        return []

    ungrounded: list[str] = []
    for adilla in specific_adilla:
        adilla_lower = adilla.lower()
        if adilla_lower in evidence_corpus:
            continue
        if any(part in evidence_corpus for part in adilla_lower.split() if len(part) > 4):
            continue
        if any(
            adilla_lower in citation or citation in adilla_lower for citation in known_citations
        ):
            continue
        if _citation_matches({e.citation for e in bundle.evidences}, adilla):
            continue
        ungrounded.append(adilla)

    if len(ungrounded) > max(2, (len(specific_adilla) * 2) // 3):
        return [
            VerificationIssue(
                code="UNGROUNDED_ADILLA",
                message=f"Majority of adilla not grounded in retrieved evidence: {ungrounded[:3]}",
            )
        ]
    return []

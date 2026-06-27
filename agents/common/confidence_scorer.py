"""Compute evidence-grounded confidence scores for SANAD responses."""

from typing import Any

from agents.knowledge_agent.models import EvidenceBundle
from agents.reasoning_agent.models import ReasoningResult
from agents.verification_agent.models import VerificationResult
from agents.verification_agent.tools import is_generic_adilla_label


def _grounding_ratio(reasoning: ReasoningResult, bundle: EvidenceBundle) -> float:
    if not reasoning.adilla or not bundle.evidences:
        return 0.5 if reasoning.analysis.strip() else 0.0

    corpus = " ".join(f"{e.text} {e.citation}" for e in bundle.evidences).lower()
    specific = [a for a in reasoning.adilla if not is_generic_adilla_label(a)]
    if not specific:
        return 0.85 if bundle.evidences else 0.5

    grounded = 0
    for adilla in specific:
        adilla_lower = adilla.lower()
        if adilla_lower in corpus:
            grounded += 1
            continue
        if any(part in corpus for part in adilla_lower.split() if len(part) > 4):
            grounded += 1

    return grounded / len(specific)


def compute_confidence(
    bundle: EvidenceBundle,
    reasoning: ReasoningResult,
    verification: VerificationResult | None = None,
    *,
    guard_scores: dict[str, Any] | None = None,
) -> tuple[float, dict[str, float]]:
    """Return final confidence (0–1) and factor breakdown."""
    evidences = bundle.evidences
    retrieval_score = (
        sum(e.score for e in evidences) / len(evidences) if evidences else 0.0
    )
    retrieval_score = min(max(retrieval_score, 0.0), 1.0)

    grounding = _grounding_ratio(reasoning, bundle)
    model_confidence = min(max(float(reasoning.confidence or 0.0), 0.0), 1.0)

    guard_safety = float((guard_scores or {}).get("safety", 1.0))
    guard_cultural = float((guard_scores or {}).get("cultural_awareness", 1.0))
    guard_factor = min(max((guard_safety + guard_cultural) / 2, 0.0), 1.0)

    verification_factor = 1.0
    if verification and not verification.approved:
        verification_factor = 0.35
    elif verification and verification.issues:
        verification_factor = max(0.5, 1.0 - 0.1 * len(verification.issues))

    opinion_factor = 1.0
    if reasoning.opinions:
        cited = sum(1 for o in reasoning.opinions if o.citations)
        opinion_factor = cited / len(reasoning.opinions)

    # Weighted blend — retrieval and grounding dominate for "real" confidence
    final = (
        retrieval_score * 0.30
        + grounding * 0.25
        + model_confidence * 0.15
        + guard_factor * 0.15
        + verification_factor * 0.10
        + opinion_factor * 0.05
    )
    final = min(max(final, 0.0), 1.0)

    breakdown = {
        "retrieval": round(retrieval_score, 3),
        "grounding": round(grounding, 3),
        "model": round(model_confidence, 3),
        "guard": round(guard_factor, 3),
        "verification": round(verification_factor, 3),
        "scholarly_coverage": round(opinion_factor, 3),
    }
    return round(final, 3), breakdown

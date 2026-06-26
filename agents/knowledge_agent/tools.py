"""Knowledge Agent tools for evidence validation and principle extraction."""

from agents.common.evidence import EvidenceItem
from agents.knowledge_agent.models import JurisprudentialPrinciple

PRINCIPLE_KEYWORDS: dict[str, tuple[str, str]] = {
    "riba": (
        "Prohibition of Riba",
        "Any guaranteed increase on a loan or debt is categorically prohibited.",
    ),
    "gharar": (
        "Prohibition of Gharar",
        "Excessive uncertainty in contracts invalidates transactions.",
    ),
    "maysir": (
        "Prohibition of Maysir",
        "Gambling and speculation of pure chance are prohibited.",
    ),
}


def is_valid_evidence(item: EvidenceItem) -> bool:
    """Reject chunks without valid source metadata or citation."""
    if not item.citation or not item.citation.strip():
        return False
    if not item.source_id or not item.chunk_id:
        return False
    if not item.text.strip():
        return False
    metadata = item.metadata or {}
    if metadata.get("is_authenticated") is False:
        return False
    return True


def infer_principles(evidences: list[EvidenceItem], entities: list[str]) -> list[JurisprudentialPrinciple]:
    """Infer applicable fiqh principles from entities and evidence text."""
    combined = " ".join(e.text.lower() for e in evidences) + " " + " ".join(entities)
    principles: list[JurisprudentialPrinciple] = []
    seen: set[str] = set()

    for key, (name, description) in PRINCIPLE_KEYWORDS.items():
        if key in combined and name not in seen:
            citation = next((e.citation for e in evidences if key in e.text.lower()), "Retrieved evidence")
            principles.append(
                JurisprudentialPrinciple(name=name, description=description, citation=citation)
            )
            seen.add(name)

    return principles

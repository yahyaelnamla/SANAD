"""Intent Agent tools for entity and language detection."""

import re

from agents.intent_agent.models import IntentType

ARABIC_PATTERN = re.compile(r"[\u0600-\u06ff]")

FINANCIAL_ENTITIES: dict[str, list[str]] = {
    "riba": ["riba", "usury", "interest", "ربا", "فائدة"],
    "crypto": ["crypto", "bitcoin", "ethereum", "عملة رقمية", "بيتكوين"],
    "stock": ["stock", "share", "equity", "سهم", "أسهم"],
    "etf": ["etf", "fund", "صندوق"],
    "sukuk": ["sukuk", "bond", "صكوك"],
    "mortgage": ["mortgage", "loan", "قرض", "رهن"],
}


def detect_language(text: str) -> str:
    """Detect Arabic or English from query text."""
    arabic_chars = len(ARABIC_PATTERN.findall(text))
    return "ar" if arabic_chars > len(text.replace(" ", "")) * 0.3 else "en"


def extract_entities(text: str) -> list[str]:
    """Extract financial/jurisprudential entities via keyword matching."""
    lowered = text.lower()
    found: list[str] = []
    for entity, keywords in FINANCIAL_ENTITIES.items():
        if any(kw in lowered for kw in keywords):
            found.append(entity)
    return found or ["general_inquiry"]


def classify_intent(text: str, entities: list[str]) -> IntentType:
    """Rule-based intent classification."""
    lowered = text.lower()
    if any(w in lowered for w in ("halal", "haram", "permissible", "prohibited", "حلال", "حرام")):
        return IntentType.SHARIAH_RULING
    if any(w in lowered for w in ("compliance", "screen", "shariah compliant", "متوافق")):
        return IntentType.COMPLIANCE_SCREENING
    if any(w in lowered for w in ("opinion", "madhab", "view", "رأي", "مذهب")):
        return IntentType.COMPARATIVE_OPINION
    if any(w in lowered for w in ("what is", "define", "ما هو", "تعريف")):
        return IntentType.DEFINITION
    if entities and entities[0] != "general_inquiry":
        return IntentType.SHARIAH_RULING
    return IntentType.GENERAL_INQUIRY


def extract_keywords(text: str) -> list[str]:
    """Extract significant keywords from the query."""
    words = re.findall(r"[\w\u0600-\u06ff]+", text.lower())
    stopwords = {"is", "the", "a", "an", "in", "of", "what", "هل", "ما", "في"}
    return [w for w in words if w not in stopwords and len(w) > 2][:10]

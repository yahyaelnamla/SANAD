"""Islamic finance topic detection and retrieval query enrichment."""

from __future__ import annotations

import re

from agents.intent_agent.models import IntentResult

TOPIC_ENRICHMENTS: dict[str, tuple[str, ...]] = {
    "stocks": ("AAOIFI equity screening", "Shariah stock", "permissible business activity"),
    "crypto": ("cryptocurrency halal", "Bitcoin", "digital assets fiqh"),
    "defi": ("DeFi", "staking", "yield farming Islamic finance"),
    "nft": ("NFT", "non-fungible token", "digital collectibles"),
    "etf": ("ETF", "exchange traded fund", "Shariah ETF"),
    "sukuk": ("Sukuk", "Islamic bond", "ijara sukuk"),
    "murabaha": ("Murabaha", "cost-plus sale", "Islamic financing"),
    "takaful": ("Takaful", "Islamic insurance", "cooperative insurance"),
    "banking": ("Islamic banking", "riba-free banking", "Shariah banking"),
    "riba": ("riba prohibition", "usury", "interest haram"),
    "zakat": ("Zakat", "nisab", "purification wealth"),
    "inheritance": ("Islamic inheritance", "faraid", "mirath"),
    "economics": ("Islamic economics", "maqasid", "maslahah"),
    "aaofi": ("AAOIFI standard", "Shariah screening ratio"),
    "fatwa": ("contemporary fatwa", "scholarly opinion", "fiqh academy"),
    "disagreement": ("scholarly disagreement", "ikhtilaf", "madhhab difference"),
}

TOPIC_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (key, re.compile("|".join(re.escape(token) for token in _tokens), re.I))
    for key, _tokens in TOPIC_ENRICHMENTS.items()
]


def detect_islamic_finance_topics(text: str) -> list[str]:
    """Return matched Islamic finance topic keys from user text."""
    if not text.strip():
        return []
    matched: list[str] = []
    for key, pattern in TOPIC_PATTERNS:
        if pattern.search(text):
            matched.append(key)
    return matched


def enrich_retrieval_query(intent: IntentResult) -> str:
    """Append domain-specific retrieval terms for Islamic finance specialization."""
    base = " ".join(dict.fromkeys([intent.raw_query, *intent.keywords[:5], *intent.entities[:4]]))
    topics = detect_islamic_finance_topics(base)
    if intent.domain and intent.domain not in {"general", "unknown"}:
        topics.append(intent.domain.replace("_", " "))

    extras: list[str] = []
    for topic in topics[:4]:
        extras.extend(TOPIC_ENRICHMENTS.get(topic, (topic.replace("_", " "),))[:2])

    if not extras:
        extras.append("Islamic finance Shariah")

    merged = " ".join(dict.fromkeys([base, *extras]))
    return merged[:480]

"""Financial Context Agent — live financial data enrichment."""

from agents.financial_context_agent.models import FinancialContext
from agents.financial_context_agent.tools import build_live_context
from agents.intent_agent.models import IntentResult


class FinancialContextAgent:
    """Enrich queries with live financial product and market context."""

    async def enrich(self, intent: IntentResult) -> FinancialContext:
        """Build financial context from entities and live market APIs."""
        return await build_live_context(intent.entities, intent.raw_query)

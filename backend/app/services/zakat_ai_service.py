"""Fanar-powered Zakat guidance for the calculator."""

from __future__ import annotations

import logging
import os

from agents.common.fanar_client import FanarLLMClient
from backend.app.services.fanar_model_router import model_for_task
from backend.app.services.output_guard_service import OutputGuardService

logger = logging.getLogger(__name__)


async def generate_zakat_guidance(
    *,
    net_wealth: float,
    zakat_due: float,
    output_currency: str,
    is_above_nisab: bool,
    asset_summary: str,
    language: str = "en",
) -> str | None:
    """Return concise scholarly Zakat guidance via Fanar-Sadiq."""
    api_key = os.getenv("FANAR_API_KEY", "")
    if not api_key:
        return None

    lang_label = "Arabic" if language == "ar" else "English"
    client = FanarLLMClient(api_key=api_key)
    model = model_for_task("summary", depth="fast")

    prompt = (
        f"Net zakatable wealth: {net_wealth:,.2f} {output_currency}. "
        f"Zakat due: {zakat_due:,.2f} {output_currency}. "
        f"Above nisab: {is_above_nisab}. Assets: {asset_summary}. "
        "Give 2-3 practical bullet points on Zakat obligations (hawl, nisab, purification). "
        "Do not invent fatwas. Keep under 120 words."
    )

    try:
        text = await client.complete(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are SANAD's Islamic finance assistant. Respond in {lang_label}. "
                        "Be concise, accurate, and cite general fiqh principles only."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=220,
        )
        cleaned = text.strip()
        if not cleaned:
            return None
        guard = OutputGuardService(client)
        passes, reason, _ = await guard.guard_output(prompt=prompt, response=cleaned)
        if not passes:
            logger.warning("Zakat guidance rejected by Fanar-Guard-2: %s", reason)
            return None
        return cleaned
    except RuntimeError as exc:
        logger.warning("Zakat AI guidance failed: %s", exc)
        return None

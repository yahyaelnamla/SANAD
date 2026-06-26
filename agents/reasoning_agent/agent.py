"""Reasoning Agent — Takyeef Fiqhi jurisprudential analysis."""

import os
from pathlib import Path

from backend.app.services.conversation_memory_service import format_history_for_prompt
from config.fanar_api_keys import FANAR_MODELS
from agents.common.fanar_client import FanarLLMClient
from agents.financial_context_agent.models import FinancialContext
from agents.intent_agent.models import IntentResult
from agents.knowledge_agent.models import EvidenceBundle
from agents.reasoning_agent.models import MadhhabPosition, ReasoningResult, ScholarlyOpinion
from agents.common.opinion_validation import validate_and_ground_opinions
from agents.reasoning_agent.tools import (
    build_analysis_from_payload,
    format_evidence_for_prompt,
    is_mostly_english,
    normalize_citations,
    normalize_string_list,
    parse_reasoning_json,
)
from agents.response_builder.tools import sanitize_user_text
from agents.verification_agent.tools import normalize_adilla_from_evidence

PROMPT_PATH = Path(__file__).parent / "prompt.md"

REASONING_MAX_TOKENS = {
    "fast": int(os.getenv("REASONING_MAX_TOKENS_FAST", "8000")),
    "standard": int(os.getenv("REASONING_MAX_TOKENS_STANDARD", "16000")),
    "deep": int(os.getenv("REASONING_MAX_TOKENS_DEEP", "32000")),
}


class ReasoningAgent:
    """Perform evidence-backed jurisprudential reasoning via Fanar-C-2-27B."""

    def __init__(self, llm_client: FanarLLMClient | None = None) -> None:
        self.llm = llm_client or FanarLLMClient()
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
        self.model = FANAR_MODELS["reasoning"]

    async def analyze(
        self,
        bundle: EvidenceBundle,
        financial_context: FinancialContext,
        intent: IntentResult,
        *,
        model: str | None = None,
        depth: str = "deep",
        evidence_listing: bool = False,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> ReasoningResult:
        """Perform Takyeef Fiqhi analysis on the evidence bundle."""
        if not bundle.has_valid_evidence:
            return ReasoningResult(
                analysis="Insufficient authenticated evidence to perform jurisprudential analysis.",
                confidence=0.0,
            )

        used_model = model or self.model
        evidence_text = format_evidence_for_prompt(bundle)
        context_text = ", ".join(p.name for p in financial_context.products) or "N/A"
        language = intent.language if intent.language in {"ar", "en"} else "ar"
        language_rule = (
            "اكتب جميع حقول النص (analysis و reasoning_steps و opinions) بالعربية الفصحى فقط. "
            "ممنوع استخدام الإنجليزية في أي حقل. "
            "استخدم التفكير المتسلسل (Chain-of-Thought) بالعربية داخلياً قبل إخراج JSON: "
            "تعريف المسألة → الأدلة → القواعد الفقهية → آراء العلماء → التكييف الفقهي."
            if language == "ar"
            else "Write all text fields (analysis, reasoning_steps, opinions) in English only."
        )

        if depth == "standard":
            max_tokens = REASONING_MAX_TOKENS["standard"]
            depth_instruction = (
                "Mode: STANDARD (concise).\n"
                "Write a clear direct answer in 3–6 short paragraphs.\n"
                + (
                    "Use section labels when helpful (تعريف، الحكم الشرعي).\n"
                    if language == "ar"
                    else "Use section labels when helpful (Definition, Ruling).\n"
                )
                + "Do NOT include inline citation numbers like [1] or (1).\n"
                "Do NOT include a madhhab comparison matrix.\n"
                "Provide a complete answer — do not truncate or cut short."
            )
        elif depth == "fast":
            max_tokens = REASONING_MAX_TOKENS["fast"]
            depth_instruction = (
                "Mode: FAST (brief).\n"
                "Answer in 2–4 short paragraphs only.\n"
                "No inline citation numbers. No scholarly matrix.\n"
                "Still provide a complete, readable answer."
            )
        elif language == "ar":
            max_tokens = REASONING_MAX_TOKENS["deep"]
            depth_instruction = (
                "Mode: ADVANCED (comprehensive).\n"
                "Provide deep Takyeef Fiqhi with detailed evidence discussion, "
                "scholarly opinions (aqwal al-fuqaha), and madhhab matrix where relevant.\n"
                "Integrate financial context when applicable.\n"
                "Use clear Arabic section labels on their own lines: من الكتاب، من السنة، من الإجماع، من كلام العلماء.\n"
                "Use bullet points (•) under each section for verses, hadith, and scholar quotes.\n"
                "Do NOT include inline citation numbers like [1] — sources are shown separately.\n"
                "Write flowing paragraphs suitable for RTL Arabic reading.\n"
                "The analysis field must be a complete Arabic answer (longer than standard mode)."
            )
        else:
            max_tokens = REASONING_MAX_TOKENS["deep"]
            depth_instruction = (
                "Mode: ADVANCED (comprehensive).\n"
                "Provide deep jurisprudential analysis with detailed evidence discussion, "
                "scholarly opinions, and madhhab comparison where relevant.\n"
                "Integrate financial context when applicable.\n"
                "Use clear English section labels: Definition, Evidence, Ruling, Scholarly views.\n"
                "Do NOT include inline citation numbers like [1] — sources are shown separately.\n"
                "Write flowing paragraphs in English only."
            )

        if evidence_listing:
            depth_instruction += (
                "\n\nSPECIAL MODE: The user asks to list ALL evidence from the prior answer. "
                "Do NOT change the topic or add unrelated rulings. "
                + (
                    "Organize under: من الكتاب، من السنة، من الإجماع، من كلام العلماء with bullet points for every verse, hadith, and scholar quote."
                    if language == "ar"
                    else "Organize under: From the Quran, From the Sunnah, From consensus, From scholars with bullet points."
                )
            )

        history_block = ""
        if conversation_history and len(conversation_history) >= 2:
            history_block = (
                "\n\nConversation history (answer relative to this thread — do NOT change topic):\n"
                f"{format_history_for_prompt(conversation_history)}\n"
                f"Current user message: {intent.raw_query}\n"
            )

        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": (
                    f"Language: {language}\n"
                    f"{language_rule}\n"
                    f"{depth_instruction}\n"
                    f"Query: {intent.raw_query}\n"
                    f"{history_block}"
                    f"Financial context: {context_text}\n"
                    f"Evidence and principles:\n{evidence_text}\n"
                    "Perform Takyeef Fiqhi with qawaid_fiqhiyya, adilla, and aqwal al-fuqaha.\n"
                    "Respond with valid JSON only. Do not include markdown fences or English planning text."
                ),
            },
        ]

        result = await self._complete_reasoning_json(
            messages,
            primary_model=used_model,
            fallback_model=FANAR_MODELS["generation_ar"],
            max_tokens=max_tokens,
            depth=depth,
        )

        qawaid = normalize_string_list(
            result.get("qawaid_fiqhiyya") or result.get("principles_applied")
        )
        if not qawaid:
            qawaid = [p.name for p in bundle.principles]

        reasoning_steps = normalize_string_list(result.get("reasoning_steps"))
        adilla = normalize_adilla_from_evidence(
            normalize_string_list(result.get("adilla")),
            bundle,
        )

        raw_opinions = [
            ScholarlyOpinion(
                scholar=o.get("scholar", "Unknown"),
                position=o.get("position", ""),
                citations=normalize_citations(o.get("citations"))
                or [e.citation for e in bundle.evidences[:1]],
                institution=o.get("institution"),
                strength=o.get("strength"),
                book=o.get("book"),
                fatwa=o.get("fatwa"),
                page=str(o.get("page")) if o.get("page") is not None else None,
                standard=o.get("standard"),
                section=o.get("section"),
                date=o.get("date"),
            )
            for o in result.get("opinions", [])
            if isinstance(o, dict) and o.get("position")
        ]
        opinions = validate_and_ground_opinions(raw_opinions, bundle)
        madhhab_matrix = [
            MadhhabPosition(
                school=m.get("school", m.get("madhhab", "Unknown")),
                position=m.get("position", ""),
                alignment=m.get("alignment", "mixed"),
                source=m.get("source") or m.get("citation"),
            )
            for m in (result.get("madhhab_matrix") or result.get("madhhab_positions") or [])
            if isinstance(m, dict) and m.get("position")
        ]
        if not opinions and bundle.evidences:
            opinions = validate_and_ground_opinions([], bundle)

        confidence = float(result.get("confidence", 0.0))
        if confidence <= 0.0 and bundle.evidences:
            avg_score = sum(e.score for e in bundle.evidences) / len(bundle.evidences)
            confidence = min(max(avg_score * 0.85, 0.45), 0.88)

        analysis = build_analysis_from_payload(result, language=language)
        analysis = sanitize_user_text(analysis)
        if not analysis or (language == "ar" and is_mostly_english(analysis)):
            analysis = await self._fallback_analysis(
                bundle,
                intent,
                language=language,
                depth=depth,
            )

        return ReasoningResult(
            principles_applied=qawaid,
            qawaid_fiqhiyya=qawaid,
            adilla=adilla,
            reasoning_steps=reasoning_steps,
            thinking_trace=result.get("_thinking_trace"),
            analysis=analysis,
            opinions=opinions,
            madhhab_matrix=madhhab_matrix,
            confidence=confidence,
            citations=[e.citation for e in bundle.evidences],
            active_model=used_model,
        )

    async def _complete_reasoning_json(
        self,
        messages: list[dict[str, str]],
        *,
        primary_model: str,
        fallback_model: str,
        max_tokens: int,
        depth: str = "standard",
    ) -> dict:
        """Request structured JSON; fall back to Arabic generator if parsing fails."""
        use_thinking = depth == "deep" and primary_model == FANAR_MODELS["reasoning"]

        if use_thinking:
            try:
                thinking, raw = await self.llm.complete_with_thinking(
                    model=primary_model,
                    messages=messages,
                    max_tokens=max_tokens,
                )
                parsed = parse_reasoning_json(raw)
                if parsed.get("analysis") or parsed.get("reasoning_steps"):
                    parsed["_thinking_trace"] = thinking
                    return parsed
            except RuntimeError:
                pass

        for model in (primary_model, fallback_model):
            try:
                payload = await self.llm.complete_json(
                    model=model,
                    messages=messages,
                    enable_thinking=False,
                    max_tokens=max_tokens,
                )
                if isinstance(payload, dict) and (
                    payload.get("analysis") or payload.get("reasoning_steps")
                ):
                    return payload
            except (RuntimeError, ValueError, TypeError):
                continue
            try:
                raw = await self.llm.complete(
                    model=model,
                    messages=[
                        *messages,
                        {
                            "role": "user",
                            "content": "Return valid JSON only with analysis and reasoning_steps.",
                        },
                    ],
                    max_tokens=max_tokens,
                    enable_thinking=False,
                )
                parsed = parse_reasoning_json(raw)
                if parsed.get("analysis") or parsed.get("reasoning_steps"):
                    return parsed
            except RuntimeError:
                continue
        return {"analysis": "", "confidence": 0.0}

    async def _fallback_analysis(
        self,
        bundle: EvidenceBundle,
        intent: IntentResult,
        *,
        language: str,
        depth: str,
    ) -> str:
        """Generate a clean prose answer when structured JSON analysis is unusable."""
        evidence_text = format_evidence_for_prompt(bundle)
        depth_hint = (
            "قدّم إجابة متقدمة مفصلة بفقرات واضحة بالعربية."
            if depth == "deep" and language == "ar"
            else "Provide a comprehensive advanced answer in clear paragraphs."
            if depth == "deep"
            else "قدّم إجابة مختصرة واضحة بالعربية."
            if language == "ar"
            else "Provide a concise clear answer."
        )
        try:
            text = await self.llm.complete(
                model=FANAR_MODELS["generation_ar"],
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are SANAD, an Islamic finance assistant. "
                            "Answer only from the supplied evidence. "
                            "Never show JSON, thinking, or English when the user language is Arabic."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Language: {language}\n"
                            f"{depth_hint}\n"
                            f"Question: {intent.raw_query}\n"
                            f"Evidence:\n{evidence_text}\n"
                            "Write the final user-facing answer only."
                        ),
                    },
                ],
                max_tokens=REASONING_MAX_TOKENS.get(depth, REASONING_MAX_TOKENS["standard"]),
                enable_thinking=False,
            )
            cleaned = sanitize_user_text(text)
            if cleaned and not (language == "ar" and is_mostly_english(cleaned)):
                return cleaned
        except RuntimeError:
            pass

        lead = bundle.evidences[0].text if bundle.evidences else ""
        if language == "ar":
            return sanitize_user_text(
                f"تعذّر توليد إجابة كاملة من النموذج. يرجى إعادة طرح السؤال.\n\n"
                f"مرجع من الأدلة:\n{lead[:600]}"
            )
        return sanitize_user_text(
            f"Unable to generate a complete model answer. Please try again.\n\n"
            f"Evidence excerpt:\n{lead[:600]}"
        )

"""Conversation memory — multi-turn context merge, session recall, and follow-up resolution."""

from __future__ import annotations

import os
import re
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from agents.common.evidence import EvidenceItem
from agents.common.fanar_client import FanarLLMClient
from backend.app.repositories.query_repository import QueryRepository
from backend.app.repositories.response_repository import ResponseRepository
from backend.app.services.fanar_model_router import model_for_task
from backend.app.services.translation_service import detect_language

MAX_HISTORY_TURNS = 30
MAX_TURN_CHARS = int(os.getenv("MAX_TURN_CHARS", "100000"))
MAX_PROMPT_HISTORY_CHARS = int(os.getenv("MAX_PROMPT_HISTORY_CHARS", "200000"))

FOLLOW_UP_PATTERNS = (
    r"^(why|how|what if|what about|and what|tell me more|explain|elaborate|continue|same|also)\b",
    r"^(لماذا|كيف|ماذا لو|وماذا|و\b|اشرح|تابع|وضح|فسر|نفس|ايضاً|أيضاً|كذلك)\b",
    r"^(yes|no|ok|sure|thanks|thank you)\b",
)

CONTEXT_REFERENCE_PATTERNS = (
    r"ادل(?:ت|ة|ك|اك|نا|ئك|ائك)",
    r"أدل(?:ت|ة|ك|اك|نا|ئك|ائك)",
    r"دل(?:يل|يلك|ائ|الة|ائل)",
    r"ال(?:سؤال|اجابة|إجابة|جواب|موضوع)\s*(?:ال)?(?:سابق|قبل|السابق|الأول|اول)",
    r"إجابت(?:ك|كما|ك|ي)",
    r"جواب(?:ك|كما)",
    r"ما\s+(?:ذكرت|قلت|أجبت|اجبت)",
    r"your\s+(?:evidence|sources|answer|previous)",
    r"(?:previous|prior|last|earlier)\s+(?:question|answer|response)",
    r"what\s+(?:evidence|sources)\s+did\s+you",
    r"give\s+me\s+(?:all|the)\s+(?:evidence|sources|verses|hadith)",
    r"\b(?:this|that|these|those|it|they|them|same)\b",
    r"\b(?:هذا|هذه|ذلك|تلك|هؤلاء|نفس(?:ه|ها|هم)?)\b",
    r"(?:second|third|first|1st|2nd|3rd)\s+(?:point|evidence|criterion|criteri(?:on|a)|ruling|argument)",
    r"(?:ال(?:نقطة|دليل|معيار|حكم))\s*(?:ال)?(?:اول|أول|ثاني|ثالث|رابع)",
    r"you\s+(?:said|mentioned|concluded|ruled)",
    r"(?:the\s+)?(?:company|ruling|conclusion|analysis)\s+you\s+mentioned",
)

EVIDENCE_FOLLOWUP_PATTERNS = (
    r"ادل",
    r"أدل",
    r"دليل",
    r"دلائل",
    r"آيات",
    r"ايات",
    r"أحاديث",
    r"احاديث",
    r"evidence",
    r"sources?",
    r"verses?",
    r"hadith",
)

SHORT_FOLLOW_UP_MAX_WORDS = 12


def is_follow_up_question(question: str) -> bool:
    """Detect short contextual follow-ups that need prior conversation."""
    text = question.strip()
    if not text:
        return False
    words = re.findall(r"[\w\u0600-\u06ff]+", text)
    if len(words) > SHORT_FOLLOW_UP_MAX_WORDS:
        return False
    lowered = text.lower()
    if any(re.search(pattern, lowered) for pattern in FOLLOW_UP_PATTERNS):
        return True
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in CONTEXT_REFERENCE_PATTERNS):
        return True
    if text.endswith("?") and len(words) <= 6:
        return True
    if len(words) <= 3:
        return True
    return False


def is_contextual_reference(question: str) -> bool:
    """Detect references to prior turns (including evidence requests)."""
    text = question.strip()
    if not text:
        return False
    if is_follow_up_question(question):
        return True
    lowered = text.lower()
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in CONTEXT_REFERENCE_PATTERNS):
        return True
    if any(re.search(pattern, lowered) for pattern in EVIDENCE_FOLLOWUP_PATTERNS):
        if re.search(r"(?:سابق|قبل|your|previous|إجاب|جواب|answer|said|ذكرت|قلت)", text, re.I):
            return True
        if re.search(r"(?:كل|all|اعط|أعط|give|list|show)", text, re.I):
            return True
    return False


def is_evidence_followup(question: str) -> bool:
    """User asks to list or expand evidence from the prior answer."""
    text = question.strip()
    if not is_contextual_reference(text):
        return False
    lowered = text.lower()
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in EVIDENCE_FOLLOWUP_PATTERNS) or any(
        re.search(pattern, lowered) for pattern in ("evidence", "sources", "verses", "hadith", "آيات", "أحاديث")
    )


def _turn_signature(turn: dict[str, str]) -> str:
    role = turn.get("role", "")
    content = (turn.get("content") or "").strip()
    return f"{role}:{content[:240]}"


def merge_conversation_histories(
    session_turns: list[dict[str, str]],
    client_turns: list[dict[str, str]] | None,
) -> list[dict[str, str]]:
    """Merge DB session recall with client-side history without duplicating turns."""
    client = [_normalize_turn(turn) for turn in (client_turns or []) if turn.get("content", "").strip()]
    db = [_normalize_turn(turn) for turn in session_turns if turn.get("content", "").strip()]

    if not db:
        # Never trust browser-only history when the server has no session for this user.
        return []
    if not client:
        return db[-MAX_HISTORY_TURNS:]

    if len(client) >= len(db):
        return client[-MAX_HISTORY_TURNS:]

    missing = len(db) - len(client)
    merged = db[:missing] + client
    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for turn in merged:
        signature = _turn_signature(turn)
        if signature in seen:
            continue
        seen.add(signature)
        deduped.append(turn)
    return deduped[-MAX_HISTORY_TURNS:]


def _normalize_turn(turn: dict[str, str]) -> dict[str, str]:
    content = (turn.get("content") or "").strip()
    if len(content) > MAX_TURN_CHARS:
        content = content[:MAX_TURN_CHARS]
    role = turn.get("role", "user")
    if role not in {"user", "assistant"}:
        role = "user"
    return {"role": role, "content": content}


def format_history_for_prompt(
    history: list[dict[str, str]],
    *,
    max_chars: int = MAX_PROMPT_HISTORY_CHARS,
) -> str:
    """Serialize prior turns for injection into agent prompts."""
    if not history:
        return ""

    lines: list[str] = []
    used = 0
    for turn in history[-MAX_HISTORY_TURNS:]:
        role = turn.get("role", "user")
        content = (turn.get("content") or "").strip()
        if not content:
            continue
        label = "User" if role == "user" else "Assistant"
        block = f"{label}: {content}"
        if used + len(block) > max_chars:
            remaining = max_chars - used
            if remaining > 120:
                lines.append(block[:remaining] + "…")
            break
        lines.append(block)
        used += len(block) + 1
    return "\n\n".join(lines)


def _format_history_turns(history: list[dict[str, str]], *, limit: int = 16) -> str:
    return format_history_for_prompt(history[-limit:])


def resolve_query_with_context(
    question: str,
    conversation_history: list[dict[str, str]] | None,
) -> str:
    """Expand follow-up questions using recent conversation turns (rule-based)."""
    if not conversation_history:
        return question

    history_text = _format_history_turns(conversation_history)
    if not history_text:
        return question

    last_assistant = next(
        (t.get("content", "") for t in reversed(conversation_history) if t.get("role") == "assistant"),
        "",
    )

    if is_evidence_followup(question):
        if detect_language(question) == "ar":
            return (
                "المستخدم يطلب عرض جميع الأدلة (آيات قرآنية، أحاديث، أقوال العلماء) من الإجابة السابقة. "
                "لا تُدخل موضوعاً جديداً. أعد تنظيم كل دليل موثّق من الإجابة السابقة تحت عناوين: "
                "من الكتاب، من السنة، من الإجماع، من كلام العلماء.\n\n"
                f"{last_assistant[:6000]}\n\n"
                f"طلب المستخدم: {question.strip()}"
            )
        return (
            f"The user asks for ALL evidence (Quran verses, Hadith, scholarly quotes) from the prior answer. "
            f"Do NOT introduce new unrelated topics. Reproduce and organize every authenticated proof from:\n\n"
            f"{last_assistant[:6000]}\n\n"
            f"User request: {question.strip()}"
        )

    if detect_language(question) == "ar":
        return (
            f"متابعة في نفس المحادثة.\n"
            f"السياق السابق:\n{history_text}\n\n"
            f"سؤال المتابعة: {question.strip()}"
        )

    return (
        f"Follow-up in the same conversation thread.\n"
        f"Prior context:\n{history_text}\n\n"
        f"Follow-up question: {question.strip()}"
    )


async def expand_follow_up_with_llm(
    llm: FanarLLMClient,
    question: str,
    conversation_history: list[dict[str, str]],
) -> str:
    """Use Fanar-Sadiq to rewrite contextual questions into standalone retrieval queries."""
    if len(conversation_history) < 2:
        return question

    history_text = _format_history_turns(conversation_history)
    last_assistant = next(
        (t.get("content", "") for t in reversed(conversation_history) if t.get("role") == "assistant"),
        "",
    )
    model = model_for_task("follow_up")
    user_lang = detect_language(question)

    system = (
        "You rewrite the user's latest message into ONE standalone Islamic finance / fiqh question "
        "that preserves the conversation topic and all implicit references (this, that, the company, "
        "the second evidence, the previous ruling, etc.). "
        "If the user asks for evidence, verses, hadith, or sources from the prior answer, rewrite as a "
        "request to list ALL proofs from the prior answer about the same topic. "
        f"Output only the rewritten question in {'Arabic' if user_lang == 'ar' else 'English'}."
    )
    if is_evidence_followup(question):
        system += " The user wants every proof from the previous assistant answer — do not change the topic."

    try:
        rewritten = await llm.complete_without_fallback(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": (
                        f"Conversation:\n{history_text}\n\n"
                        f"Last assistant answer excerpt:\n{last_assistant[:4000]}\n\n"
                        f"User message: {question}"
                    ),
                },
            ],
            temperature=0.1,
            max_tokens=500,
        )
        cleaned = rewritten.strip().strip('"').strip("'")
        if cleaned and len(cleaned) >= 8:
            return cleaned
    except RuntimeError:
        pass

    return resolve_query_with_context(question, conversation_history)


def _build_assistant_turn_content(response: Any) -> str:
    parts: list[str] = []
    if response.summary:
        parts.append(str(response.summary).strip())
    if response.reasoning:
        reasoning = str(response.reasoning).strip()
        if reasoning and reasoning not in (parts[0] if parts else ""):
            parts.append(reasoning[:4000])
    if response.evidence:
        cites = []
        for item in response.evidence[:15]:
            if isinstance(item, dict):
                cites.append(
                    f"- {item.get('citation', '')}: {(item.get('text') or '')[:220]}"
                )
        if cites:
            parts.append("[Evidence used]\n" + "\n".join(cites))
    if response.opinions:
        opinions = []
        for item in response.opinions[:8]:
            if isinstance(item, dict) and item.get("position"):
                scholar = item.get("scholar", "Scholar")
                opinions.append(f"- {scholar}: {item.get('position', '')[:180]}")
        if opinions:
            parts.append("[Scholarly views]\n" + "\n".join(opinions))
    content = "\n\n".join(parts).strip()
    return content[:MAX_TURN_CHARS] if content else ""


async def fetch_session_context(
    session: AsyncSession,
    user_id: uuid.UUID,
    session_id: str | None,
    *,
    limit: int = 20,
) -> list[dict[str, str]]:
    """Load Q&A pairs from the same chat session in chronological order."""
    if not session_id:
        return []

    query_repo = QueryRepository(session)
    response_repo = ResponseRepository(session)
    queries = await query_repo.list_by_session_chronological(user_id, session_id, limit=limit)

    turns: list[dict[str, str]] = []
    for query in queries:
        turns.append({"role": "user", "content": query.question[:MAX_TURN_CHARS]})
        response = await response_repo.get_by_query_id(query.id)
        if response:
            content = _build_assistant_turn_content(response)
            if content:
                turns.append({"role": "assistant", "content": content})
    return turns


async def fetch_prior_session_evidence(
    session: AsyncSession,
    user_id: uuid.UUID,
    session_id: str | None,
) -> list[EvidenceItem]:
    """Return evidence chunks from the most recent completed turn in this session."""
    if not session_id:
        return []

    query_repo = QueryRepository(session)
    response_repo = ResponseRepository(session)
    queries = await query_repo.list_by_session(user_id, session_id, limit=1)
    if not queries:
        return []

    response = await response_repo.get_by_query_id(queries[0].id)
    if not response or not response.evidence:
        return []

    items: list[EvidenceItem] = []
    for raw in response.evidence:
        if isinstance(raw, dict):
            try:
                items.append(EvidenceItem(**raw))
            except (TypeError, ValueError):
                continue
    return items


async def build_effective_query(
    session: AsyncSession,
    user_id: uuid.UUID,
    question: str,
    *,
    session_id: str | None = None,
    conversation_history: list[dict[str, str]] | None = None,
    llm: FanarLLMClient | None = None,
) -> tuple[str, dict[str, Any]]:
    """Merge histories and prepare retrieval hints while preserving the original user question."""
    memory_meta: dict[str, Any] = {
        "conversation_memory_used": False,
        "merged_history": [],
        "retrieval_query": question,
    }

    session_turns = await fetch_session_context(session, user_id, session_id)
    history = merge_conversation_histories(session_turns, conversation_history)

    if not history:
        return question, memory_meta

    memory_meta["conversation_memory_used"] = True
    memory_meta["merged_history"] = history
    memory_meta["history_turns"] = len(history)

    if is_evidence_followup(question):
        memory_meta["reuse_prior_evidence"] = True
        prior = await fetch_prior_session_evidence(session, user_id, session_id)
        if prior:
            memory_meta["prior_evidence_chunks"] = prior

    prior_exchange = len(history) >= 2
    needs_retrieval_hint = prior_exchange and (
        is_contextual_reference(question) or is_follow_up_question(question)
    )

    if needs_retrieval_hint:
        if llm:
            retrieval_query = await expand_follow_up_with_llm(llm, question, history)
        else:
            retrieval_query = resolve_query_with_context(question, history)
        if retrieval_query.strip() and retrieval_query.strip() != question.strip():
            memory_meta["retrieval_query"] = retrieval_query.strip()
            memory_meta["expanded_follow_up"] = True

    return question, memory_meta

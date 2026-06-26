"""Reasoning Agent tools for evidence-backed Takyeef Fiqhi analysis."""

import json
import re

from agents.common.fanar_client import split_thinking_content
from agents.knowledge_agent.models import EvidenceBundle
from agents.response_builder.tools import sanitize_user_text

_PLANNING_LINE = re.compile(
    r"^(?:The user|The question|Let me|I need to|First,|Next,|Now,|For adilla|"
    r"These form|Moving to|I should|I will|Double-check|Specifically,|Also,|"
    r"Make sure|Reviewing|Starting by|Based on the provided).*$",
    re.MULTILINE | re.IGNORECASE,
)
_JSON_FENCE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


def normalize_string_list(items: list | None) -> list[str]:
    """Coerce LLM list output into plain strings."""
    if not items:
        return []
    normalized: list[str] = []
    for item in items:
        if isinstance(item, str):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(
                item.get("reference")
                or item.get("citation")
                or item.get("text")
                or json.dumps(item, ensure_ascii=False)
            )
        else:
            normalized.append(str(item))
    return normalized


def normalize_citations(raw: object | None) -> list[str]:
    """Coerce Fanar opinion citations into a string list."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return normalize_string_list(raw)
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list) and parsed and all(isinstance(x, str) for x in parsed):
                    return normalize_string_list(parsed)
            except json.JSONDecodeError:
                pass
            return [text]
        return [text]
    return [str(raw)]


def format_evidence_for_prompt(bundle: EvidenceBundle) -> str:
    """Format evidence bundle for LLM prompt."""
    lines = []
    for i, evidence in enumerate(bundle.evidences, 1):
        lines.append(f"[{i}] {evidence.citation}\n{evidence.text}")
    for principle in bundle.principles:
        lines.append(
            f"Principle: {principle.name} — {principle.description} ({principle.citation})"
        )
    return "\n\n".join(lines)


def is_mostly_english(text: str) -> bool:
    """Heuristic: is text predominantly Latin-script prose."""
    alpha = [char for char in text if char.isalpha()]
    if len(alpha) < 12:
        return False
    latin = sum(1 for char in alpha if char.isascii())
    return latin / len(alpha) > 0.65


def strip_planning_prose(text: str) -> str:
    """Remove English chain-of-thought planning lines from model output."""
    cleaned = _PLANNING_LINE.sub("", text)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_json_object(text: str) -> dict | None:
    """Extract the outermost JSON object from noisy model output."""
    stripped = text.strip()
    fence = _JSON_FENCE.search(stripped)
    if fence:
        stripped = fence.group(1).strip()

    if stripped.startswith("{"):
        try:
            payload = json.loads(stripped)
            return payload if isinstance(payload, dict) else None
        except json.JSONDecodeError:
            pass

    start = stripped.find("{")
    if start < 0:
        return None

    depth = 0
    in_string = False
    escape = False
    for index, char in enumerate(stripped[start:], start=start):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = stripped[start : index + 1]
                try:
                    payload = json.loads(candidate)
                    return payload if isinstance(payload, dict) else None
                except json.JSONDecodeError:
                    return None
    return None


def extract_analysis_field(text: str) -> str | None:
    """Best-effort extraction of analysis from malformed JSON text."""
    match = re.search(
        r'"analysis"\s*:\s*"((?:\\.|[^"\\])*)"',
        text,
        re.DOTALL,
    )
    if not match:
        match = re.search(
            r'"analysis"\s*:\s*"([\s\S]*?)"\s*[,}]',
            text,
        )
    if not match:
        return None
    try:
        return json.loads(f'"{match.group(1)}"')
    except json.JSONDecodeError:
        return match.group(1).replace("\\n", "\n").replace('\\"', '"').strip() or None


def build_analysis_from_payload(result: dict, *, language: str) -> str:
    """Build user-facing analysis text from structured reasoning JSON."""
    analysis_raw = result.get("analysis")
    if isinstance(analysis_raw, str) and analysis_raw.strip():
        cleaned = sanitize_user_text(analysis_raw)
        if cleaned and not (language == "ar" and is_mostly_english(cleaned)):
            return cleaned

    steps = normalize_string_list(result.get("reasoning_steps"))
    opinions = result.get("opinions") or []
    sections: list[str] = []

    if language == "ar":
        if steps:
            sections.append("**الأدلة والاستدلال:**\n" + "\n".join(f"• {step}" for step in steps[:6]))
        opinion_lines: list[str] = []
        for item in opinions[:4]:
            if not isinstance(item, dict):
                continue
            position = str(item.get("position", "")).strip()
            scholar = str(item.get("scholar", "")).strip()
            if position:
                opinion_lines.append(f"• {scholar}: {position}" if scholar else f"• {position}")
        if opinion_lines:
            sections.append("**آراء العلماء:**\n" + "\n".join(opinion_lines))
    else:
        if steps:
            sections.append("**Evidence and reasoning:**\n" + "\n".join(f"• {step}" for step in steps[:6]))
        opinion_lines = []
        for item in opinions[:4]:
            if not isinstance(item, dict):
                continue
            position = str(item.get("position", "")).strip()
            scholar = str(item.get("scholar", "")).strip()
            if position:
                opinion_lines.append(f"• {scholar}: {position}" if scholar else f"• {position}")
        if opinion_lines:
            sections.append("**Scholarly views:**\n" + "\n".join(opinion_lines))

    if sections:
        return "\n\n".join(sections)

    fallback = sanitize_user_text(str(analysis_raw or ""))
    if fallback and not (language == "ar" and is_mostly_english(fallback)):
        return fallback
    return ""


def parse_reasoning_json(raw: str) -> dict:
    """Extract JSON payload from reasoning output (after thinking tags)."""
    _, content = split_thinking_content(raw)
    text = strip_planning_prose(content.strip())

    payload = extract_json_object(text)
    if payload:
        return payload

    analysis = extract_analysis_field(text)
    if analysis:
        return {"analysis": analysis, "confidence": 0.75}

    cleaned = sanitize_user_text(text)
    if cleaned and not is_mostly_english(cleaned):
        return {"analysis": cleaned, "confidence": 0.75}

    return {"analysis": "", "confidence": 0.75}


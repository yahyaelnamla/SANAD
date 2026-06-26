"""Live Fanar API client for chat, moderation, and Islamic RAG retrieval."""

import asyncio
import base64
import hashlib
import json
import logging
import re
from typing import Any

import httpx

from agents.common.source_classifier import classify_evidence_kind, enrich_citation_label
from config.fanar_api_keys import (
    FANAR_API_BASE_URL,
    FANAR_GUARD_MIN_CULTURAL,
    FANAR_GUARD_MIN_SAFETY,
    FANAR_MODELS,
    FANAR_ORGANIZATION,
    get_fanar_api_key,
)

logger = logging.getLogger(__name__)

# Fanar-Guard requires a non-empty response field; empty string causes HTTP 500.
_INPUT_GUARD_PLACEHOLDER = (
    "No assistant response yet. Screen only the user prompt for safety and "
    "cultural appropriateness in an Islamic finance context."
)


def _is_mostly_english(text: str) -> bool:
    """Heuristic: is text predominantly Latin-script prose."""
    alpha = [char for char in text if char.isalpha()]
    if len(alpha) < 12:
        return False
    latin = sum(1 for char in alpha if char.isascii())
    return latin / len(alpha) > 0.65


def split_thinking_content(raw: str) -> tuple[str | None, str]:
    """Parse <thinking> tags from model output (handles unclosed tags)."""
    match = re.search(
        r"<(?:thinking|redacted_thinking)>(.*?)</(?:thinking|redacted_thinking)>",
        raw,
        re.DOTALL | re.IGNORECASE,
    )
    if match:
        thinking = match.group(1).strip()
        remainder = re.sub(
            r"<(?:thinking|redacted_thinking)>.*?</(?:thinking|redacted_thinking)>",
            "",
            raw,
            flags=re.DOTALL | re.IGNORECASE,
        ).strip()
        return thinking, remainder

    unclosed = re.search(
        r"<(?:thinking|redacted_thinking)>([\s\S]*)$",
        raw,
        re.IGNORECASE,
    )
    if unclosed:
        return unclosed.group(1).strip(), ""

    if _is_mostly_english(raw[:400]) and "{" in raw:
        json_start = raw.find("{")
        return raw[:json_start].strip() or None, raw[json_start:].strip()

    return None, raw.strip()


def prepare_text_for_speech(text: str) -> str:
    """Strip markdown and UI artifacts so TTS reads the answer accurately."""
    cleaned = text.strip()
    cleaned = re.sub(r"```[\s\S]*?```", " ", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"#{1,6}\s*", "", cleaned)
    cleaned = re.sub(r"━+", " ", cleaned)
    cleaned = re.sub(r"\[(\d+)\]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def detect_speech_language(text: str, hint: str = "ar") -> str:
    """Pick ar/en TTS voice from script content."""
    arabic = len(re.findall(r"[\u0600-\u06FF]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if arabic > latin:
        return "ar"
    if latin > 0:
        return "en"
    return hint if hint in {"ar", "en"} else "ar"


class FanarLLMClient:
    """Async client for Fanar v1 endpoints with retry and structured helpers."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        organization: str | None = None,
        max_retries: int = 3,
        timeout: float = 120.0,
    ) -> None:
        self.api_key = api_key or get_fanar_api_key()
        if not self.api_key:
            raise ValueError(
                "FanarLLMClient: FANAR_API_KEY is not set. "
                "Set the environment variable or pass api_key= explicitly."
            )
        self.base_url = (base_url or FANAR_API_BASE_URL).rstrip("/")
        self.organization = organization or FANAR_ORGANIZATION
        self.max_retries = max_retries
        self.timeout = timeout
        self._pending_tokens = 0
        self._total_tokens = 0
        self._http_client: httpx.AsyncClient | None = None
        self._lock: asyncio.Lock = asyncio.Lock()

    def _client(self) -> httpx.AsyncClient:
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=self.timeout)
        return self._http_client

    async def _get_client(self) -> httpx.AsyncClient:
        async with self._lock:
            return self._client()

    async def close(self) -> None:
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None

    def consume_tokens_since_last(self) -> int | None:
        """Return tokens used since the last consume call."""
        tokens = self._pending_tokens
        self._pending_tokens = 0
        return tokens if tokens else None

    @property
    def total_tokens(self) -> int:
        """Cumulative token count for this client instance."""
        return self._total_tokens

    def _record_usage(self, data: dict[str, Any]) -> None:
        usage = data.get("usage") or {}
        total = usage.get("total_tokens")
        if total is None:
            prompt = int(usage.get("prompt_tokens") or 0)
            completion = int(usage.get("completion_tokens") or 0)
            total = prompt + completion if (prompt or completion) else 0
        if total:
            self._pending_tokens += int(total)
            self._total_tokens += int(total)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-Fanar-Key": self.api_key,
            "X-Organization": self.organization,
            "Content-Type": "application/json",
        }

    async def complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        response_format: dict[str, str] | None = None,
        enable_thinking: bool = False,
        max_tokens: int | None = None,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """Generate a text completion from Fanar chat/completions."""
        fallback = FANAR_MODELS["generation_ar"]
        try:
            return await self._complete_once(
                model=model,
                messages=messages,
                temperature=temperature,
                response_format=response_format,
                enable_thinking=enable_thinking,
                max_tokens=max_tokens,
                extra=extra,
            )
        except RuntimeError as exc:
            if model == fallback:
                raise
            logger.warning("Falling back from %s to %s: %s", model, fallback, exc)
            return await self._complete_once(
                model=fallback,
                messages=messages,
                temperature=temperature,
                response_format=None,
                enable_thinking=False,
                max_tokens=max_tokens,
                extra=extra,
            )

    async def complete_without_fallback(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int | None = None,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """Chat completion without falling back to Fanar-Sadiq (used for translation)."""
        return await self._complete_once(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format=None,
            enable_thinking=False,
            max_tokens=max_tokens,
            extra=extra,
        )

    async def _complete_once(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float,
        response_format: dict[str, str] | None,
        enable_thinking: bool,
        max_tokens: int | None,
        extra: dict[str, Any] | None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if response_format:
            payload["response_format"] = response_format
        if enable_thinking:
            payload["enable_thinking"] = True
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if extra:
            payload.update(extra)

        data = await self._post("/chat/completions", payload)
        self._record_usage(data)
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("Fanar API returned no choices")

        content = choices[0].get("message", {}).get("content")
        if not isinstance(content, str):
            raise ValueError("Invalid completion payload from Fanar API")
        return content

    async def complete_json(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        enable_thinking: bool = False,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Return parsed JSON from a Fanar completion."""
        try:
            raw = await self.complete(
                model=model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
                enable_thinking=enable_thinking,
                max_tokens=max_tokens,
            )
        except RuntimeError as exc:
            logger.debug("complete_json primary call failed (%s); retrying with fallback.", exc)
            raw = await self.complete(
                model=FANAR_MODELS["generation_ar"],
                messages=[
                    *messages,
                    {
                        "role": "user",
                        "content": "Respond with valid JSON only, no markdown fences.",
                    },
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
        return self._parse_json(raw)

    async def complete_with_thinking(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4000,
    ) -> tuple[str | None, str]:
        """Return (thinking_trace, final_content) using native selective reasoning."""
        try:
            raw = await self.complete(
                model=model,
                messages=messages,
                temperature=temperature,
                enable_thinking=True,
                max_tokens=max_tokens,
            )
        except RuntimeError:
            try:
                raw = await self.complete(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    enable_thinking=False,
                    max_tokens=max_tokens,
                )
            except RuntimeError:
                raw = await self.complete(
                    model=FANAR_MODELS["generation_ar"],
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
        return split_thinking_content(raw)

    async def moderate_input(self, *, user_query: str) -> dict[str, Any]:
        """Screen user input with FanarGuard before pipeline execution."""
        return await self.moderate(prompt=user_query, response=_INPUT_GUARD_PLACEHOLDER)

    async def moderate(self, *, prompt: str, response: str) -> dict[str, Any]:
        """Run FanarGuard safety and cultural alignment check with retry; fail closed."""
        payload = {
            "model": FANAR_MODELS["guard"],
            "prompt": prompt,
            "response": response,
        }
        last_exc: RuntimeError | None = None
        for attempt in range(self.max_retries):
            try:
                return await self._post("/moderations", payload)
            except RuntimeError as exc:
                last_exc = exc
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)
        logger.error(
            "FanarGuard unavailable after %s retries — failing closed: %s",
            self.max_retries,
            last_exc,
        )
        return {
            "safety": 0.0,
            "cultural_awareness": 0.0,
            "guard_unavailable": True,
        }

    def passes_guard(self, moderation: dict[str, Any]) -> tuple[bool, str | None]:
        """Evaluate FanarGuard scores against configured thresholds."""
        if moderation.get("guard_unavailable"):
            return False, (
                "FanarGuard moderation service is temporarily unavailable. "
                "Please try again shortly."
            )
        safety = float(moderation.get("safety", 0.0))
        cultural = float(moderation.get("cultural_awareness", 0.0))
        if safety < FANAR_GUARD_MIN_SAFETY:
            return False, f"FanarGuard safety score too low ({safety:.2f})."
        if cultural < FANAR_GUARD_MIN_CULTURAL:
            return (
                False,
                "Response failed FanarGuard cultural alignment check "
                f"(score {cultural:.2f}).",
            )
        return True, None

    async def retrieve_knowledge(
        self,
        query: str,
        *,
        language: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve grounded Islamic content via Fanar-Sadiq with full source texts."""
        lang_hint = "Arabic" if language == "ar" else "English"
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Fanar-Sadiq Islamic knowledge retrieval. "
                    "Return ONLY authenticated, evidence-grounded excerpts. "
                    "For Quran: include the FULL verse text plus Surah name and Ayah number. "
                    "For Hadith: include the FULL matn (text), narrator, collection, and grade. "
                    "For Fatwa: include the scholar or body name and the FULL ruling excerpt. "
                    "Never respond with bare reference numbers like [1] or [2] alone. "
                    f"Respond in {lang_hint}."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Retrieve up to {top_k} distinct authenticated Islamic evidences for:\n{query}\n"
                    "Each excerpt must be self-contained and citable."
                ),
            },
        ]
        data = await self._post(
            "/chat/completions",
            {
                "model": FANAR_MODELS["rag"],
                "messages": messages,
                "max_tokens": 4000,
                "islamic_content_only": True,
            },
        )
        self._record_usage(data)
        message = data.get("choices", [{}])[0].get("message", {})
        references = message.get("references") or []
        content = message.get("content") or ""

        evidences: list[dict[str, Any]] = []
        for ref in references[:top_k]:
            text = (ref.get("content") or ref.get("text") or "").strip()
            if not text:
                continue
            source = ref.get("source") or ref.get("title") or "Fanar-Sadiq"
            ref_num = ref.get("number")
            kind = classify_evidence_kind(text, str(source))
            citation = enrich_citation_label(kind, f"{source} [{ref_num}]" if ref_num else source, text)
            verification_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
            source_url = source if isinstance(source, str) and source.startswith("http") else None
            evidences.append(
                {
                    "text": text,
                    "citation": citation,
                    "source_title": source if not source.startswith("http") else "Fanar-Sadiq Reference",
                    "source_author": ref.get("author") or ref.get("scholar") or source,
                    "source_type": kind,
                    "language": language or "ar",
                    "score": float(ref.get("score", 0.92)),
                    "metadata": {
                        "source_url": source_url,
                        "verification_hash": verification_hash,
                        "fanar_reference_number": ref_num,
                        "evidence_kind": kind,
                    },
                }
            )

        if not evidences and content.strip():
            kind = classify_evidence_kind(content)
            verification_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            evidences.append(
                {
                    "text": content,
                    "citation": enrich_citation_label(kind, "Fanar-Sadiq Knowledge Base", content),
                    "source_title": "Fanar-Sadiq",
                    "source_author": "Fanar-Sadiq",
                    "source_type": kind,
                    "language": language or "ar",
                    "score": 0.85,
                    "metadata": {
                        "source_url": "https://fanar.qa",
                        "verification_hash": verification_hash,
                        "evidence_kind": kind,
                    },
                }
            )
        return evidences

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        *,
        filename: str = "recording.webm",
        language: str | None = None,
    ) -> str:
        """Transcribe audio via Fanar-Aura-STT."""
        files = {"file": (filename, audio_bytes, "audio/webm")}
        data: dict[str, str] = {"model": FANAR_MODELS["stt"]}
        if language:
            data["language"] = "ar" if language == "ar" else "en"

        url = f"{self.base_url}/audio/transcriptions"
        client = await self._get_client()
        response = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "X-Fanar-Key": self.api_key,
                "X-Organization": self.organization,
            },
            files=files,
            data=data,
        )
        if response.status_code in {401, 403, 404, 422}:
            raise RuntimeError(f"Fanar STT HTTP {response.status_code}: {response.text[:300]}")
        response.raise_for_status()
        payload = response.json()
        text = payload.get("text") or payload.get("transcript") or ""
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Fanar STT returned empty transcription")
        return text.strip()

    async def translate_text(
        self,
        text: str,
        *,
        target_language: str = "en",
        source_language: str | None = None,
    ) -> str:
        """Translate text using Fanar-Shaheen via /v1/translations."""
        if source_language and target_language == source_language:
            return text
        src = source_language or ("ar" if target_language == "en" else "en")
        extended_langs = {"ar", "en", "fr", "ur", "tr", "ms"}
        if src not in extended_langs or target_language not in extended_langs:
            logger.warning(
                "translate_text: unsupported lang pair %s→%s, falling back to ar→en",
                src,
                target_language,
            )
            src, target_language = "ar", "en"
        if src == target_language:
            return text
        if src in {"ar", "en"} and target_language in {"ar", "en"}:
            langpair = f"{src}-{target_language}"
            try:
                data = await self._post(
                    "/translations",
                    {
                        "model": FANAR_MODELS["translation"],
                        "text": text,
                        "langpair": langpair,
                        "preprocessing": "default",
                    },
                )
                translated = data.get("text")
                if isinstance(translated, str) and translated.strip():
                    return translated.strip()
            except RuntimeError as exc:
                logger.warning("Fanar translations API failed, falling back to chat: %s", exc)

        lang_names = {
            "ar": "Arabic",
            "en": "English",
            "fr": "French",
            "ur": "Urdu",
            "tr": "Turkish",
            "ms": "Malay",
        }
        target = lang_names.get(target_language, target_language)
        source_hint = lang_names.get(src, src)
        messages = [
            {
                "role": "system",
                "content": (
                    f"Translate the user text to {target}. "
                    "Preserve Islamic terminology and citation markers accurately. "
                    "Output translation only."
                ),
            },
            {"role": "user", "content": f"From {source_hint}: {text}"},
        ]
        return await self.complete(
            model=FANAR_MODELS["translation"],
            messages=messages,
            temperature=0.1,
        )

    async def translate_for_display(
        self,
        text: str,
        *,
        target_language: str = "en",
        source_language: str | None = None,
    ) -> str:
        """Translate UI text — prefer Fanar-Shaheen REST, then chat without Sadiq fallback."""
        if source_language and target_language == source_language:
            return text
        src = source_language or detect_speech_language(text, "ar")
        if src == target_language:
            return text

        if src in {"ar", "en"} and target_language in {"ar", "en"}:
            langpair = f"{src}-{target_language}"
            try:
                data = await self._post(
                    "/translations",
                    {
                        "model": FANAR_MODELS["translation"],
                        "text": text,
                        "langpair": langpair,
                        "preprocessing": "default",
                    },
                )
                translated = data.get("text")
                if isinstance(translated, str) and translated.strip():
                    return translated.strip()
            except RuntimeError as exc:
                logger.debug("Shaheen REST translation failed, using chat: %s", exc)

        lang_names = {
            "ar": "Arabic",
            "en": "English",
            "fr": "French",
            "ur": "Urdu",
            "tr": "Turkish",
            "ms": "Malay",
        }
        target = lang_names.get(target_language, target_language)
        source_hint = lang_names.get(src, src)
        max_tokens = min(16384, max(8192, len(text) * 4))
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a professional translator. Translate ALL text from {source_hint} "
                    f"to {target}. Preserve Quranic verses, Hadith wording, and paragraph breaks. "
                    f"Output ONLY the {target} translation."
                ),
            },
            {"role": "user", "content": text},
        ]
        return await self.complete_without_fallback(
            model=FANAR_MODELS["translation"],
            messages=messages,
            temperature=0.1,
            max_tokens=max_tokens,
        )

    async def synthesize_speech(
        self,
        text: str,
        *,
        language: str = "ar",
        voice: str | None = None,
    ) -> bytes:
        """Generate speech audio via Fanar-Aura-TTS-2."""
        cleaned = prepare_text_for_speech(text)
        if not cleaned:
            raise ValueError("TTS input text is empty.")

        speech_lang = detect_speech_language(cleaned, language)
        selected_voice = voice or ("Abdulrahman" if speech_lang == "ar" else "Amelia")
        input_text = cleaned[:4000]
        if len(cleaned) > 4000:
            logger.warning(
                "synthesize_speech: input truncated from %d to 4000 chars",
                len(cleaned),
            )

        url = f"{self.base_url}/audio/speech"
        client = await self._get_client()
        response = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "X-Fanar-Key": self.api_key,
                "X-Organization": self.organization,
                "Content-Type": "application/json",
            },
            json={
                "model": FANAR_MODELS["tts"],
                "input": input_text,
                "voice": selected_voice,
                "response_format": "mp3",
            },
        )
        if response.status_code in {401, 403, 404, 422}:
            raise RuntimeError(f"Fanar TTS HTTP {response.status_code}: {response.text[:300]}")
        response.raise_for_status()
        if not response.content:
            raise ValueError("Fanar TTS returned empty audio")
        return response.content

    async def count_tokens(self, content: str, *, model: str | None = None) -> int | None:
        """Return token count via Fanar /v1/tokens endpoint."""
        if not content.strip():
            return 0
        token_model = model or FANAR_MODELS["reasoning"]
        try:
            data = await self._post(
                "/tokens",
                {"model": token_model, "content": content},
            )
            count = data.get("tokens") or data.get("token_count") or data.get("count")
            if isinstance(count, (int, float)):
                return int(count)
        except RuntimeError as exc:
            logger.debug("Fanar token count unavailable: %s", exc)
        return None

    async def extract_document_text(
        self,
        content: bytes,
        *,
        filename: str = "document.pdf",
        language: str = "en",
    ) -> str:
        """Extract text from PDF or image via Fanar-Oryx-IVU (OCR / vision)."""
        lang_hint = "Arabic" if language == "ar" else "English"
        b64 = base64.b64encode(content).decode("ascii")
        mime = "application/pdf" if filename.lower().endswith(".pdf") else "image/png"

        payload: dict[str, Any] = {
            "model": FANAR_MODELS["vision"],
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"Extract all readable text from this document in {lang_hint}. "
                                "Preserve financial figures, tables, and page structure. "
                                "Output plain text only."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"},
                        },
                    ],
                }
            ],
            "max_tokens": 8000,
        }

        data = await self._post("/chat/completions", payload)
        self._record_usage(data)
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("Fanar-Oryx-IVU returned no content")
        text = choices[0].get("message", {}).get("content", "")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Fanar-Oryx-IVU returned empty text")
        return text.strip()

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        last_error: Exception | None = None
        url = f"{self.base_url}{path}"

        for attempt in range(1, self.max_retries + 1):
            try:
                client = await self._get_client()
                response = await client.post(url, headers=self._headers(), json=payload)
                if response.status_code in {401, 403, 404, 422}:
                    detail = response.text[:300]
                    raise RuntimeError(
                        f"Fanar API HTTP {response.status_code} ({path}): {detail}"
                    )
                response.raise_for_status()
                return response.json()
            except RuntimeError:
                raise
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                logger.warning("Fanar API attempt %s failed (%s): %s", attempt, path, exc)
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** (attempt - 1))

        msg = f"Fanar API failed after {self.max_retries} attempts: {path}"
        raise RuntimeError(msg) from last_error

    @staticmethod
    def _parse_json(raw: str) -> dict[str, Any]:
        text = raw.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return {"analysis": text, "summary": text[:500], "confidence": 0.75}

"""Wrap Fanar-Aura-STT and Fanar-Aura-TTS-2 for voice queries."""

from agents.common.fanar_client import FanarLLMClient


class VoiceAgent:
    """Wrap Fanar-Aura-STT and Fanar-Aura-TTS-2 for voice queries."""

    def __init__(self, llm_client: FanarLLMClient) -> None:
        self.llm = llm_client

    async def transcribe(self, audio_bytes: bytes, *, language: str = "ar") -> str:
        """Convert audio query to text via Fanar-Aura-STT."""
        return await self.llm.transcribe_audio(
            audio_bytes,
            filename="query.webm",
            language=language,
        )

    async def speak(self, text: str, *, language: str = "ar") -> bytes:
        """Convert text response to audio via Fanar-Aura-TTS-2."""
        return await self.llm.synthesize_speech(text, language=language)

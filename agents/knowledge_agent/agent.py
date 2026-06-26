"""Knowledge Agent — assembles structured evidence bundles."""

from pathlib import Path

from agents.common.evidence import EvidenceItem
from config.fanar_api_keys import FANAR_MODELS
from agents.common.fanar_client import FanarLLMClient
from agents.intent_agent.models import IntentResult
from agents.knowledge_agent.models import EvidenceBundle, JurisprudentialPrinciple
from agents.knowledge_agent.tools import infer_principles, is_valid_evidence
from agents.retrieval_agent.models import RetrievalAgentResult

PROMPT_PATH = Path(__file__).parent / "prompt.md"


class KnowledgeAgent:
    """Collect and structure evidence for jurisprudential reasoning."""

    def __init__(self, llm_client: FanarLLMClient | None = None) -> None:
        self.llm = llm_client or FanarLLMClient()
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    async def assemble(
        self,
        retrieval: RetrievalAgentResult,
        intent: IntentResult,
    ) -> EvidenceBundle:
        """Build an evidence bundle from retrieved chunks."""
        valid_evidences = []
        rejected = 0

        for chunk in retrieval.chunks:
            if is_valid_evidence(chunk):
                valid_evidences.append(chunk)
            else:
                rejected += 1

        principles = infer_principles(valid_evidences, intent.entities)

        if valid_evidences:
            try:
                llm_principles = await self._extract_principles_llm(valid_evidences, intent)
                principles = self._merge_principles(principles, llm_principles)
            except RuntimeError:
                pass

        source_ids = list(dict.fromkeys(e.source_id for e in valid_evidences))

        return EvidenceBundle(
            evidences=valid_evidences,
            principles=principles,
            source_ids=source_ids,
            rejected_count=rejected,
        )

    async def _extract_principles_llm(
        self,
        evidences: list[EvidenceItem],
        intent: IntentResult,
    ) -> list[JurisprudentialPrinciple]:
        evidence_text = "\n---\n".join(e.text for e in evidences)
        language = intent.language if intent.language in {"ar", "en"} else "ar"
        language_rule = (
            "Extract principle names and descriptions in Arabic only."
            if language == "ar"
            else "Extract principle names and descriptions in English only."
        )
        result = await self.llm.complete_json(
            model=FANAR_MODELS["agentic"],
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Language: {language}\n"
                        f"{language_rule}\n"
                        f"Query: {intent.raw_query}\n"
                        f"Entities: {intent.entities}\n"
                        f"Evidence:\n{evidence_text}\n"
                        "Extract applicable fiqh principles with citations."
                    ),
                },
            ],
        )
        return [
            JurisprudentialPrinciple(
                name=p["name"],
                description=p["description"],
                citation=p["citation"],
            )
            for p in result.get("principles", [])
        ]

    @staticmethod
    def _merge_principles(
        rule_based: list[JurisprudentialPrinciple],
        llm_based: list[JurisprudentialPrinciple],
    ) -> list[JurisprudentialPrinciple]:
        seen = {p.name for p in rule_based}
        merged = list(rule_based)
        for principle in llm_based:
            if principle.name not in seen:
                merged.append(principle)
                seen.add(principle.name)
        return merged

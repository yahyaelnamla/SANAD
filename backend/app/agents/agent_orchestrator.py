"""Multi-agent pipeline orchestrator with Plan-Execute-Verify agentic loop."""

import logging
import os
import uuid
from typing import Any, Final, cast, Literal

from sqlalchemy.ext.asyncio import AsyncSession

from agents.common.confidence_scorer import compute_confidence
from agents.common.fanar_client import FanarLLMClient
from agents.common.state import AgentPipelineState
from agents.common.trace_timing import (
    build_execution_metrics,
    complete_trace_step,
    flush_step_tokens,
    reject_trace_step,
    start_trace_step,
)
from agents.financial_context_agent.agent import FinancialContextAgent
from agents.financial_context_agent.models import FinancialContext
from agents.intent_agent.agent import IntentAgent
from agents.knowledge_agent.agent import KnowledgeAgent
from agents.reasoning_agent.agent import ReasoningAgent
from agents.response_builder.agent import ResponseBuilder
from agents.response_builder.models import FinalResponse
from agents.response_builder.tools import build_refusal_response, sanitize_user_text
from agents.retrieval_agent.agent import RetrievalAgent
from agents.retrieval_agent.models import RetrievalAgentResult
from agents.verification_agent.agent import VerificationAgent
from agents.voice_agent.agent import VoiceAgent
from backend.app.services.auto_mode_service import (
    auto_mode_requires_financial,
    detect_auto_mode,
)
from backend.app.services.conversation_memory_service import build_effective_query
from backend.app.services.document_memory_service import fetch_document_evidence
from backend.app.services.evidence_language_service import align_evidence_language
from backend.app.services.fanar_model_router import TaskKind, model_for_task
from backend.app.services.pipeline_config import resolve_pipeline_config
from backend.app.services.query_depth import plan_for_depth
from backend.app.services.query_trace_cache import publish
from backend.app.services.suggested_questions_service import generate_suggested_questions

logger = logging.getLogger(__name__)

FANAR_SUPPORTED_LANGUAGES = frozenset({"ar", "en", "fr", "ur", "tr", "ms"})
MAX_EVIDENCE_TOKENS: Final[int] = int(os.getenv("MAX_EVIDENCE_TOKENS", "12000"))


def _trace_dicts(state: AgentPipelineState) -> list[dict[str, Any]]:
    return [step.model_dump(exclude_none=True) for step in state.agent_trace]


def _publish_live_trace(
    state: AgentPipelineState,
    query_id: uuid.UUID | None,
    *,
    draft_answer: str | None = None,
) -> None:
    if query_id is None:
        return
    publish(query_id, _trace_dicts(state), draft_answer=draft_answer)


class AgentOrchestrator:
    """Coordinate the agentic Plan → Execute → Verify pipeline."""

    DEFAULT_STEPS = [
        "intent",
        "retrieval",
        "knowledge",
        "financial",
        "reasoning",
        "verification",
        "response",
    ]

    def __init__(
        self,
        session: AsyncSession,
        llm_client: FanarLLMClient | None = None,
    ) -> None:
        api_key = os.getenv("FANAR_API_KEY")
        self.llm = llm_client or FanarLLMClient(api_key=api_key, timeout=300.0)
        self.intent_agent = IntentAgent(self.llm)
        self.retrieval_agent = RetrievalAgent(session, fanar_client=self.llm)
        self.knowledge_agent = KnowledgeAgent(self.llm)
        self.financial_agent = FinancialContextAgent()
        self.reasoning_agent = ReasoningAgent(self.llm)
        self.verification_agent = VerificationAgent(self.llm)
        self.response_builder = ResponseBuilder(self.llm)
        self.voice_agent = VoiceAgent(self.llm)

    async def close(self) -> None:
        """Release shared HTTP resources."""
        await self.llm.close()

    def _begin_step(
        self,
        state: AgentPipelineState,
        task: TaskKind,
        agent: str,
        *,
        depth: str,
        fanar_model: str,
        query_id: uuid.UUID | None,
        phase: str = "execute",
        model_override: str | None = None,
        language: str | None = None,
    ) -> str:
        model = model_override or model_for_task(
            task,
            depth=depth,
            preference=fanar_model,
            language=language,
        )
        state.active_model = model
        start_trace_step(state, phase=phase, agent=agent, model=model)
        _publish_live_trace(state, query_id)
        return model

    async def process_query(
        self,
        query: str,
        *,
        user_id: uuid.UUID | None = None,
        top_k: int = 5,
        advanced_analysis: bool = False,
        preferred_language: str | None = None,
        fanar_model: str = "auto",
        session_id: str | None = None,
        conversation_history: list[dict[str, str]] | None = None,
        query_id: uuid.UUID | None = None,
    ) -> FinalResponse:
        """Run Plan-Execute-Verify agentic loop for a user query."""
        original_query = query
        memory_meta: dict[str, Any] | None = None
        if user_id is not None:
            original_query, memory_meta = await build_effective_query(
                self.retrieval_agent.session,
                user_id,
                query,
                session_id=session_id,
                conversation_history=conversation_history,
                llm=self.llm,
            )

        input_mod = await self.llm.moderate_input(user_query=original_query)
        input_passes, input_reason = self.llm.passes_guard(input_mod)
        if not input_passes:
            lang = preferred_language or "en"
            return build_refusal_response(
                input_reason or "Query did not pass content screening.",
                language=lang,
                agent_trace=[],
            )

        state = AgentPipelineState(query=original_query)
        memory_meta_ = memory_meta or {}
        state.conversation_history = list(memory_meta_.get("merged_history") or [])
        state.retrieval_query = memory_meta_.get("retrieval_query") or original_query
        state.conversation_memory_used = bool(memory_meta_.get("conversation_memory_used"))
        auto_mode = detect_auto_mode(original_query)
        state.auto_mode = auto_mode
        depth, top_k, advanced_analysis, _pipeline_flags = resolve_pipeline_config(
            original_query,
            advanced_analysis=advanced_analysis,
            fanar_model=fanar_model,
        )
        # _pipeline_flags: reserved for future per-deployment overrides from resolve_pipeline_config
        state.pipeline_depth = depth

        plan = await self._plan(
            original_query,
            depth=depth,
            auto_mode=auto_mode,
            fanar_model=fanar_model,
        )
        state.execution_plan = plan["steps"]
        self._begin_step(
            state,
            "intent",
            "Planner",
            depth=depth,
            fanar_model=fanar_model,
            query_id=query_id,
            phase="plan",
        )
        complete_trace_step(state)
        flush_step_tokens(state, self.llm)
        _publish_live_trace(state, query_id)

        state = await self._execute(
            state,
            plan,
            user_id=user_id,
            top_k=top_k,
            depth=depth,
            preferred_language=preferred_language,
            fanar_model=fanar_model,
            query_id=query_id,
            memory_meta=memory_meta_,
        )
        financial_context_dict = (
            state.financial_context.to_api_dict() if state.financial_context else None
        )

        if state.refused:
            _publish_live_trace(state, query_id)
            refusal = build_refusal_response(
                state.refusal_reason or "No authenticated evidence found.",
                language=state.intent.language if state.intent else "en",
                agent_trace=_trace_dicts(state),
            )
            refusal.execution_metrics = self._build_metrics(state, fanar_model)
            refusal.financial_context = financial_context_dict
            return refusal

        if not state.reasoning or not state.knowledge:
            raise RuntimeError("Reasoning or Knowledge is missing before this step.")
        self._begin_step(
            state,
            "verification",
            "VerificationAgent",
            depth=depth,
            fanar_model=fanar_model,
            query_id=query_id,
            phase="verify",
        )
        try:
            state.verification = await self.verification_agent.verify(
                state.reasoning,
                state.knowledge,
                user_query=original_query,
                depth=depth,
            )
        except Exception as exc:
            logger.error("VerificationAgent failed: %s", exc, exc_info=True)
            raise RuntimeError(f"VerificationAgent failed: {exc}") from exc
        flush_step_tokens(state, self.llm)
        if state.verification.approved:
            complete_trace_step(state)
        else:
            reject_trace_step(state)
        _publish_live_trace(state, query_id)

        if not state.verification.approved:
            state.refused = True
            state.refusal_reason = state.verification.reason
            refusal = build_refusal_response(
                state.refusal_reason or "Verification failed.",
                language=state.intent.language if state.intent else "en",
                agent_trace=_trace_dicts(state),
            )
            refusal.execution_metrics = self._build_metrics(state, fanar_model)
            refusal.financial_context = financial_context_dict
            return refusal

        final_confidence, confidence_breakdown = compute_confidence(
            state.knowledge,
            state.reasoning,
            state.verification,
            guard_scores=state.verification.guard_scores,
        )
        state.reasoning.confidence = final_confidence

        if not (state.knowledge and state.reasoning and state.intent):
            raise RuntimeError("Knowledge, Reasoning, or Intent missing before ResponseBuilder.")
        self._begin_step(
            state,
            "response",
            "ResponseBuilder",
            depth=depth,
            fanar_model=fanar_model,
            query_id=query_id,
            phase="response",
        )
        execution_metrics = self._build_metrics(state, fanar_model)
        try:
            state.final_response = await self.response_builder.build(
                state.knowledge,
                state.reasoning,
                state.intent,
                agent_trace=_trace_dicts(state),
                confidence_breakdown=confidence_breakdown,
                financial_context=financial_context_dict,
                execution_metrics=execution_metrics,
            )
        except Exception as exc:
            logger.error("ResponseBuilder failed: %s", exc, exc_info=True)
            raise RuntimeError(f"ResponseBuilder failed: {exc}") from exc
        flush_step_tokens(state, self.llm)
        complete_trace_step(state)
        _publish_live_trace(state, query_id)

        if state.final_response and not state.final_response.refused and depth == "deep":
            suggestions = await generate_suggested_questions(
                self.llm,
                question=original_query,
                summary=state.final_response.summary,
                language=state.intent.language if state.intent else "en",
            )
            state.final_response.suggested_questions = suggestions

        if state.final_response:
            state.final_response.execution_metrics = self._build_metrics(state, fanar_model)

        if state.final_response is None:
            raise RuntimeError("ResponseBuilder did not return a FinalResponse.")
        return state.final_response

    async def process_document_query(
        self,
        content: bytes,
        filename: str,
        *,
        language: str = "ar",
        user_id: uuid.UUID | None = None,
        query_id: uuid.UUID | None = None,
        **query_kwargs: Any,
    ) -> FinalResponse:
        """Extract text from uploaded PDF/image via Fanar-Oryx-IVU, then run pipeline."""
        retrieval = await self.retrieval_agent.retrieve_from_document(
            content,
            filename=filename,
            language=language,
        )
        if retrieval.refused:
            return build_refusal_response(
                retrieval.reason or "Document extraction failed.",
                language=language,
            )
        extracted_query = retrieval.query
        return await self.process_query(
            extracted_query,
            preferred_language=language,
            user_id=user_id,
            query_id=query_id,
            **query_kwargs,
        )

    async def process_voice_query(
        self,
        audio_bytes: bytes,
        *,
        language: str = "ar",
        synthesize: bool = True,
        **query_kwargs: Any,
    ) -> tuple[FinalResponse, bytes | None]:
        """Transcribe audio, run the text pipeline, optionally synthesize the summary."""
        transcript = await self.voice_agent.transcribe(audio_bytes, language=language)
        response = await self.process_query(
            transcript,
            preferred_language=language,
            **query_kwargs,
        )
        audio_out: bytes | None = None
        if synthesize and response.summary:
            audio_out = await self.voice_agent.speak(response.summary, language=language)
        return response, audio_out

    def _build_metrics(self, state: AgentPipelineState, fanar_model: str) -> dict[str, Any]:
        """Aggregate execution metrics including user model preference and token totals."""
        metrics = build_execution_metrics(state, llm=self.llm)
        metrics["fanar_model_preference"] = fanar_model
        if self.llm.total_tokens:
            metrics["tokens_total"] = self.llm.total_tokens
            if not metrics.get("tokens_estimate"):
                metrics["tokens_estimate"] = self.llm.total_tokens
        return metrics

    async def _plan(
        self,
        query: str,
        *,
        depth: str = "deep",
        auto_mode: str = "normal",
        fanar_model: str = "auto",
    ) -> dict:
        """Build execution steps from query depth; optional agentic planner for deep mode."""
        if depth in {"fast", "standard"}:
            plan = plan_for_depth(cast(Literal["fast", "standard", "deep"], depth))
            plan["requires_financial_context"] = False
            return plan

        plan = plan_for_depth("deep")
        if auto_mode_requires_financial(auto_mode):
            plan["requires_financial_context"] = True
        elif auto_mode == "document":
            plan["requires_financial_context"] = False

        if os.getenv("SKIP_AGENTIC_PLANNER", "false").lower() in {"1", "true", "yes"}:
            return plan

        system_name = os.getenv("AGENT_SYSTEM_NAME", "SANAD")
        planner_model_display = os.getenv("PLANNER_MODEL_DISPLAY_NAME", "Fanar-Sadiq-Agentic")
        planner_prompt = (
            f"You are the {system_name} agentic planner using {planner_model_display}.\n"
            "Decompose the user query into an execution plan for Shariah financial reasoning.\n"
            "Return JSON with:\n"
            "- steps: ordered list from [intent, retrieval, knowledge, financial, reasoning, verification, response]\n"
            "- requires_financial_context: boolean\n"
            "- rationale: brief explanation"
        )

        try:
            agentic_model = model_for_task("plan", depth=depth, preference=fanar_model)
            result = await self.llm.complete_json(
                model=agentic_model,
                messages=[
                    {"role": "system", "content": planner_prompt},
                    {"role": "user", "content": f"Plan execution for:\n{query}"},
                ],
            )
            steps = result.get("steps", self.DEFAULT_STEPS)
            if not isinstance(steps, list) or not steps:
                steps = self.DEFAULT_STEPS
            return {
                "steps": steps,
                "requires_financial_context": bool(
                    result.get("requires_financial_context", plan["requires_financial_context"])
                ),
                "depth": "deep",
            }
        except Exception as exc:
            logger.warning(
                "Agentic planner failed (%s: %s); falling back to default steps.",
                type(exc).__name__,
                exc,
            )
            return plan

    async def _run_intent(
        self,
        state: AgentPipelineState,
        *,
        depth: str,
        fanar_model: str,
        preferred_language: str | None,
        query_id: uuid.UUID | None,
    ) -> str:
        self._begin_step(
            state,
            "intent",
            "IntentAgent",
            depth=depth,
            fanar_model=fanar_model,
            query_id=query_id,
        )
        try:
            state.intent = await self.intent_agent.analyze(
                state.query,
                conversation_history=state.conversation_history,
            )
        except Exception as exc:
            logger.error("IntentAgent failed: %s", exc, exc_info=True)
            raise RuntimeError(f"IntentAgent failed: {exc}") from exc
        if preferred_language in FANAR_SUPPORTED_LANGUAGES:
            state.intent.language = preferred_language
        detected_language = state.intent.language or "en"
        flush_step_tokens(state, self.llm)
        complete_trace_step(state)
        _publish_live_trace(state, query_id)
        logger.info("Intent classified: %s", state.intent.intent_type)
        return detected_language

    async def _run_retrieval(
        self,
        state: AgentPipelineState,
        *,
        user_id: uuid.UUID | None,
        top_k: int,
        depth: str,
        fanar_model: str,
        query_id: uuid.UUID | None,
        memory_meta: dict[str, Any],
        detected_language: str,
    ) -> AgentPipelineState:
        self._begin_step(
            state,
            "retrieval",
            "RetrievalAgent",
            depth=depth,
            fanar_model=fanar_model,
            query_id=query_id,
            language=detected_language,
        )
        prior_chunks = memory_meta.get("prior_evidence_chunks") or []

        if memory_meta.get("reuse_prior_evidence") and prior_chunks:
            state.retrieval = RetrievalAgentResult(
                query=state.intent.raw_query if state.intent else state.query,
                chunks=prior_chunks,
            )
            flush_step_tokens(state, self.llm)
            complete_trace_step(state)
            _publish_live_trace(state, query_id)
        else:
            retrieval_intent = state.intent.model_copy(
                update={"raw_query": state.retrieval_query or state.query},
            )
            try:
                state.retrieval = await self.retrieval_agent.retrieve(
                    retrieval_intent,
                    top_k=top_k,
                    language=detected_language,
                )
            except Exception as exc:
                logger.error("RetrievalAgent failed: %s", exc, exc_info=True)
                raise RuntimeError(f"RetrievalAgent failed: {exc}") from exc
            flush_step_tokens(state, self.llm)
            complete_trace_step(state)
            _publish_live_trace(state, query_id)

        if user_id is not None:
            document_evidence = await fetch_document_evidence(
                self.retrieval_agent.session,
                user_id,
                state.query,
            )
            if document_evidence:
                state.document_context_used = True
                self._begin_step(
                    state,
                    "retrieval",
                    "DocumentMemory",
                    depth=depth,
                    fanar_model=fanar_model,
                    query_id=query_id,
                    model_override="user-documents",
                )
                if state.retrieval.refused or not state.retrieval.chunks:
                    state.retrieval = RetrievalAgentResult(
                        query=state.query,
                        chunks=document_evidence,
                        refused=False,
                        reason=None,
                    )
                else:
                    state.retrieval.chunks = document_evidence + state.retrieval.chunks
                complete_trace_step(state)
                _publish_live_trace(state, query_id)

        if state.retrieval.refused or not state.retrieval.has_evidence:
            state.refused = True
            state.refusal_reason = state.retrieval.reason
            _publish_live_trace(state, query_id)
        return state

    async def _run_knowledge(
        self,
        state: AgentPipelineState,
        *,
        top_k: int,
        depth: str,
        detected_language: str,
        fanar_model: str,
        query_id: uuid.UUID | None,
    ) -> AgentPipelineState:
        self._begin_step(
            state,
            "knowledge",
            "KnowledgeAgent",
            depth=depth,
            fanar_model=fanar_model,
            query_id=query_id,
            language=detected_language,
        )
        if state.retrieval is None:
            raise RuntimeError("Retrieval result missing before KnowledgeAgent.")

        if state.retrieval.chunks:
            evidence_preview = "\n".join(c.text[:200] for c in state.retrieval.chunks)
            token_estimate = await self.llm.count_tokens(evidence_preview)
            if token_estimate and token_estimate > MAX_EVIDENCE_TOKENS:
                state.retrieval.chunks = sorted(
                    state.retrieval.chunks,
                    key=lambda c: c.score,
                    reverse=True,
                )[:top_k]
                logger.warning(
                    "Pre-knowledge trim: reduced to top-%d chunks (%d estimated tokens)",
                    top_k,
                    token_estimate,
                )

        try:
            state.knowledge = await self.knowledge_agent.assemble(state.retrieval, state.intent)
        except Exception as exc:
            logger.error("KnowledgeAgent failed: %s", exc, exc_info=True)
            raise RuntimeError(f"KnowledgeAgent failed: {exc}") from exc
        if (
            depth == "deep"
            and detected_language in FANAR_SUPPORTED_LANGUAGES
            and detected_language != "en"
            and state.knowledge.evidences
        ):
            state.knowledge.evidences = await align_evidence_language(
                state.knowledge.evidences,
                detected_language,
                self.llm,
            )
        flush_step_tokens(state, self.llm)
        complete_trace_step(state)
        _publish_live_trace(state, query_id)

        if not state.knowledge.has_valid_evidence:
            state.refused = True
            state.refusal_reason = "No valid evidence after knowledge assembly."
            _publish_live_trace(state, query_id)
        return state

    async def _run_financial(
        self,
        state: AgentPipelineState,
        *,
        depth: str,
        fanar_model: str,
        query_id: uuid.UUID | None,
    ) -> AgentPipelineState:
        self._begin_step(
            state,
            "financial",
            "FinancialContextAgent",
            depth=depth,
            fanar_model=fanar_model,
            query_id=query_id,
            model_override="yahoo-finance",
        )
        try:
            state.financial_context = await self.financial_agent.enrich(state.intent)
        except Exception as exc:
            logger.error("FinancialContextAgent failed: %s", exc, exc_info=True)
            raise RuntimeError(f"FinancialContextAgent failed: {exc}") from exc
        complete_trace_step(state)
        _publish_live_trace(state, query_id)
        return state

    async def _run_reasoning(
        self,
        state: AgentPipelineState,
        *,
        depth: str,
        detected_language: str,
        fanar_model: str,
        query_id: uuid.UUID | None,
        memory_meta: dict[str, Any],
    ) -> AgentPipelineState:
        reasoning_model = self._begin_step(
            state,
            "reasoning",
            "ReasoningAgent",
            depth=depth,
            fanar_model=fanar_model,
            query_id=query_id,
            language=detected_language,
        )
        if not state.knowledge or not state.financial_context:
            raise RuntimeError("Knowledge or FinancialContext missing before ReasoningAgent.")
        try:
            state.reasoning = await self.reasoning_agent.analyze(
                state.knowledge,
                state.financial_context,
                state.intent,
                model=reasoning_model,
                depth=depth,
                evidence_listing=bool(memory_meta.get("reuse_prior_evidence")),
                conversation_history=state.conversation_history,
            )
        except Exception as exc:
            logger.error("ReasoningAgent failed: %s", exc, exc_info=True)
            raise RuntimeError(f"ReasoningAgent failed: {exc}") from exc
        flush_step_tokens(state, self.llm)
        complete_trace_step(state)
        if state.reasoning:
            draft = sanitize_user_text(state.reasoning.analysis)
            _publish_live_trace(state, query_id, draft_answer=draft or None)
        else:
            _publish_live_trace(state, query_id)
        return state

    async def _execute(
        self,
        state: AgentPipelineState,
        plan: dict,
        *,
        user_id: uuid.UUID | None = None,
        top_k: int,
        depth: str = "deep",
        preferred_language: str | None = None,
        fanar_model: str = "auto",
        query_id: uuid.UUID | None = None,
        memory_meta: dict[str, Any] | None = None,
    ) -> AgentPipelineState:
        """Execute pipeline agents according to the plan."""
        memory_meta_ = memory_meta or {}
        steps = plan.get("steps", self.DEFAULT_STEPS)
        requires_financial = plan.get("requires_financial_context", True)
        detected_language = "en"

        if "intent" in steps:
            detected_language = await self._run_intent(
                state,
                depth=depth,
                fanar_model=fanar_model,
                preferred_language=preferred_language,
                query_id=query_id,
            )

        if state.intent is None:
            raise RuntimeError("IntentAgent produced no output; cannot continue pipeline.")

        if "retrieval" in steps:
            state = await self._run_retrieval(
                state,
                user_id=user_id,
                top_k=top_k,
                depth=depth,
                fanar_model=fanar_model,
                query_id=query_id,
                memory_meta=memory_meta_,
                detected_language=detected_language,
            )
            if state.refused:
                return state

        if "knowledge" in steps:
            state = await self._run_knowledge(
                state,
                top_k=top_k,
                depth=depth,
                detected_language=detected_language,
                fanar_model=fanar_model,
                query_id=query_id,
            )
            if state.refused:
                return state

        if requires_financial and "financial" in steps:
            state = await self._run_financial(
                state,
                depth=depth,
                fanar_model=fanar_model,
                query_id=query_id,
            )
        elif state.financial_context is None:
            state.financial_context = FinancialContext(entities=state.intent.entities)

        if "reasoning" in steps:
            state = await self._run_reasoning(
                state,
                depth=depth,
                detected_language=detected_language,
                fanar_model=fanar_model,
                query_id=query_id,
                memory_meta=memory_meta_,
            )

        return state

"""Shared pipeline state for the multi-agent orchestrator."""

from pydantic import BaseModel, Field, PrivateAttr

from agents.financial_context_agent.models import FinancialContext
from agents.intent_agent.models import IntentResult
from agents.knowledge_agent.models import EvidenceBundle
from agents.reasoning_agent.models import ReasoningResult
from agents.response_builder.models import FinalResponse
from agents.retrieval_agent.models import RetrievalAgentResult
from agents.verification_agent.models import VerificationResult


class AgentStepStatus(BaseModel):
    """Status of a single agent step for live UI telemetry."""

    phase: str
    agent: str
    model: str
    status: str = "pending"
    latency_ms: int | None = None
    started_at: str | None = None
    completed_at: str | None = None
    tokens_estimate: int | None = None

    _started_perf: float | None = PrivateAttr(default=None)


class AgentPipelineState(BaseModel):
    """Mutable state passed through the agent orchestrator."""

    query: str
    intent: IntentResult | None = None
    retrieval: RetrievalAgentResult | None = None
    knowledge: EvidenceBundle | None = None
    financial_context: FinancialContext | None = None
    reasoning: ReasoningResult | None = None
    verification: VerificationResult | None = None
    final_response: FinalResponse | None = None
    refused: bool = False
    refusal_reason: str | None = None
    execution_plan: list[str] = Field(default_factory=list)
    agent_trace: list[AgentStepStatus] = Field(default_factory=list)
    active_model: str | None = None
    pipeline_depth: str = "deep"
    document_context_used: bool = False
    conversation_memory_used: bool = False
    auto_mode: str = "normal"
    conversation_history: list[dict[str, str]] = Field(default_factory=list)
    retrieval_query: str | None = None

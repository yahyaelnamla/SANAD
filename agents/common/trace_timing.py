"""Agent trace timing helpers for execution telemetry."""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Any

from agents.common.state import AgentPipelineState, AgentStepStatus


def start_trace_step(
    state: AgentPipelineState,
    *,
    phase: str,
    agent: str,
    model: str,
) -> AgentStepStatus:
    """Append a running agent step with a monotonic start timestamp."""
    step = AgentStepStatus(
        phase=phase,
        agent=agent,
        model=model,
        status="running",
        started_at=_iso_now(),
    )
    step._started_perf = time.perf_counter()
    state.agent_trace.append(step)
    return step


def complete_trace_step(state: AgentPipelineState, *, tokens_estimate: int | None = None) -> None:
    """Mark the latest trace step completed and record latency."""
    if not state.agent_trace:
        return
    step = state.agent_trace[-1]
    if step.status == "completed":
        return
    if step._started_perf is not None:
        step.latency_ms = int((time.perf_counter() - step._started_perf) * 1000)
    step.status = "completed"
    step.completed_at = _iso_now()
    if tokens_estimate is not None:
        step.tokens_estimate = tokens_estimate


def reject_trace_step(state: AgentPipelineState) -> None:
    """Mark the latest trace step rejected."""
    if not state.agent_trace:
        return
    step = state.agent_trace[-1]
    if step._started_perf is not None:
        step.latency_ms = int((time.perf_counter() - step._started_perf) * 1000)
    step.status = "rejected"
    step.completed_at = _iso_now()


def flush_step_tokens(state: AgentPipelineState, llm: Any) -> None:
    """Attach Fanar token usage to the latest trace step."""
    consume = getattr(llm, "consume_tokens_since_last", None)
    if not consume or not state.agent_trace:
        return
    tokens = consume()
    if tokens is not None and state.agent_trace[-1].tokens_estimate is None:
        state.agent_trace[-1].tokens_estimate = tokens


def build_execution_metrics(state: AgentPipelineState, *, llm: Any | None = None) -> dict[str, Any]:
    """Aggregate pipeline execution metrics for the API response."""
    latencies = [s.latency_ms for s in state.agent_trace if s.latency_ms is not None]
    tokens = [s.tokens_estimate for s in state.agent_trace if s.tokens_estimate is not None]
    models = list(dict.fromkeys(s.model for s in state.agent_trace if s.model))
    metrics: dict = {
        "total_latency_ms": sum(latencies),
        "steps_completed": len([s for s in state.agent_trace if s.status == "completed"]),
        "steps_total": len(state.agent_trace),
        "models_used": models,
        "tokens_estimate": sum(tokens) if tokens else None,
        "pipeline_depth": state.pipeline_depth,
        "document_context_used": state.document_context_used or None,
        "conversation_memory_used": getattr(state, "conversation_memory_used", False) or None,
        "auto_mode": getattr(state, "auto_mode", None),
    }
    if llm is not None and getattr(llm, "total_tokens", 0):
        total = llm.total_tokens
        if total and not metrics["tokens_estimate"]:
            metrics["tokens_estimate"] = total
    return metrics


def _iso_now() -> str:
    return datetime.now(UTC).isoformat()

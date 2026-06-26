"""Tests for agent trace timing helpers."""

from agents.common.state import AgentPipelineState, AgentStepStatus
from agents.common.trace_timing import (
    build_execution_metrics,
    complete_trace_step,
    start_trace_step,
)


def test_trace_timing_records_latency() -> None:
    state = AgentPipelineState(query="test")
    start_trace_step(state, phase="execute", agent="IntentAgent", model="fanar-sadiq")
    complete_trace_step(state, tokens_estimate=120)

    step = state.agent_trace[0]
    assert step.status == "completed"
    assert step.latency_ms is not None
    assert step.latency_ms >= 0
    assert step.tokens_estimate == 120
    assert step.started_at
    assert step.completed_at


def test_build_execution_metrics_aggregates_steps() -> None:
    state = AgentPipelineState(
        query="test",
        agent_trace=[
            AgentStepStatus(
                phase="execute",
                agent="IntentAgent",
                model="fanar-sadiq",
                status="completed",
                latency_ms=100,
                tokens_estimate=50,
            ),
            AgentStepStatus(
                phase="execute",
                agent="RetrievalAgent",
                model="fanar-rag",
                status="completed",
                latency_ms=250,
            ),
        ],
    )

    metrics = build_execution_metrics(state)
    assert metrics["total_latency_ms"] == 350
    assert metrics["steps_completed"] == 2
    assert metrics["steps_total"] == 2
    assert metrics["models_used"] == ["fanar-sadiq", "fanar-rag"]
    assert metrics["tokens_estimate"] == 50

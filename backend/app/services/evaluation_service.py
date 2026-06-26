"""Evaluation dashboard — Fanar strengths demo for hackathon judges."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.enums import QueryStatus
from backend.app.models.query import Query
from backend.app.models.user import User
from backend.app.schemas.evaluation_schemas import (
    DemoPromptSchema,
    EvaluationDashboardSchema,
    EvaluationStatsSchema,
    FeatureMatrixRowSchema,
    RecentQueryMetricSchema,
)
from backend.app.services.fanar_model_router import (
    fanar_capabilities_manifest,
    fanar_capability_improvements,
)

DEMO_PROMPTS: list[DemoPromptSchema] = [
    DemoPromptSchema(
        id="fast_riba",
        title="Fast Shariah answer",
        description="Simple fiqh question routed through retrieval + Fanar-Sadiq in seconds.",
        fanar_product="Fanar-Sadiq",
        route="/chat",
        question="Is riba haram in Islam?",
    ),
    DemoPromptSchema(
        id="deep_bitcoin",
        title="Deep multi-scholar analysis",
        description="Complex comparison uses Fanar-C-2-27B reasoning with Guard verification.",
        fanar_product="Fanar-C-2-27B",
        route="/chat",
        question="Compare scholarly opinions on Bitcoin staking and yield products.",
    ),
    DemoPromptSchema(
        id="company_scan",
        title="Company Shariah screening",
        description="Live financial context with Fanar-Sadiq synthesis and market data.",
        fanar_product="Fanar-Sadiq",
        route="/scanner/company",
    ),
    DemoPromptSchema(
        id="document_ocr",
        title="PDF & OCR analysis",
        description="Upload annual reports — Fanar-Oryx-IVU-2 extracts tables and riba signals.",
        fanar_product="Fanar-Oryx-IVU-2",
        route="/documents",
    ),
    DemoPromptSchema(
        id="voice_ar",
        title="Voice assistant",
        description="Record in Arabic or English — Fanar-Aura-STT-1 transcribes with dialect support.",
        fanar_product="Fanar-Aura-STT-1",
        route="/chat",
    ),
    DemoPromptSchema(
        id="translate",
        title="Multilingual answers",
        description="Instant translation via Fanar-Shaheen-MT-1 without rerunning the pipeline.",
        fanar_product="Fanar-Shaheen-MT-1",
        route="/chat",
        question="What is the ruling on mixed ETFs?",
    ),
]

FEATURE_MATRIX: list[FeatureMatrixRowSchema] = [
    FeatureMatrixRowSchema(
        id="chat",
        feature="Chat & summaries",
        fanar_products=["Fanar-Sadiq"],
        description="Intent, knowledge synthesis, response building, follow-ups",
    ),
    FeatureMatrixRowSchema(
        id="deep_fiqh",
        feature="Deep fiqh reasoning",
        fanar_products=["Fanar-C-2-27B", "Fanar-Guard-2"],
        description="Comparisons, disagreements, multi-step synthesis with mandatory guard",
    ),
    FeatureMatrixRowSchema(
        id="evidence",
        feature="Evidence retrieval",
        fanar_products=["Fanar-Sadiq"],
        description="RAG over authenticated Quran, Hadith, fatwa, and Shariah standards",
    ),
    FeatureMatrixRowSchema(
        id="voice",
        feature="Voice mode",
        fanar_products=["Fanar-Aura-STT-1"],
        description="Arabic dialects and English speech-to-text in chat",
    ),
    FeatureMatrixRowSchema(
        id="documents",
        feature="Document analyzer",
        fanar_products=["Fanar-Oryx-IVU-2", "Fanar-Sadiq"],
        description="OCR, tables, riba detection, document-memory Q&A",
    ),
    FeatureMatrixRowSchema(
        id="translation",
        feature="Translation",
        fanar_products=["Fanar-Shaheen-MT-1"],
        description="Six-language answer translation preserving citations",
    ),
]

LIMITATIONS = [
    "Token counts depend on Fanar usage metadata when returned by the API.",
    "Live market quotes may time out; cached quotes used as fallback.",
    "Scholarly opinions require authenticated source grounding — ungrounded claims are dropped.",
]

FUTURE_SUGGESTIONS = [
    "Native streaming token events from Fanar-Sadiq for lower perceived latency.",
    "Structured JSON mode for madhhab matrix and financial screening fields.",
    "Batch embedding API for faster knowledge-base ingestion.",
    "Fanar-Sadiq-Agentic native tool-call schema for Yahoo Finance and Serper.",
    "Fanar-Guard-2 batch moderation for multi-section responses.",
]


class EvaluationService:
    """Build judge-facing dashboard from persisted query metrics."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_dashboard(self, user: User) -> EvaluationDashboardSchema:
        """Aggregate recent query metrics and Fanar capability mapping."""
        stmt = (
            select(Query)
            .where(
                Query.user_id == user.id,
                Query.status == QueryStatus.COMPLETED,
            )
            .options(selectinload(Query.response))
            .order_by(Query.created_at.desc())
            .limit(40)
        )
        result = await self.session.execute(stmt)
        queries = list(result.scalars().all())

        latencies: list[float] = []
        tokens: list[float] = []
        models: set[str] = set()
        guard_pass = 0
        guard_total = 0
        fast_count = 0
        deep_count = 0
        doc_memory = 0
        recent: list[RecentQueryMetricSchema] = []

        for query in queries:
            response = query.response
            if response is None:
                continue

            metrics = response.execution_metrics or {}
            latency = metrics.get("total_latency_ms")
            if isinstance(latency, (int, float)):
                latencies.append(float(latency))

            token_est = metrics.get("tokens_total") or metrics.get("tokens_estimate")
            if isinstance(token_est, (int, float)):
                tokens.append(float(token_est))

            for model in metrics.get("models_used") or []:
                if isinstance(model, str) and model.strip():
                    models.add(model.strip())

            depth = metrics.get("pipeline_depth")
            if depth == "fast":
                fast_count += 1
            elif depth == "deep":
                deep_count += 1

            if metrics.get("document_context_used"):
                doc_memory += 1

            for step in response.agent_trace or []:
                if not isinstance(step, dict):
                    continue
                agent = str(step.get("agent") or "")
                if "Verification" in agent or step.get("phase") == "verify":
                    guard_total += 1
                    if step.get("status") == "completed":
                        guard_pass += 1

            if len(recent) < 8:
                token_int = int(token_est) if isinstance(token_est, (int, float)) else None
                recent.append(
                    RecentQueryMetricSchema(
                        query_id=str(query.id),
                        question=query.title[:200],
                        latency_ms=float(latency) if isinstance(latency, (int, float)) else None,
                        tokens_estimate=token_int,
                        pipeline_depth=str(depth) if depth else None,
                        models_used=list(metrics.get("models_used") or []),
                        refused=bool(response.refused),
                    )
                )

        avg_latency = sum(latencies) / len(latencies) if latencies else None
        avg_tokens = sum(tokens) / len(tokens) if tokens else None
        total_tokens = int(sum(tokens)) if tokens else None
        guard_rate = (guard_pass / guard_total) if guard_total else None

        stats = EvaluationStatsSchema(
            total_completed_queries=len(queries),
            average_latency_ms=round(avg_latency, 1) if avg_latency is not None else None,
            average_tokens_estimate=round(avg_tokens, 0) if avg_tokens is not None else None,
            total_tokens_estimate=total_tokens,
            unique_models_used=sorted(models),
            guard_pass_rate=round(guard_rate, 3) if guard_rate is not None else None,
            fast_pipeline_count=fast_count,
            deep_pipeline_count=deep_count,
            document_memory_queries=doc_memory,
        )

        return EvaluationDashboardSchema(
            fanar_capabilities=fanar_capabilities_manifest(),
            fanar_capability_improvements=fanar_capability_improvements(),
            stats=stats,
            demo_prompts=DEMO_PROMPTS,
            feature_matrix=FEATURE_MATRIX,
            recent_queries=recent,
            limitations=LIMITATIONS,
            future_fanar_suggestions=FUTURE_SUGGESTIONS,
        )

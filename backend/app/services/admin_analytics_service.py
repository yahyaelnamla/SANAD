"""Admin analytics — query volume, refusal rate, model usage."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import QueryStatus
from backend.app.models.query import Query
from backend.app.models.response import Response
from backend.app.repositories.source_repository import SourceRepository
from backend.app.schemas.source_schemas import (
    AdminAnalyticsResponse,
    AdminDailyQueryCount,
    AdminModelUsage,
    AdminStatsResponse,
)


class AdminAnalyticsService:
    """Aggregate platform metrics for the admin dashboard."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.source_repo = SourceRepository(session)

    async def get_source_stats(self) -> AdminStatsResponse:
        total = await self.source_repo.count_filtered()
        authenticated = await self.source_repo.count_authenticated()
        pending = await self.source_repo.count_pending()
        return AdminStatsResponse(
            total_sources=total,
            authenticated_sources=authenticated,
            pending_sources=pending,
        )

    async def get_analytics(self) -> AdminAnalyticsResponse:
        """Return query and model usage analytics."""
        source_stats = await self.get_source_stats()

        total_q = await self._count_queries()
        completed_q = await self._count_queries(status=QueryStatus.COMPLETED)
        failed_q = await self._count_queries(status=QueryStatus.FAILED)
        refused_q = await self._count_refused()
        daily = await self._daily_query_counts(days=7)
        models = await self._model_usage()
        avg_latency = await self._average_latency_ms()

        refusal_rate = round(refused_q / completed_q, 3) if completed_q else 0.0

        return AdminAnalyticsResponse(
            total_sources=source_stats.total_sources,
            authenticated_sources=source_stats.authenticated_sources,
            pending_sources=source_stats.pending_sources,
            total_queries=total_q,
            completed_queries=completed_q,
            failed_queries=failed_q,
            refused_queries=refused_q,
            refusal_rate=refusal_rate,
            average_latency_ms=avg_latency,
            queries_by_day=daily,
            model_usage=models,
        )

    async def _count_queries(self, *, status: QueryStatus | None = None) -> int:
        stmt = select(func.count()).select_from(Query)
        if status is not None:
            stmt = stmt.where(Query.status == status)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def _count_refused(self) -> int:
        stmt = select(func.count()).select_from(Response).where(Response.refused.is_(True))
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def _daily_query_counts(self, *, days: int) -> list[AdminDailyQueryCount]:
        since = datetime.now(UTC) - timedelta(days=days - 1)
        stmt = (
            select(func.date_trunc("day", Query.created_at).label("day"), func.count())
            .where(Query.created_at >= since)
            .group_by("day")
            .order_by("day")
        )
        result = await self.session.execute(stmt)
        rows = {row.day.date().isoformat(): int(row.count) for row in result.all()}

        output: list[AdminDailyQueryCount] = []
        for offset in range(days):
            day = (datetime.now(UTC) - timedelta(days=days - 1 - offset)).date()
            key = day.isoformat()
            output.append(AdminDailyQueryCount(date=key, count=rows.get(key, 0)))
        return output

    async def _model_usage(self, *, limit: int = 80) -> list[AdminModelUsage]:
        stmt = (
            select(Response.execution_metrics)
            .where(Response.execution_metrics.isnot(None))
            .order_by(Response.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        counter: Counter[str] = Counter()
        for (metrics,) in result.all():
            if not isinstance(metrics, dict):
                continue
            for model in metrics.get("models_used") or []:
                if isinstance(model, str) and model.strip():
                    counter[model.strip()] += 1
        return [
            AdminModelUsage(model=name, count=count)
            for name, count in counter.most_common(12)
        ]

    async def _average_latency_ms(self) -> float | None:
        stmt = (
            select(Response.execution_metrics)
            .where(Response.execution_metrics.isnot(None))
            .order_by(Response.created_at.desc())
            .limit(100)
        )
        result = await self.session.execute(stmt)
        latencies: list[float] = []
        for (metrics,) in result.all():
            if not isinstance(metrics, dict):
                continue
            value = metrics.get("total_latency_ms")
            if isinstance(value, (int, float)):
                latencies.append(float(value))
        if not latencies:
            return None
        return round(sum(latencies) / len(latencies), 1)

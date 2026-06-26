"""Query service — orchestrates agents, repositories, and persistence."""

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from agents.response_builder.models import FinalResponse
from backend.app.agents.agent_orchestrator import AgentOrchestrator
from backend.app.config.database import AsyncSessionLocal
from backend.app.config.settings import get_settings
from backend.app.exceptions import ForbiddenError, NoEvidenceError, NotFoundError
from backend.app.models.enums import QueryStatus
from backend.app.models.query import Query
from backend.app.models.response import Response
from backend.app.models.user import User
from backend.app.repositories.query_repository import QueryRepository
from backend.app.repositories.response_repository import ResponseRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.services.user_preferences_service import UserPreferencesService
from backend.app.schemas.query_schemas import (
    AgentTraceSchema,
    ConfidenceBreakdownSchema,
    EvidenceSchema,
    ExecutionMetricsSchema,
    FinancialContextSchema,
    MadhhabPositionSchema,
    OpinionSchema,
    PrincipleSchema,
    QueryCreateRequest,
    QueryExportResponse,
    QueryListItemSchema,
    QueryListResponse,
    QueryResultSchema,
    QueryUpdateRequest,
    SourceSchema,
)
from backend.app.services.query_export import build_query_markdown
from backend.app.services.query_trace_cache import clear as clear_live_trace
from backend.app.services.query_trace_cache import get_draft_answer
from backend.app.services.query_trace_cache import get_trace as get_live_trace

logger = logging.getLogger(__name__)


class QueryService:
    """Business logic for Shariah reasoning queries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.query_repo = QueryRepository(session)
        self.response_repo = ResponseRepository(session)
        self.orchestrator = AgentOrchestrator(session)
        self.settings = get_settings()

    async def submit_query(self, user: User, request: QueryCreateRequest) -> QueryResultSchema:
        """Process a user query through the multi-agent pipeline."""
        if self.settings.query_async:
            return await self.enqueue_query(user, request)
        return await self._submit_query_sync(user, request)

    async def enqueue_query(self, user: User, request: QueryCreateRequest) -> QueryResultSchema:
        """Create a query record and return immediately for background processing."""
        language = request.language or "ar"
        query = Query(
            user_id=user.id,
            question=request.question,
            language=language,
            status=QueryStatus.PROCESSING,
            session_id=request.session_id,
        )
        await self.query_repo.create(query)
        return QueryResultSchema(
            query_id=query.id,
            status=QueryStatus.PROCESSING,
            question=request.question,
            language=language,
            created_at=query.created_at,
        )

    async def _submit_query_sync(
        self,
        user: User,
        request: QueryCreateRequest,
    ) -> QueryResultSchema:
        """Run the full pipeline synchronously (used in tests)."""
        language = request.language or "ar"
        query = Query(
            user_id=user.id,
            question=request.question,
            language=language,
            status=QueryStatus.PENDING,
            session_id=request.session_id,
        )
        await self.query_repo.create(query)
        await self._run_pipeline(query, request)
        await self.session.refresh(query)
        if query.status == QueryStatus.FAILED:
            raise NoEvidenceError(
                "No authenticated sources found.",
                details={"query_id": str(query.id)},
            )
        response = await self.response_repo.get_by_query_id(query.id)
        if response is None:
            return QueryResultSchema(
                query_id=query.id,
                status=query.status,
                question=query.question,
                language=query.language,
                refused=query.status == QueryStatus.FAILED,
                refusal_reason=(
                    "No authenticated sources found."
                    if query.status == QueryStatus.FAILED
                    else None
                ),
                created_at=query.created_at,
            )
        final = self._final_from_response(response, query.language)
        return self._to_result_schema(query, final)

    async def _run_pipeline(self, query: Query, request: QueryCreateRequest) -> None:
        """Execute orchestrator and persist or mark query failed."""
        await self.query_repo.update_status(query, QueryStatus.PROCESSING)
        history = None
        if request.conversation_history:
            history = [turn.model_dump() for turn in request.conversation_history]

        final = await self.orchestrator.process_query(
            request.question,
            user_id=query.user_id,
            advanced_analysis=request.advanced_analysis,
            preferred_language=request.language or query.language or "ar",
            fanar_model=request.fanar_model,
            session_id=query.session_id,
            conversation_history=history,
            query_id=query.id,
        )

        if final.refused:
            await self._persist_response(query, final)
            await self.query_repo.update_status(query, QueryStatus.FAILED)
            return

        await self._persist_response(query, final)
        await self.query_repo.update_status(query, QueryStatus.COMPLETED)
        await self._record_user_topic(query, request.question)

    async def get_query(self, user: User, query_id: uuid.UUID) -> QueryResultSchema:
        """Fetch a single query and its response."""
        query = await self.query_repo.get_by_id(query_id)
        if query is None:
            raise NotFoundError(f"Query {query_id} not found.")
        if query.user_id != user.id:
            raise ForbiddenError("You do not have access to this query.")

        response = await self.response_repo.get_by_query_id(query_id)
        if response is None:
            live_trace = get_live_trace(query_id) or []
            draft_summary = get_draft_answer(query_id)
            return QueryResultSchema(
                query_id=query.id,
                status=query.status,
                question=query.question,
                language=query.language,
                refused=query.status == QueryStatus.FAILED,
                refusal_reason=(
                    "No authenticated sources found."
                    if query.status == QueryStatus.FAILED
                    else None
                ),
                agent_trace=[AgentTraceSchema(**step) for step in live_trace],
                draft_summary=draft_summary,
                created_at=query.created_at,
            )

        return self._to_result_schema_from_orm(query, response)

    async def list_queries(
        self,
        user: User,
        *,
        limit: int = 50,
        offset: int = 0,
        include_archived: bool = False,
    ) -> QueryListResponse:
        """Return paginated query history for a user."""
        queries = await self.query_repo.list_by_user(
            user.id,
            limit=limit,
            offset=offset,
            include_archived=include_archived,
        )
        items: list[QueryListItemSchema] = []

        for query in queries:
            response = await self.response_repo.get_by_query_id(query.id)
            items.append(self._to_list_item(query, response))

        return QueryListResponse(items=items, total=len(items), limit=limit, offset=offset)

    async def update_query(
        self,
        user: User,
        query_id: uuid.UUID,
        request: QueryUpdateRequest,
    ) -> QueryListItemSchema:
        """Update conversation metadata (rename, archive, folder, tags)."""
        query = await self._get_owned_query(user, query_id)
        data = request.model_dump(exclude_unset=True)
        await self.query_repo.update_metadata(
            query,
            display_title=data.get("display_title"),
            archived=data.get("archived"),
            folder=data.get("folder"),
            tags=data.get("tags"),
            unset_folder=data.get("folder") == "",
        )
        response = await self.response_repo.get_by_query_id(query.id)
        return self._to_list_item(query, response)

    async def delete_query(self, user: User, query_id: uuid.UUID) -> None:
        """Permanently delete a conversation."""
        query = await self._get_owned_query(user, query_id)
        await self.query_repo.delete(query)

    async def export_query(
        self,
        user: User,
        query_id: uuid.UUID,
    ) -> QueryExportResponse:
        """Export a query response as markdown."""
        query = await self._get_owned_query(user, query_id)
        response = await self.response_repo.get_by_query_id(query.id)
        content = build_query_markdown(query, response)
        slug = query.id.hex[:8]
        return QueryExportResponse(
            query_id=query.id,
            filename=f"sanad-{slug}.md",
            content=content,
        )

    async def _record_user_topic(self, query: Query, question: str) -> None:
        """Track recent topics in user preferences for cross-session memory."""
        user_repo = UserRepository(self.session)
        user = await user_repo.get_by_id(query.user_id)
        if user is None:
            return
        service = UserPreferencesService(user_repo)
        topic = question.strip()[:200]
        await service.record_recent_topic(user, topic)

    async def _get_owned_query(self, user: User, query_id: uuid.UUID) -> Query:
        query = await self.query_repo.get_by_id(query_id)
        if query is None:
            raise NotFoundError(f"Query {query_id} not found.")
        if query.user_id != user.id:
            raise ForbiddenError("You do not have access to this query.")
        return query

    @staticmethod
    def _to_list_item(query: Query, response: Response | None) -> QueryListItemSchema:
        return QueryListItemSchema(
            query_id=query.id,
            question=query.question,
            display_title=query.display_title,
            language=query.language,
            status=query.status,
            summary=response.summary if response else None,
            confidence=response.confidence if response else 0.0,
            refused=query.status == QueryStatus.FAILED,
            archived=query.archived,
            folder=query.folder,
            tags=list(query.tags or []),
            session_id=query.session_id,
            turn_count=1,
            created_at=query.created_at,
        )

    async def _persist_response(self, query: Query, final: FinalResponse) -> Response:
        response = Response(
            query_id=query.id,
            summary=final.summary,
            evidence=[e.model_dump() for e in final.evidence],
            principles=[p.model_dump() for p in final.principles],
            reasoning=final.reasoning,
            opinions=[o.model_dump() for o in final.opinions],
            sources=final.sources,
            confidence=final.confidence,
            confidence_breakdown=final.confidence_breakdown,
            agent_trace=final.agent_trace,
            thinking_trace=final.thinking_trace,
            financial_context=final.financial_context,
            execution_metrics=final.execution_metrics,
            madhhab_matrix=final.madhhab_matrix,
            suggested_questions=final.suggested_questions,
            refused=final.refused,
            refusal_reason=final.refusal_reason,
        )
        created = await self.response_repo.create(response)
        clear_live_trace(query.id)
        return created

    @staticmethod
    def _final_from_response(response: Response, language: str) -> FinalResponse:
        from agents.common.evidence import EvidenceItem
        from agents.knowledge_agent.models import JurisprudentialPrinciple
        from agents.reasoning_agent.models import ScholarlyOpinion

        return FinalResponse(
            summary=response.summary,
            evidence=[EvidenceItem(**e) for e in response.evidence],
            principles=[JurisprudentialPrinciple(**p) for p in response.principles],
            reasoning=response.reasoning,
            opinions=[ScholarlyOpinion(**o) for o in response.opinions],
            sources=response.sources,
            confidence=response.confidence,
            language=language,
            agent_trace=response.agent_trace or [],
            financial_context=response.financial_context,
            execution_metrics=response.execution_metrics,
            madhhab_matrix=response.madhhab_matrix or [],
            suggested_questions=list(response.suggested_questions or []),
        )

    @staticmethod
    def _schema_from_final(final: FinalResponse) -> dict:
        """Shared field mapping for QueryResultSchema construction."""
        return {
            "summary": final.summary,
            "evidence": [EvidenceSchema(**e.model_dump()) for e in final.evidence],
            "principles": [PrincipleSchema(**p.model_dump()) for p in final.principles],
            "reasoning": final.reasoning,
            "opinions": [OpinionSchema(**o.model_dump()) for o in final.opinions],
            "sources": [SourceSchema(**s) for s in final.sources],
            "confidence": final.confidence,
            "confidence_breakdown": (
                ConfidenceBreakdownSchema(**final.confidence_breakdown)
                if final.confidence_breakdown
                else None
            ),
            "refused": final.refused,
            "refusal_reason": final.refusal_reason,
            "agent_trace": [AgentTraceSchema(**t) for t in final.agent_trace],
            "thinking_trace": final.thinking_trace,
            "financial_context": (
                FinancialContextSchema(**final.financial_context)
                if final.financial_context
                else None
            ),
            "execution_metrics": (
                ExecutionMetricsSchema(**final.execution_metrics)
                if final.execution_metrics
                else None
            ),
            "madhhab_matrix": [
                MadhhabPositionSchema(**m) for m in (final.madhhab_matrix or [])
            ],
            "suggested_questions": list(final.suggested_questions or []),
        }

    def _to_result_schema(self, query: Query, final: FinalResponse) -> QueryResultSchema:
        return QueryResultSchema(
            query_id=query.id,
            status=QueryStatus.COMPLETED,
            question=query.question,
            language=final.language,
            created_at=query.created_at,
            **self._schema_from_final(final),
        )

    def _to_result_schema_from_orm(self, query: Query, response: Response) -> QueryResultSchema:
        final = self._final_from_response(response, query.language)
        final.refused = response.refused or query.status == QueryStatus.FAILED
        final.refusal_reason = response.refusal_reason
        return QueryResultSchema(
            query_id=query.id,
            status=query.status,
            question=query.question,
            language=query.language,
            created_at=query.created_at,
            **self._schema_from_final(final),
        )


async def process_query_background(query_id: uuid.UUID, request: QueryCreateRequest) -> None:
    """Background worker for async query processing."""
    from agents.response_builder.tools import build_refusal_response

    async with AsyncSessionLocal() as session:
        service = QueryService(session)
        query = await service.query_repo.get_by_id(query_id)
        if query is None:
            logger.warning("Background query not found: %s", query_id)
            return

        try:
            await service._run_pipeline(query, request)
            await session.commit()
        except Exception as exc:
            logger.exception("Background query processing failed: %s", query_id)
            await session.rollback()
            async with AsyncSessionLocal() as fail_session:
                fail_repo = QueryRepository(fail_session)
                fail_response_repo = ResponseRepository(fail_session)
                failed_query = await fail_repo.get_by_id(query_id)
                if failed_query and failed_query.status not in (
                    QueryStatus.COMPLETED,
                    QueryStatus.FAILED,
                ):
                    refusal = build_refusal_response(
                        "Analysis could not be completed. Please try again.",
                        language=failed_query.language,
                    )
                    await fail_response_repo.create(
                        Response(
                            query_id=failed_query.id,
                            summary=refusal.summary,
                            evidence=[],
                            principles=[],
                            reasoning=refusal.reasoning,
                            opinions=[],
                            sources=[],
                            confidence=0.0,
                            confidence_breakdown={},
                            agent_trace=[],
                            thinking_trace=None,
                            refused=True,
                            refusal_reason=refusal.refusal_reason,
                        )
                    )
                    await fail_repo.update_status(failed_query, QueryStatus.FAILED)
                clear_live_trace(query_id)
                await fail_session.commit()

"""Source management service with audit logging."""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.exceptions import NotFoundError, ValidationError
from backend.app.models.audit_log import AuditLog
from backend.app.models.enums import SourceType
from backend.app.models.source import Source
from backend.app.models.user import User
from backend.app.repositories.audit_log_repository import AuditLogRepository
from backend.app.repositories.source_repository import SourceRepository
from backend.app.schemas.source_schemas import (
    AdminStatsResponse,
    SourceCreateRequest,
    SourceListResponse,
    SourceResponse,
    SourceUpdateRequest,
)


class SourceService:
    """Business logic for admin source management."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.source_repo = SourceRepository(session)
        self.audit_repo = AuditLogRepository(session)

    async def list_sources(
        self,
        *,
        is_authenticated: bool | None = None,
        source_type: SourceType | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> SourceListResponse:
        """Return paginated sources for admin review."""
        items = await self.source_repo.list_filtered(
            is_authenticated=is_authenticated,
            source_type=source_type,
            limit=limit,
            offset=offset,
        )
        total = await self.source_repo.count_filtered(
            is_authenticated=is_authenticated,
            source_type=source_type,
        )
        return SourceListResponse(
            items=[self._to_response(source) for source in items],
            total=total,
        )

    async def create_source(
        self,
        actor: User,
        request: SourceCreateRequest,
    ) -> SourceResponse:
        """Add a new knowledge source (pending review by default)."""
        source = Source(
            title=request.title.strip(),
            author=request.author.strip(),
            source_type=request.source_type,
            language=request.language,
            url=str(request.url) if request.url else None,
            is_authenticated=request.is_authenticated,
        )
        created = await self.source_repo.create(source)
        await self._log_action(
            actor,
            action="source.create",
            resource=f"sources/{created.id}",
            details={
                "title": created.title,
                "is_authenticated": created.is_authenticated,
            },
        )
        return self._to_response(created)

    async def update_source(
        self,
        actor: User,
        source_id: uuid.UUID,
        request: SourceUpdateRequest,
    ) -> SourceResponse:
        """Update source metadata or authentication status."""
        source = await self.source_repo.get_by_id(source_id)
        if source is None:
            raise NotFoundError("Source not found.")

        updates = request.model_dump(exclude_unset=True)
        if not updates:
            raise ValidationError("No fields provided for update.")

        changes: dict[str, Any] = {}
        for field, value in updates.items():
            if field == "url":
                normalized = str(value) if value is not None else None
                if normalized != source.url:
                    changes["url"] = normalized
                    source.url = normalized
            elif field in {"title", "author"} and value is not None:
                normalized = value.strip()
                if getattr(source, field) != normalized:
                    changes[field] = normalized
                    setattr(source, field, normalized)
            elif getattr(source, field) != value:
                changes[field] = value.value if hasattr(value, "value") else value
                setattr(source, field, value)

        if not changes:
            return self._to_response(source)

        await self.session.flush()
        await self.session.refresh(source)
        await self._log_action(
            actor,
            action="source.update",
            resource=f"sources/{source.id}",
            details=changes,
        )
        return self._to_response(source)

    async def delete_source(
        self,
        actor: User,
        source_id: uuid.UUID,
    ) -> None:
        """Remove a source from the knowledge base."""
        source = await self.source_repo.get_by_id(source_id)
        if source is None:
            raise NotFoundError("Source not found.")

        await self._log_action(
            actor,
            action="source.delete",
            resource=f"sources/{source.id}",
            details={"title": source.title},
        )
        await self.source_repo.delete(source)

    async def get_admin_stats(self) -> AdminStatsResponse:
        """Return dashboard metrics for source oversight."""
        total = await self.source_repo.count_filtered()
        authenticated = await self.source_repo.count_authenticated()
        pending = await self.source_repo.count_pending()
        return AdminStatsResponse(
            total_sources=total,
            authenticated_sources=authenticated,
            pending_sources=pending,
        )

    async def _log_action(
        self,
        actor: User,
        *,
        action: str,
        resource: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        await self.audit_repo.create(
            AuditLog(
                user_id=actor.id,
                action=action,
                resource=resource,
                details=details,
            )
        )

    @staticmethod
    def _to_response(source: Source) -> SourceResponse:
        return SourceResponse(
            id=str(source.id),
            title=source.title,
            author=source.author,
            source_type=source.source_type.value,
            language=source.language,
            url=source.url,
            is_authenticated=source.is_authenticated,
            created_at=source.created_at,
        )

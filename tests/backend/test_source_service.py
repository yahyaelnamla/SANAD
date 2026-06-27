"""Unit tests for SourceService."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.auth.security import hash_password
from backend.app.exceptions import NotFoundError, ValidationError
from backend.app.models.enums import SourceType, UserRole
from backend.app.models.user import User
from backend.app.repositories.audit_log_repository import AuditLogRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.source_schemas import SourceCreateRequest, SourceUpdateRequest
from backend.app.services.source_service import SourceService


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    repo = UserRepository(db_session)
    return await repo.create(
        User(
            email="service-admin@example.com",
            password_hash=hash_password("SecurePass123!"),
            role=UserRole.ADMIN,
            locale="en",
        )
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_source_writes_audit_log(
    db_session: AsyncSession,
    admin_user: User,
) -> None:
    service = SourceService(db_session)
    result = await service.create_source(
        admin_user,
        SourceCreateRequest(
            title="Unit Test Source",
            author="Tester",
            source_type=SourceType.CLASSICAL,
            language="ar",
        ),
    )

    assert result.title == "Unit Test Source"
    assert result.is_authenticated is False

    audit_repo = AuditLogRepository(db_session)
    logs = await audit_repo.list_by_user(admin_user.id)
    assert any(log.action == "source.create" for log in logs)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_source_authentication(
    db_session: AsyncSession,
    admin_user: User,
) -> None:
    service = SourceService(db_session)
    created = await service.create_source(
        admin_user,
        SourceCreateRequest(
            title="Pending Source",
            author="Board",
            source_type=SourceType.FATWA,
            language="en",
            is_authenticated=False,
        ),
    )

    updated = await service.update_source(
        admin_user,
        uuid.UUID(created.id),
        SourceUpdateRequest(is_authenticated=True),
    )
    assert updated.is_authenticated is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_missing_source_raises(
    db_session: AsyncSession,
    admin_user: User,
) -> None:
    service = SourceService(db_session)
    with pytest.raises(NotFoundError):
        await service.update_source(
            admin_user,
            uuid.uuid4(),
            SourceUpdateRequest(title="Missing"),
        )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_with_empty_payload_raises(
    db_session: AsyncSession,
    admin_user: User,
) -> None:
    service = SourceService(db_session)
    created = await service.create_source(
        admin_user,
        SourceCreateRequest(
            title="Source",
            author="Author",
            source_type=SourceType.STANDARD,
            language="en",
        ),
    )

    with pytest.raises(ValidationError):
        await service.update_source(
            admin_user,
            uuid.UUID(created.id),
            SourceUpdateRequest(),
        )

"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.admin import router as admin_router
from backend.app.api.auth import router as auth_router
from backend.app.api.billing import router as billing_router
from backend.app.api.conversations import router as conversations_router
from backend.app.api.evaluation import router as evaluation_router
from backend.app.api.health import router as health_router
from backend.app.api.knowledge import router as knowledge_router
from backend.app.api.platform import router as platform_router
from backend.app.api.queries import router as queries_router
from backend.app.api.scholars import router as scholars_router
from backend.app.api.search import router as search_router
from backend.app.api.sources import router as sources_router
from backend.app.api.sso import router as sso_router
from backend.app.api.tools import router as tools_router
from backend.app.config.database import init_database
from backend.app.config.settings import get_settings
from backend.app.exceptions import SANADError
from backend.app.schemas.error_schemas import ErrorResponse
from backend.app.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup/shutdown hooks."""
    await init_database()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    setup_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        description="AI-Powered Shariah Financial Reasoning Platform",
        version=settings.app_version,
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(SANADError)
    async def sanad_error_handler(_request: Request, exc: SANADError) -> JSONResponse:
        """Map application exceptions to structured JSON error responses."""
        body = ErrorResponse(code=exc.code, message=exc.message, details=exc.details)
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(sso_router, prefix=settings.api_prefix)
    app.include_router(billing_router, prefix=settings.api_prefix)
    app.include_router(queries_router, prefix=settings.api_prefix)
    app.include_router(conversations_router, prefix=settings.api_prefix)
    app.include_router(search_router, prefix=settings.api_prefix)
    app.include_router(knowledge_router, prefix=settings.api_prefix)
    app.include_router(sources_router, prefix=settings.api_prefix)
    app.include_router(tools_router, prefix=settings.api_prefix)
    app.include_router(admin_router, prefix=settings.api_prefix)
    app.include_router(evaluation_router, prefix=settings.api_prefix)
    app.include_router(platform_router, prefix=settings.api_prefix)
    app.include_router(scholars_router, prefix=settings.api_prefix)

    return app


app = create_app()

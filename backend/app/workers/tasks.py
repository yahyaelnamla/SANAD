"""Celery background tasks for SANAD."""

from __future__ import annotations

import logging

from backend.app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="sanad.ping")
def ping() -> str:
    """Health-check task to verify worker connectivity."""
    return "pong"


@celery_app.task(name="sanad.process_query_async", bind=True)
def process_query_async(self, query_id: str) -> dict[str, str]:
    """Placeholder for future async Shariah query processing.

    The synchronous API path remains authoritative for the explainability chain.
    This task reserves the Celery queue for long-running ingestion or batch jobs.
    """
    logger.info("Async query task queued for query_id=%s", query_id)
    return {"query_id": query_id, "status": "queued"}

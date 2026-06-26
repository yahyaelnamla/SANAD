FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY alembic/ ./alembic/
COPY backend/ ./backend/
COPY config/ ./config/
COPY agents/ ./agents/
COPY rag/ ./rag/
COPY scripts/docker-set-database-url.sh ./scripts/docker-set-database-url.sh
COPY scripts/celery-entrypoint.sh ./scripts/celery-entrypoint.sh
COPY scripts/docker-entrypoint.sh ./scripts/docker-entrypoint.sh
RUN sed -i 's/\r$//' ./scripts/docker-set-database-url.sh ./scripts/celery-entrypoint.sh ./scripts/docker-entrypoint.sh && \
    chmod +x ./scripts/docker-set-database-url.sh ./scripts/celery-entrypoint.sh ./scripts/docker-entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/live || exit 1

ENTRYPOINT ["./scripts/docker-entrypoint.sh"]

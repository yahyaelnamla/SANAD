#!/usr/bin/env bash
set -euo pipefail

source ./scripts/docker-set-database-url.sh

exec celery -A backend.app.workers.celery_app:celery_app worker --loglevel=info "$@"

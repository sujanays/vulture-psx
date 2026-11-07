#!/usr/bin/env sh
set -e

# Start Celery worker in background
celery -A backend.worker.celery_app worker --loglevel=info --concurrency=2 &

# Start Uvicorn web server in foreground
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
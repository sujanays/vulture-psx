#!/usr/bin/env sh

# Exit immediately if a command exits with a non-zero status
set -e

# 1. Start Celery worker in the background (&)
celery -A backend.worker.celery_app worker --loglevel=info --concurrency=2 &

# 2. Start Uvicorn in the foreground (binds to Render's $PORT)
exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
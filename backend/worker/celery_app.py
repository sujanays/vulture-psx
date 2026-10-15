from __future__ import annotations

from celery import Celery
import os

# Redis broker URL – default to localhost; can be overridden via env var
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery('vulture_scanner', broker=REDIS_URL, backend=REDIS_URL)

# Optional: configure task serialization, result expiration, etc.
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_expires=3600,  # keep results for 1 hour
    timezone='UTC',
    enable_utc=True,
)

# Autodiscover tasks in the 'scanner' package
celery_app.autodiscover_tasks(['scanner'])

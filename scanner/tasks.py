from __future__ import annotations

from celery import shared_task
from .utils import run_all_checks

@shared_task(name='scanner.tasks.perform_scan')
def perform_scan(url: str) -> dict:
    """Celery task that runs the full security scan.
    Returns the JSON‑serialisable results produced by ``run_all_checks``.
    """
    # run_all_checks is async; we need to run the event loop here
    import asyncio
    return asyncio.run(run_all_checks(url))

from __future__ import annotations

import asyncio
from celery import shared_task
from .utils import run_all_checks
from backend.db.database import update_scan_status

@shared_task(bind=True, name='scanner.tasks.perform_scan')
def perform_scan(self, url: str) -> dict:
    """Celery task that runs the full security scan and updates the database.
    """
    task_id = self.request.id
    update_scan_status(task_id=task_id, status="STARTED")
    try:
        results = asyncio.run(run_all_checks(url))
        score = results.get("score", 0)
        grade = results.get("grade", "F")
        update_scan_status(
            task_id=task_id,
            status="SUCCESS",
            score=score,
            grade=grade,
            result_json=results
        )
        return results
    except Exception as e:
        update_scan_status(
            task_id=task_id,
            status="FAILURE",
            error=str(e)
        )
        raise e

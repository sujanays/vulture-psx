from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from uuid import uuid4
from ..worker.celery_app import celery_app
from ..scanner.utils import run_all_checks
import asyncio

router = APIRouter()

class ScanRequest(BaseModel):
    url: HttpUrl

class ScanStatusResponse(BaseModel):
    task_id: str
    status: str
    result: dict | None = None

@router.post('/scan/', response_model=ScanStatusResponse)
async def trigger_scan(request: ScanRequest):
    # launch Celery task
    task = celery_app.send_task('scanner.tasks.perform_scan', args=[str(request.url)], task_id=str(uuid4()))
    return ScanStatusResponse(task_id=task.id, status='PENDING')

@router.get('/scan/{task_id}/status', response_model=ScanStatusResponse)
async def get_scan_status(task_id: str):
    async_result = celery_app.AsyncResult(task_id)
    if async_result.state == 'PENDING':
        return ScanStatusResponse(task_id=task_id, status='PENDING')
    elif async_result.state == 'FAILURE':
        raise HTTPException(status_code=500, detail=str(async_result.result))
    else:  # SUCCESS or other states
        result = async_result.result if async_result.result else None
        return ScanStatusResponse(task_id=task_id, status=async_result.state, result=result)

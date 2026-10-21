from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, HttpUrl
from uuid import uuid4
from typing import Dict, List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..worker.celery_app import celery_app
from ..db.database import (
    create_scan,
    update_scan_status,
    get_scan,
    list_scans,
    delete_scan
)
from ..services.pdf_generator import generate_pdf_report

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

from pydantic import BaseModel, field_validator

class ScanRequest(BaseModel):
    url: str

    @field_validator('url')
    @classmethod
    def validate_and_normalize_url(cls, v: str) -> str:
        clean = str(v).strip()
        if not clean:
            raise ValueError("URL cannot be empty")

        scheme = "https://"
        rest = clean
        if clean.lower().startswith("http://"):
            scheme = "http://"
            rest = clean[7:]
        elif clean.lower().startswith("https://"):
            scheme = "https://"
            rest = clean[8:]

        slash_idx = rest.find("/")
        domain = rest[:slash_idx] if slash_idx != -1 else rest
        path = rest[slash_idx:] if slash_idx != -1 else ""

        domain_parts = domain.split(".")
        if len(domain_parts) == 2 and not domain.lower().startswith("www."):
            domain = f"www.{domain}"

        return f"{scheme}{domain}{path}"


class ScanStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None

@router.post('/scan/', response_model=ScanStatusResponse)
@limiter.limit("10/minute")
async def trigger_scan(request: Request, body: ScanRequest):
    task_id = str(uuid4())
    url_str = str(body.url)
    
    # Store initial record in SQLite
    create_scan(task_id=task_id, url=url_str)
    
    # Launch Celery background task
    celery_app.send_task(
        'scanner.tasks.perform_scan',
        args=[url_str],
        task_id=task_id
    )
    
    return ScanStatusResponse(task_id=task_id, status='PENDING')

@router.get('/scan/{task_id}/status', response_model=ScanStatusResponse)
async def get_scan_status(task_id: str):
    # Check DB first
    scan_row = get_scan(task_id)
    if scan_row and scan_row.get("status") in ("SUCCESS", "FAILURE"):
        return ScanStatusResponse(
            task_id=task_id,
            status=scan_row["status"],
            result=scan_row.get("result"),
            error=scan_row.get("error")
        )

    # Check Celery AsyncResult
    async_result = celery_app.AsyncResult(task_id)
    state = async_result.state

    if state in ('PENDING', 'STARTED'):
        return ScanStatusResponse(task_id=task_id, status=state)
    elif state == 'FAILURE':
        err_msg = str(async_result.result)
        update_scan_status(task_id=task_id, status='FAILURE', error=err_msg)
        return ScanStatusResponse(task_id=task_id, status='FAILURE', error=err_msg)
    elif state == 'SUCCESS':
        res = async_result.result if async_result.result else {}
        update_scan_status(
            task_id=task_id,
            status='SUCCESS',
            score=res.get("score", 0),
            grade=res.get("grade", "F"),
            result_json=res
        )
        return ScanStatusResponse(task_id=task_id, status='SUCCESS', result=res)
    else:
        return ScanStatusResponse(task_id=task_id, status=state)

@router.get('/scan/{task_id}')
async def get_scan_details(task_id: str):
    scan = get_scan(task_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan record not found.")
    return scan

@router.get('/scan/{task_id}/pdf')
async def download_scan_pdf(task_id: str):
    scan = get_scan(task_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    
    if scan.get("status") != "SUCCESS" or not scan.get("result"):
        # If DB doesn't have it yet, check Celery
        async_result = celery_app.AsyncResult(task_id)
        if async_result.state == "SUCCESS":
            scan["result"] = async_result.result
        else:
            raise HTTPException(status_code=400, detail="Scan is still in progress or failed. Cannot generate PDF.")

    try:
        pdf_bytes = generate_pdf_report(scan)
        domain = scan.get("url", "report").replace("https://", "").replace("http://", "").replace("/", "_")
        filename = f"vulture_report_{domain}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@router.get('/scans/', response_model=List[Dict])
async def list_recent_scans():
    """Return a list of recent scan records from persistent database storage."""
    return list_scans(limit=50)

@router.delete('/scan/{task_id}')
async def delete_scan_record(task_id: str):
    success = delete_scan(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return {"message": "Scan deleted successfully", "task_id": task_id}

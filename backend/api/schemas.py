from pydantic import BaseModel, HttpUrl
from typing import Dict, List, Optional

class ScanRequest(BaseModel):
    url: HttpUrl

class ScanResult(BaseModel):
    url: str
    score: int
    grade: str
    details: Dict
    passed: List[str]
    failed: List[str]

class ScanStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[ScanResult] = None

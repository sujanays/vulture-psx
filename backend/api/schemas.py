from pydantic import BaseModel, field_validator
from typing import Dict, List, Optional

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
    error: Optional[str] = None

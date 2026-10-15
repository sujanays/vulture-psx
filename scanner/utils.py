"""Utility helpers for the scanner package.

Provides:
- async HTTP fetch (`fetch_url`)
- grade calculation (`calculate_grade`)
- aggregation (`run_all_checks`)
"""

import httpx
from typing import Dict, List
from .header_analysis import evaluate as evaluate_headers
from .ssl_inspection import evaluate as evaluate_ssl
from .cms_detection import evaluate as evaluate_cms

async def fetch_url(url: str, timeout: int = 10) -> httpx.Response:
    """Async GET request returning the httpx.Response.
    Raises httpx.RequestError on failure.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        return await client.get(url)

def calculate_grade(score: int) -> str:
    """Map numeric score (0‑100) to a letter grade.
    Simple thresholds: A (90+), B (80‑89), C (70‑79), D (60‑69), F (<60).
    """
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"

async def run_all_checks(url: str) -> Dict:
    """Execute all scanning modules for a given URL.
    Returns a JSON‑serialisable dict with overall score, grade, and per‑module details.
    """
    # Header analysis – need raw headers, we can fetch via httpx
    try:
        resp = await fetch_url(url)
        headers = {k.lower(): v for k, v in resp.headers.items()}
        header_res = evaluate_headers(headers)
    except Exception as e:
        header_res = {"score": -30, "details": {}, "error": str(e)}

    # SSL/TLS inspection – use hostname only (strip scheme)
    from urllib.parse import urlparse
    hostname = urlparse(url).hostname or ""
    ssl_res = evaluate_ssl(hostname) if hostname else {"valid": False, "error": "Invalid hostname"}

    # CMS detection – need HTML content
    try:
        html = resp.text if 'resp' in locals() else ""
        cms_res = evaluate_cms(url)
    except Exception as e:
        cms_res = {"findings": [], "score": -10, "error": str(e)}

    # Aggregate scores
    total_score = 0
    passed: List[str] = []
    failed: List[str] = []

    # Header score
    total_score += header_res.get("score", 0)
    for k, v in header_res.get("details", {}).items():
        (passed if v else failed).append(f"Header {k}")

    # SSL score – convert exp_score to points (0‑10) if valid
    if ssl_res.get("valid"):
        total_score += ssl_res.get("exp_score", 0)
        passed.append("SSL certificate validity")
        if ssl_res.get("cipher_strength") == "strong":
            total_score += 10
            passed.append("Strong cipher suite")
        else:
            failed.append("Weak cipher suite")
    else:
        total_score -= 20
        failed.append("SSL/TLS validation")

    # CMS score
    total_score += cms_res.get("score", 0)
    for finding in cms_res.get("findings", []):
        failed.append(f"CMS finding: {finding}")

    # Clamp score between 0 and 100
    total_score = max(0, min(100, total_score))
    grade = calculate_grade(total_score)

    return {
        "url": url,
        "score": total_score,
        "grade": grade,
        "details": {
            "headers": header_res.get("details", {}),
            "ssl": {
                "valid": ssl_res.get("valid"),
                "cipher_strength": ssl_res.get("cipher_strength"),
                "expires_in_days": ssl_res.get("exp_score")  # approximate mapping
            },
            "cms": cms_res.get("findings", [])
        },
        "passed": passed,
        "failed": failed
    }

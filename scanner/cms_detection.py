"""CMS detection module.

Provides simple detection of common CMS platforms via HTML meta tags and HTTP headers.
"""

import httpx
from bs4 import BeautifulSoup
from typing import Dict, List

def _detect_cms(html: str, headers: Dict[str, str]) -> List[str]:
    findings: List[str] = []
    # Meta generator tag
    soup = BeautifulSoup(html, "html.parser")
    generator = soup.find("meta", attrs={"name": "generator"})
    if generator and generator.get("content"):
        findings.append(f"Generator meta: {generator['content']}")
    # X-Powered-By header
    powered = headers.get("x-powered-by")
    if powered:
        findings.append(f"X-Powered-By: {powered}")
    return findings

def evaluate(url: str) -> Dict:
    """Fetch the URL, run CMS detection, and return a score.
    Returns a dict with:
    - ``findings``: list of strings describing detected CMS info
    - ``score``: integer penalty (‑10 per outdated detection)
    """
    try:
        resp = httpx.get(url, timeout=10.0)
        html = resp.text
        headers = {k.lower(): v for k, v in resp.headers.items()}
        cms_findings = _detect_cms(html, headers)
        score = 0
        for item in cms_findings:
            lowered = item.lower()
            # simple outdated version heuristics
            if any(old in lowered for old in ["wordpress 5.", "drupal 7.", "joomla 3."]):
                score -= 10
        return {"findings": cms_findings, "score": score}
    except Exception as e:
        return {"findings": [], "score": -10, "error": str(e)}

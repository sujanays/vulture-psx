"""Utility helpers for the scanner package.

Provides:
- SSRF protection & safe IP resolution
- Async HTTP fetch
- Security scoring and letter grade calculation
- Comprehensive checks aggregation (Headers, SSL, Cookies, CMS/Tech)
"""

import httpx
import ipaddress
import socket
from urllib.parse import urlparse
from typing import Dict, List, Any

from .header_analysis import evaluate as evaluate_headers
from .ssl_inspection import evaluate as evaluate_ssl
from .cms_detection import evaluate as evaluate_cms
from .cookie_analysis import evaluate as evaluate_cookies

def is_safe_target(hostname: str) -> bool:
    """Validate that the hostname does not resolve to private or reserved IP addresses (SSRF prevention).
    """
    if not hostname:
        return False
    if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        return False
    try:
        ip_addrs = socket.getaddrinfo(hostname, None)
        for item in ip_addrs:
            ip_str = item[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            if (
                ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_reserved
                or ip_obj.is_multicast
            ):
                return False
        return True
    except Exception:
        # If DNS cannot be resolved, allow scan attempt to fail gracefully downstream
        return True

def calculate_grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"

async def run_all_checks(url: str) -> Dict[str, Any]:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    scheme = parsed.scheme or "https"

    if not is_safe_target(hostname):
        return {
            "url": url,
            "score": 0,
            "grade": "F",
            "error": "Scanning internal, local, or private IP addresses is blocked for security (SSRF prevention).",
            "passed": [],
            "failed": ["Host is a private/internal network IP"],
            "details": {}
        }

    # Fetch target webpage
    headers = {}
    raw_cookies = []
    html = ""
    http_error = None
    status_code = None

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, verify=False) as client:
            resp = await client.get(url, headers={"User-Agent": "VulTure-Security-Scanner/1.0"})
            status_code = resp.status_code
            headers = {k.lower(): v for k, v in resp.headers.items()}
            raw_cookies = resp.headers.get_list("set-cookie")
            html = resp.text
    except Exception as e:
        http_error = str(e)

    # 1. Header Analysis
    header_res = evaluate_headers(headers)

    # 2. SSL/TLS Inspection
    if scheme == "https":
        ssl_res = evaluate_ssl(hostname)
    else:
        ssl_res = {
            "valid": False,
            "cipher_strength": "none",
            "days_left": 0,
            "exp_score": -30,
            "error": "URL does not use HTTPS encryption"
        }

    # 3. CMS & Technology Fingerprint
    cms_res = evaluate_cms(html, headers)

    # 4. Cookie Analysis
    cookie_res = evaluate_cookies(raw_cookies)

    # Scoring calculation
    # Base score: 100
    score = 100
    passed: List[str] = []
    failed: List[str] = []
    remediations: List[Dict[str, str]] = []

    # Process headers
    for h in header_res.get("items", []):
        if h["present"]:
            passed.append(f"Header: {h['title']}")
        else:
            failed.append(f"Missing Header: {h['title']}")
            remediations.append({
                "category": "Headers",
                "title": f"Implement {h['title']}",
                "severity": h["severity"],
                "advice": h["remediation"]
            })
            score -= (15 if h["severity"] == "High" else 10 if h["severity"] == "Medium" else 5)

    # Process SSL
    if ssl_res.get("valid"):
        passed.append("Valid SSL/TLS Certificate")
        if ssl_res.get("cipher_strength") == "strong":
            passed.append("Strong Cipher Suite & Modern TLS")
        else:
            failed.append("Moderate or Weak Cipher Suite")
            score -= 10
            remediations.append({
                "category": "SSL/TLS",
                "title": "Upgrade TLS Cipher Suites",
                "severity": "Medium",
                "advice": "Configure web server to only support TLSv1.2 and TLSv1.3 with forward secrecy ciphers."
            })
        if ssl_res.get("days_left", 0) < 30:
            failed.append(f"SSL Certificate expiring soon ({ssl_res.get('days_left')} days)")
            score -= 10
            remediations.append({
                "category": "SSL/TLS",
                "title": "Renew SSL Certificate",
                "severity": "High",
                "advice": "Certificate is nearing expiration. Renew cert to avoid browser trust warnings."
            })
    else:
        failed.append("Invalid or Missing SSL Certificate")
        score -= 35
        remediations.append({
            "category": "SSL/TLS",
            "title": "Enable HTTPS with Valid Certificate",
            "severity": "High",
            "advice": "Install a valid SSL certificate (e.g. Let's Encrypt) and force HTTPS redirect."
        })

    # Process CMS / Info Leaks
    for finding in cms_res.get("findings", []):
        if "Information Disclosure" in finding or "Outdated" in finding:
            failed.append(finding)
            score -= 5
            remediations.append({
                "category": "Information Disclosure",
                "title": "Hide Server Signatures",
                "severity": "Low",
                "advice": "Disable Server and X-Powered-By tokens in web server configurations."
            })
        else:
            passed.append(finding)

    # Process Cookies
    for c_issue in cookie_res.get("issues", []):
        failed.append(c_issue)
        score -= 5
        remediations.append({
            "category": "Cookies",
            "title": "Harden Cookie Attributes",
            "severity": "Medium",
            "advice": "Ensure all Set-Cookie directives specify 'Secure; HttpOnly; SameSite=Lax'."
        })

    final_score = max(0, min(100, score))
    grade = calculate_grade(final_score)

    return {
        "url": url,
        "hostname": hostname,
        "status_code": status_code,
        "score": final_score,
        "grade": grade,
        "passed": passed,
        "failed": failed,
        "remediations": remediations,
        "details": {
            "headers": header_res,
            "ssl": ssl_res,
            "cms": cms_res,
            "cookies": cookie_res
        },
        "error": http_error
    }

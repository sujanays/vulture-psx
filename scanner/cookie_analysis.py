"""Cookie Security Analysis Module.

Inspects Set-Cookie headers for security attributes (Secure, HttpOnly, SameSite).
"""

from typing import List, Dict, Any
from http.cookies import SimpleCookie

def evaluate(raw_cookie_headers: List[str]) -> Dict[str, Any]:
    if not raw_cookie_headers:
        return {
            "score": 0,
            "has_cookies": False,
            "cookies": [],
            "issues": []
        }

    cookies_data = []
    issues = []
    score_penalty = 0

    for header_val in raw_cookie_headers:
        cookie = SimpleCookie()
        try:
            cookie.load(header_val)
        except Exception:
            continue

        for name, morsel in cookie.items():
            secure = morsel['secure'] is True or 'secure' in header_val.lower()
            httponly = morsel['httponly'] is True or 'httponly' in header_val.lower()
            samesite = morsel.get('samesite', None)
            if not samesite:
                # Check raw string
                for part in header_val.split(';'):
                    if 'samesite' in part.lower():
                        samesite = part.split('=')[-1].strip()
                        break

            c_info = {
                "name": name,
                "secure": bool(secure),
                "httponly": bool(httponly),
                "samesite": samesite or "None"
            }
            cookies_data.append(c_info)

            if not secure:
                issues.append(f"Cookie '{name}' is missing 'Secure' flag")
                score_penalty += 5
            if not httponly:
                issues.append(f"Cookie '{name}' is missing 'HttpOnly' flag")
                score_penalty += 5
            if not samesite or samesite.lower() == "none":
                issues.append(f"Cookie '{name}' has missing or Lax SameSite policy")
                score_penalty += 2

    return {
        "score": -min(20, score_penalty),
        "has_cookies": True,
        "cookies": cookies_data,
        "issues": issues
    }

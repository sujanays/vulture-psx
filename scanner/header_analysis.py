from typing import Dict, Any

SECURITY_HEADERS = {
    "content-security-policy": {
        "key": "csp",
        "title": "Content Security Policy (CSP)",
        "severity": "High",
        "description": "Restricts sources of executable scripts, stylesheets, and embedded resources to prevent XSS and data injection attacks.",
        "remediation": "Add 'Content-Security-Policy: default-src 'self'; script-src 'self' ...' to your web server config.",
        "weight": 15
    },
    "strict-transport-security": {
        "key": "hsts",
        "title": "HTTP Strict Transport Security (HSTS)",
        "severity": "High",
        "description": "Enforces secure (HTTPS) connections, preventing SSL-stripping and man-in-the-middle attacks.",
        "remediation": "Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload' header.",
        "weight": 15
    },
    "x-frame-options": {
        "key": "x_frame_options",
        "title": "X-Frame-Options",
        "severity": "Medium",
        "description": "Controls whether the site can be embedded in an <iframe>, mitigating Clickjacking attacks.",
        "remediation": "Add 'X-Frame-Options: DENY' or 'X-Frame-Options: SAMEORIGIN'.",
        "weight": 10
    },
    "x-content-type-options": {
        "key": "x_content_type_options",
        "title": "X-Content-Type-Options",
        "severity": "Medium",
        "description": "Prevents MIME-type sniffing where browsers execute uploaded non-script files as scripts.",
        "remediation": "Add 'X-Content-Type-Options: nosniff'.",
        "weight": 10
    },
    "referrer-policy": {
        "key": "referrer_policy",
        "title": "Referrer-Policy",
        "severity": "Low",
        "description": "Controls how much referrer information (paths, queries) is sent when navigating to external origins.",
        "remediation": "Add 'Referrer-Policy: strict-origin-when-cross-origin'.",
        "weight": 5
    },
    "permissions-policy": {
        "key": "permissions_policy",
        "title": "Permissions-Policy",
        "severity": "Low",
        "description": "Restricts browser features and hardware APIs (camera, microphone, geolocation).",
        "remediation": "Add 'Permissions-Policy: camera=(), microphone=(), geolocation=()'.",
        "weight": 5
    }
}

def evaluate(headers: Dict[str, str]) -> Dict[str, Any]:
    norm_headers = {k.lower(): v for k, v in headers.items()}
    score = 0
    details = {}
    items = []

    for header_name, meta in SECURITY_HEADERS.items():
        present = header_name in norm_headers
        val = norm_headers.get(header_name, "")
        if present:
            score += meta["weight"]
        else:
            score -= meta["weight"] // 2

        details[meta["key"]] = present
        items.append({
            "header": header_name,
            "title": meta["title"],
            "present": present,
            "value": val if present else None,
            "severity": meta["severity"],
            "description": meta["description"],
            "remediation": meta["remediation"]
        })

    return {
        "score": score,
        "details": details,
        "items": items
    }

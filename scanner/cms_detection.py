"""Technology & CMS detection module.

Provides passive fingerprinting of web servers, frameworks, and common CMS platforms
via HTTP headers and HTML markup, identifying server version information disclosure.
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Any

def detect_technologies(html: str, headers: Dict[str, str]) -> Dict[str, Any]:
    findings: List[str] = []
    technologies: List[Dict[str, str]] = []
    penalties: int = 0
    soup = BeautifulSoup(html, "html.parser") if html else None

    # 1. Server header identification & information disclosure check
    server = headers.get("server")
    if server:
        findings.append(f"Server header identified: {server}")
        technologies.append({"category": "Web Server", "name": server})
        # Check if server reveals detailed version numbers (information disclosure)
        if any(char.isdigit() for char in server):
            findings.append(f"Information Disclosure: Server header leaks specific version ({server})")
            penalties += 5

    # 2. X-Powered-By header
    powered = headers.get("x-powered-by")
    if powered:
        findings.append(f"X-Powered-By header exposed: {powered}")
        technologies.append({"category": "Backend Runtime", "name": powered})
        penalties += 5

    # 3. HTML Meta Generator Tag
    if soup:
        generator = soup.find("meta", attrs={"name": "generator"})
        if generator and generator.get("content"):
            gen_content = generator["content"]
            findings.append(f"Generator Meta Tag: {gen_content}")
            technologies.append({"category": "CMS / Generator", "name": gen_content})
            lowered = gen_content.lower()
            if any(old in lowered for old in ["wordpress 4.", "wordpress 5.", "drupal 7.", "joomla 3."]):
                findings.append(f"Outdated CMS detected ({gen_content})")
                penalties += 15

    # 4. Frontend Framework signatures in HTML
    if html:
        lowered_html = html.lower()
        if '__next' in lowered_html or 'next/static' in lowered_html:
            technologies.append({"category": "Frontend Framework", "name": "Next.js"})
        elif '__nuxt' in lowered_html or 'nuxt.js' in lowered_html:
            technologies.append({"category": "Frontend Framework", "name": "Nuxt.js"})
        elif 'data-reactroot' in lowered_html:
            technologies.append({"category": "Frontend Library", "name": "React"})
        elif 'wp-content' in lowered_html:
            if not any(t["name"].lower().startswith("wordpress") for t in technologies):
                technologies.append({"category": "CMS", "name": "WordPress"})

    score = -penalties
    return {
        "findings": findings,
        "technologies": technologies,
        "score": score
    }

def evaluate(html: str, headers: Dict[str, str]) -> Dict[str, Any]:
    try:
        norm_headers = {k.lower(): v for k, v in headers.items()}
        return detect_technologies(html, norm_headers)
    except Exception as e:
        return {"findings": [], "technologies": [], "score": 0, "error": str(e)}

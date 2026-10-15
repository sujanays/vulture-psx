import httpx
from typing import Dict

def check_csp(headers: Dict[str, str]) -> bool:
    return 'content-security-policy' in {k.lower(): v for k, v in headers.items()}

def check_x_frame_options(headers: Dict[str, str]) -> bool:
    return 'x-frame-options' in {k.lower(): v for k, v in headers.items()}

def check_hsts(headers: Dict[str, str]) -> bool:
    return 'strict-transport-security' in {k.lower(): v for k, v in headers.items()}

def evaluate(headers: Dict[str, str]) -> Dict:
    score = 0
    results = {}
    for name, func in [('csp', check_csp), ('x_frame_options', check_x_frame_options), ('hsts', check_hsts)]:
        present = func(headers)
        results[name] = present
        score += 10 if present else -10
    return {'score': score, 'details': results}

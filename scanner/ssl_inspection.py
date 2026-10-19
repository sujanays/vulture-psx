import ssl
import socket
from datetime import datetime
from typing import Dict, Any, Optional

def get_certificate(host: str, port: int = 443) -> Dict[str, Any]:
    context = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=6) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            cert = ssock.getpeercert()
            cipher = ssock.cipher()
            version = ssock.version()
    return {'cert': cert, 'cipher': cipher, 'version': version}

def parse_issuer(cert: Dict) -> str:
    issuer_tuples = cert.get('issuer', ())
    for rdn in issuer_tuples:
        for key, value in rdn:
            if key in ('commonName', 'organizationName'):
                return value
    return "Unknown CA"

def check_expiration(cert: Dict) -> tuple[int, int, str]:
    notAfter = cert.get('notAfter')
    if not notAfter:
        return -10, 0, "Unknown"
    try:
        exp_date = datetime.strptime(notAfter, '%b %d %H:%M:%S %Y %Z')
        days_left = (exp_date - datetime.utcnow()).days
        if days_left > 30:
            score = 15
        elif days_left > 0:
            score = 5
        else:
            score = -20
        return score, days_left, exp_date.strftime("%Y-%m-%d")
    except Exception:
        return -5, 0, "Invalid date format"

def evaluate_cipher_strength(cipher_info) -> str:
    if not cipher_info:
        return 'weak'
    cipher_name, protocol, bits = cipher_info
    if 'TLSv1.3' in protocol or (bits and bits >= 256):
        return 'strong'
    elif bits and bits >= 128:
        return 'moderate'
    else:
        return 'weak'

def evaluate(host: str) -> Dict[str, Any]:
    try:
        data = get_certificate(host)
        cert = data['cert']
        cipher_tuple = data['cipher']
        version = data.get('version', 'TLS')
        exp_score, days_left, exp_date_str = check_expiration(cert)
        cipher_strength = evaluate_cipher_strength(cipher_tuple)
        issuer = parse_issuer(cert)
        
        cipher_name = cipher_tuple[0] if cipher_tuple else "Unknown"

        return {
            'valid': True,
            'exp_score': exp_score,
            'days_left': days_left,
            'expiration_date': exp_date_str,
            'cipher_strength': cipher_strength,
            'cipher_name': cipher_name,
            'protocol': version,
            'issuer': issuer
        }
    except Exception as e:
        return {
            'valid': False,
            'exp_score': -20,
            'days_left': 0,
            'expiration_date': None,
            'cipher_strength': 'none',
            'cipher_name': 'None',
            'protocol': 'None',
            'issuer': 'None',
            'error': str(e)
        }

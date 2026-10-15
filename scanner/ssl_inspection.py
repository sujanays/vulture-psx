import ssl
import socket
from datetime import datetime
from typing import Dict

def get_certificate(host: str, port: int = 443) -> Dict:
    context = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            cert = ssock.getpeercert()
            cipher = ssock.cipher()
    return {'cert': cert, 'cipher': cipher}

def check_expiration(cert_dict: Dict) -> int:
    notAfter = cert_dict['cert'].get('notAfter')
    if not notAfter:
        return -10  # cannot determine
    exp_date = datetime.strptime(notAfter, '%b %d %H:%M:%S %Y %Z')
    days_left = (exp_date - datetime.utcnow()).days
    # award points based on remaining days
    if days_left > 365:
        return 10
    elif days_left > 30:
        return 5
    else:
        return -5

def evaluate_cipher_strength(cipher_info) -> str:
    # cipher_info is a tuple like ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', 256)
    _, protocol, bits = cipher_info
    if protocol.startswith('TLSv1.3'):
        return 'strong'
    if bits >= 256:
        return 'strong'
    elif bits >= 128:
        return 'moderate'
    else:
        return 'weak'

def evaluate(host: str) -> Dict:
    try:
        data = get_certificate(host)
        exp_score = check_expiration(data)
        cipher_strength = evaluate_cipher_strength(data['cipher'])
        return {'valid': True, 'exp_score': exp_score, 'cipher_strength': cipher_strength}
    except Exception as e:
        return {'valid': False, 'error': str(e)}

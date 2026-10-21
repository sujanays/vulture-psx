# VulnScan Lite / VulTure: Scanning Logic & Technical Compliance Specification

---

## Executive Summary

**VulnScan Lite** (integrated within the **VulTure** security scanning engine) is a lightweight, non-intrusive security posture assessment platform. The architecture is engineered around the principle of **strictly passive analysis**: evaluating defensive capabilities, transport encryption, and exposed metadata without injecting attack payloads, exploiting vulnerabilities, or disrupting target operations.

This document details the internal mechanics of the passive detection engine, system compliance protocols, header evaluation mathematics, SSL/TLS handshake inspection, and technology fingerprinting routines.

---

##  1. Header Analysis Mechanics

### 1.1 Inspection Architecture
When a target URL is submitted, the backend engine executes a benign HTTP GET request using an isolated client session. HTTP response headers returned by the target web server are collected and normalized to lowercase (`norm_headers = {k.lower(): v for k, v in headers.items()}`) to guarantee RFC 7230 case-insensitive conformity.

The scanner evaluates the presence and structural configuration of critical security headers:

#### 1. `Content-Security-Policy` (CSP)
* **Function:** Mitigates Cross-Site Scripting (XSS), code injection, clickjacking, and unauthorized resource embedding.
* **Mechanism:** Instructs the browser to whitelist authorized domains for scripts (`script-src`), styles (`style-src`), frame ancestors (`frame-ancestors`), and generic objects (`default-src`).
* **Detection:** Verifies if the `content-security-policy` header exists in the normalized response dictionary.

#### 2. `X-Frame-Options`
* **Function:** Defends against UI redressing and Clickjacking attacks.
* **Mechanism:** Directs conforming browsers whether the page may be rendered inside `<frame>`, `<iframe>`, `<embed>`, or `<object>` elements.
* **Detection:** Verifies presence and valid directive values (`DENY` or `SAMEORIGIN`).

#### 3. `Strict-Transport-Security` (HSTS)
* **Function:** Enforces encrypted HTTPS communication, mitigating SSL-stripping, man-in-the-middle (MitM) wiretapping, and cookie hijacking.
* **Mechanism:** Requires user agents to interact with the domain exclusively over TLS for a declared lifetime (`max-age`), with optional sub-domain inheritance (`includeSubDomains`) and preloading (`preload`).
* **Detection:** Confirms presence of `strict-transport-security` header and validates standard directives.

### 1.2 Exact Scoring Logic
Security headers directly impact the composite security score. The standardized scoring formula applied for header analysis is:

$$\text{Header Score Contribution} = \sum_{h \in \mathcal{H}} S(h)$$

Where $\mathcal{H} = \{\text{CSP}, \text{X-Frame-Options}, \text{HSTS}\}$ (alongside configured secondary controls), and:

$$S(h) = \begin{cases} +10 & \text{if header } h \text{ is present and recognized} \\ -10 & \text{if header } h \text{ is missing} \end{cases}$$

#### Scoring Breakdown Table
| Security Control Header | Presence Status | Score Adjustment | Severity if Missing | Remediation Strategy |
| :--- | :---: | :---: | :---: | :--- |
| **`Content-Security-Policy`** | Present | **+10 points** | High | Configure `default-src 'self'` with explicit whitelist origins. |
| **`Content-Security-Policy`** | Missing | **-10 points** | High | Define strict CSP policy in web server or CDN edge rules. |
| **`X-Frame-Options`** | Present | **+10 points** | Medium | Maintain `DENY` or `SAMEORIGIN` to prevent framing. |
| **`X-Frame-Options`** | Missing | **-10 points** | Medium | Set `X-Frame-Options: SAMEORIGIN` or utilize CSP `frame-ancestors`. |
| **`Strict-Transport-Security`** | Present | **+10 points** | High | Ensure `max-age` is at least 31,536,000 seconds (1 year). |
| **`Strict-Transport-Security`** | Missing | **-10 points** | High | Add `Strict-Transport-Security: max-age=31536000; includeSubDomains`. |

---

## 2. SSL/TLS Inspection Mechanics

### 2.1 Python Native `ssl` Connection Architecture
Rather than calling heavy third-party command-line binaries (such as `nmap` or `testssl.sh`) or executing invasive handshake probes, the engine uses Python's standard `ssl` and `socket` libraries.

```python
import ssl
import socket

def get_certificate(host: str, port: int = 443):
    context = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=6) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            cert = ssock.getpeercert()
            cipher = ssock.cipher()
            version = ssock.version()
    return {'cert': cert, 'cipher': cipher, 'version': version}
```

1. **Default Context Creation:** `ssl.create_default_context()` prepares a secure client context loading trusted system CA root certificates, enforcing certificate verification (`ssl.CERT_REQUIRED`), and enabling hostname checking.
2. **TCP Socket Establishment:** `socket.create_connection((host, port), timeout=6)` performs a low-overhead TCP three-way handshake with the target host on port 443.
3. **SNI (Server Name Indication) Wrapping:** `context.wrap_socket(sock, server_hostname=host)` initiates the TLS handshake, transmitting the `server_hostname` in the ClientHello message to ensure multi-tenant servers present the correct virtual host certificate.

### 2.2 Verification Checks Performed

#### 1. Certificate Validity and Trust Chain
* The peer certificate is retrieved via `ssock.getpeercert()`.
* The trust chain is verified against local trusted Root CA authorities. If the certificate is self-signed, untrusted, or has a mismatched hostname, Python's SSL layer raises an `SSLCertVerificationError`, which the engine catches and flags as an untrusted or invalid certificate state (`valid: false`).
* The CA Issuer is parsed from the distinguished name tuples (`commonName` or `organizationName`, e.g., "Let's Encrypt", "DigiCert", "Cloudflare Inc").

#### 2. Expiration Date Calculation
* The certificate's `notAfter` timestamp is extracted (format: `%b %d %H:%M:%S %Y %Z`).
* The engine calculates remaining validity:
  $$\Delta t_{\text{days}} = \frac{T_{\text{notAfter}} - T_{\text{current}}}{86400 \text{ seconds}}$$
* **Evaluation Thresholds:**
  * $\Delta t_{\text{days}} > 30$: Certificate is healthy and valid.
  * $0 < \Delta t_{\text{days}} \le 30$: Certificate expires soon; warning raised.
  * $\Delta t_{\text{days}} \le 0$: Certificate is expired; flagged as critical failure.

#### 3. Cipher Suite Strength Inspection (Non-Intrusive)
* The active cipher suite is captured directly from `ssock.cipher()`, which returns a 3-tuple:
  $$(\text{cipher\_name}, \text{protocol\_version}, \text{secret\_bits})$$
* **Non-Aggressive Inspection Guarantee:**
  * The scanner **never** performs brute-force cipher renegotiation, heartbleed exploits, or denial-of-service stress tests.
  * It passively inspects the parameters that the server negotiated naturally during a standard client connection:
    * **Strong:** Negotiated via `TLSv1.3` or with key bit length $\ge 256$ bits (e.g., `TLS_AES_256_GCM_SHA384`, `ECDHE-RSA-AES256-GCM-SHA384`).
    * **Moderate:** Key bit length $\ge 128$ bits (e.g., `ECDHE-RSA-AES128-GCM-SHA256`).
    * **Weak:** Deprecated protocol (TLSv1.0, TLSv1.1) or key bit length $< 128$ bits.

---

## 3. CMS & Outdated Software Detection

### 3.1 Passive Scraping & Fingerprinting Patterns
The engine passively inspects HTML markup and response headers returned during the initial request, searching for signature markers without probing administrative endpoints (`/wp-admin`, `/administrator/`) or fuzzing hidden directories.

#### 1. HTML `<meta>` Tag Inspection
Content Management Systems (CMS) frequently output metadata disclosing the platform name and exact build version. The engine employs `BeautifulSoup` to parse the `<head>` tree:
```html
<meta name="generator" content="WordPress 5.8.2" />
```
* **Extraction:** The parser locates `soup.find("meta", attrs={"name": "generator"})` and reads the `content` attribute.
* **Pattern Recognition:** Detects signatures such as `WordPress [version]`, `Drupal [version]`, `Joomla! [version]`, and static site generators (Gatsby, Hugo, Jekyll).

#### 2. HTTP Response Header Fingerprinting
* **`X-Powered-By`:** Inspects headers disclosing application runtimes, application frameworks, or engine versions (e.g., `X-Powered-By: PHP/8.1.13`, `Express`, `ASP.NET`).
* **`Server`:** Examines web server signatures (e.g., `Server: Apache/2.4.41 (Ubuntu)`, `Server: nginx/1.18.0`). When numeric version strings are exposed, the engine logs an Information Disclosure finding.

#### 3. Passive DOM Heuristics
* Identification of client-side assets without aggressive scanning:
  * WordPress: Presence of `/wp-content/` or `/wp-includes/` resource paths.
  * Next.js: Identification of `__next` DOM container IDs or `/_next/static/` script references.
  * Nuxt.js: Detection of `__nuxt` element wrappers or `nuxt.js` asset tags.
  * React: Detection of `data-reactroot` attributes or React bundle identifiers.

### 3.2 Outdated Platform Parsing & Security Flagging
When a generator or software signature is detected, the version string is isolated and compared against vulnerability databases and end-of-life (EOL) release indices:

```python
# Outdated Platform Matching Logic
lowered = gen_content.lower()
if any(old in lowered for old in ["wordpress 4.", "wordpress 5.", "drupal 7.", "joomla 3."]):
    findings.append(f"Outdated CMS detected ({gen_content})")
    penalties += 15
```

* **WordPress 4.x / 5.x:** Flagged due to unpatched core vulnerabilities, legacy REST API exposures, and deprecated cryptographic standards.
* **Drupal 7.x:** Flagged due to End-of-Life (EOL) milestone, deprecated PHP compatibility, and vulnerability to known public exploits (e.g., Drupalgeddon series).
* **Joomla 3.x:** Flagged due to sunset support lifecycle and remote code execution vulnerabilities in legacy extensions.
* **Risk Reporting:** When an outdated version is identified, the findings report highlights the specific version string, lowers the composite posture score, and provides actionable remediation guidance (e.g., upgrade to current LTS releases and suppress `<meta name="generator">` output).

---

## 5. Security & Safety Guarantees

| Category | Passive Scanner Approach | Aggressive / Active Scanner Approach (Avoided) |
| :--- | :--- | :--- |
| **Network Footprint** | Single standard HTTPS request per host | Thousands of sequential / concurrent requests |
| **Payload Injection** | None (Zero SQLi, XSS, SSRF payloads injected) | Active fuzzing and taint analysis |
| **Authentication** | Inspects public unauthenticated surface only | Brute-force credential spraying |
| **Resource Impact** | Negligible (~50ms network round-trip) | Potential Denial of Service / server degradation |
| **Compliance Risk** | Minimal (Standard web client behavior) | High (Requires explicit penetration testing contract) |

---
*Document Version: 1.0.0*  
*Project: VulnScan Lite / VulTure Security Engine*  
*Compliance Classification: Defensive / Passive Reconnaissance*

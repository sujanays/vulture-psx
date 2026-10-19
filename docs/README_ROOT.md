# VulTure Security Scanner

> **⚠️ Only scan websites you own or have permission to test. This tool performs passive analysis only.**

## Overview

VulTure is a production-ready, full‑stack web application for passive security posture assessment. It analyzes websites against modern web security benchmarks and delivers visual scores, actionable remediation advice, and executive PDF audit reports.

### Evaluated Security Vectors
1. **HTTP Security Headers**:
   - `Content-Security-Policy` (CSP)
   - `Strict-Transport-Security` (HSTS)
   - `X-Frame-Options` (Clickjacking mitigation)
   - `X-Content-Type-Options` (MIME-sniffing prevention)
   - `Referrer-Policy` (Referrer leakage control)
   - `Permissions-Policy` (Hardware & API restrictions)
2. **SSL / TLS Encryption**:
   - Certificate validation & Certificate Authority (CA) issuer
   - Expiration countdown with threshold warnings
   - Protocol version (TLSv1.2, TLSv1.3) and cipher suite strength
3. **Cookie Security**:
   - Evaluates `Set-Cookie` directives for `Secure`, `HttpOnly`, and `SameSite` flags
4. **Technology & Server Fingerprinting**:
   - Web server signatures (`Server` header)
   - Runtime leaks (`X-Powered-By`)
   - CMS & frontend frameworks (WordPress, Drupal, Joomla, Next.js, Nuxt, React)
   - Flags version disclosures that aid attacker reconnaissance
5. **SSRF & Private IP Protection**:
   - Automated DNS validation rejecting private IP ranges (RFC 1918, localhost, cloud metadata endpoints)

---

## Architecture & Tech Stack

- **Frontend**: React 19, Vite, responsive Cyber Dark design system with SVG circular gauge, live animated scanner stepper, tabbed findings view, and scan history drawer.
- **Backend**: FastAPI with async route handlers, CORS middleware, and rate-limiting (`slowapi`, 10 req/min).
- **Task Queue**: Celery 5 + Redis 7 for non-blocking asynchronous scanning.
- **Persistence**: SQLite with named Docker volume (`vulture_data`) for permanent scan history.
- **Reporting**: WeasyPrint with custom CSS template for executive PDF downloads.
- **Orchestration**: Docker & Docker Compose.

---

## Quick Start

### 1. Launch All Services with Docker
```bash
docker compose -f docker/docker-compose.yml up -d --build
```

### 2. Access the Application
- **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173)
- **Interactive API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redis Broker**: `localhost:6379`

### 3. API Endpoints
- `POST /api/scan/` — Queue a new passive security scan (`{"url": "https://example.com"}`)
- `GET /api/scan/{task_id}/status` — Poll task progress and fetch scan report
- `GET /api/scan/{task_id}/pdf` — Download the compiled PDF security audit report
- `GET /api/scans/` — Retrieve past scan records from persistent database
- `DELETE /api/scan/{task_id}` — Delete a scan record from history

### 4. Running the Test Suite
```bash
docker exec vulture_backend python -m unittest discover tests
```

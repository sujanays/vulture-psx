# 🦅 VulTure — Passive Web Vulnerability & Architecture Scanner

> **⚠️ Disclaimer:** Only scan websites you own or have explicit written authorization to test. VulTure performs non-intrusive, passive security evaluations only.

VulTure is a production-ready, full-stack cybersecurity web application designed to evaluate the passive security posture of any public web target. It analyzes critical security vectors including HTTP security headers, SSL/TLS transport encryption, cookie attributes, and technology stack information leaks. The application provides dynamic scoring (0–100), letter grading (A–F), actionable remediation guidance, persistent scan history, and downloadable executive PDF audit reports.

---

## 📸 Core Features

- **🛡️ HTTP Security Headers Audit**: Evaluates `CSP`, `HSTS`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, and `Permissions-Policy` with severity tags and copyable fix snippets.
- **🔒 SSL / TLS Inspection**: Validates certificates, tracks expiration countdowns, identifies the issuing CA, evaluates protocol versions (TLSv1.2, TLSv1.3), and checks cipher suite strength.
- **🍪 Cookie Hygiene Analysis**: Inspects `Set-Cookie` directives for `Secure`, `HttpOnly`, and `SameSite` flags.
- **⚙️ Technology & CMS Fingerprinting**: Identifies web servers (Nginx, Apache, Cloudflare), frontend/backend frameworks (Next.js, React, Nuxt), CMS platforms (WordPress, Drupal, Joomla), and alerts on server version disclosure.
- **🛡️ SSRF & Private IP Protection**: Automatically resolves DNS and blocks attempts to scan private, loopback, or reserved network addresses (`127.0.0.1`, `10.0.0.0/8`, `192.168.0.0/16`, AWS metadata `169.254.169.254`, IPv6 `::1`).
- **📊 Interactive Cyber Dashboard**: Features an animated circular score gauge, live progress stepper, tabbed inspection views, and dark mode UI.
- **📄 Executive PDF Audit Reports**: One-click PDF report generation powered by WeasyPrint.
- **💾 Persistent Database Storage**: Embedded SQLite database mounted on a Docker volume for scan history and re-inspection.

---

## 🏗️ Architecture & Tech Stack

```text
               ┌────────────────────────────────────────────────────────┐
               │                  User Browser                         │
               │            (http://localhost:5173)                     │
               └───────────────▲────────────────────────▲───────────────┘
                               │                        │
                     HTTP API  │                        │  Static Assets
                     Requests  │                        │  (HTML/CSS/JS)
                               ▼                        ▼
               ┌────────────────────────┐      ┌────────────────────────┐
               │    FastAPI Backend     │      │   Nginx Frontend (UI)  │
               │ (http://localhost:8000)│      │  Container: 5173 -> 80 │
               └───────────────┬────────┘      └────────────────────────┘
                               │
                Dispatches Scan│   Reads / Writes History
                               ▼
               ┌────────────────────────┐      ┌────────────────────────┐
               │      Redis Broker      │◄────►│  Celery Worker Engine  │
               │      Port: 6379        │      │ (vulture_worker)       │
               └────────────────────────┘      └───────────┬────────────┘
                                                           │
                                           Stores Audit    ▼
                                           ──────────────────────────────
                                           SQLite DB (/app/data/vulture.db)
                                           Named Volume: vulture_data
```

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | React 19, Vite, Vanilla CSS | Interactive Cyber UI, Gauge Chart, Tabs, History Drawer |
| **Backend API** | FastAPI, Uvicorn, SlowAPI | REST API endpoints, SSRF guard, rate-limiting (10 req/min) |
| **Task Queue** | Celery 5 + Redis 7 | Asynchronous, non-blocking scan execution |
| **Scanner Engine** | Python 3.11, HTTPX, BeautifulSoup4 | Passive network inspection, SSL handshake, cookie analysis |
| **Database** | SQLite 3 | Persistent scan history across container restarts |
| **PDF Reporting** | WeasyPrint 62.3, Pydyf 0.10.0 | Server-side printable PDF generation |
| **Orchestration** | Docker, Docker Compose | Multi-container setup with isolated bridge network |

---

## 🚀 Prerequisites

1. **Docker Desktop** installed and running on Windows, macOS, or Linux.
2. **Git** for cloning the repository.

---

## ⚡ Quick Start

### 1. Clone & Navigate to the Project
```bash
git clone <repository-url>
cd VulTure
```

### 2. Launch the Application Stack
Run the following command from the repository root:
```bash
docker compose -f docker/docker-compose.yml up -d --build
```

### 3. Verify Containers are Running
```bash
docker compose -f docker/docker-compose.yml ps
```
All four services should show status **Up**:
```text
NAME               IMAGE             STATUS         PORTS
vulture_frontend   docker-frontend   Up             0.0.0.0:5173->80/tcp
vulture_backend    docker-backend    Up             0.0.0.0:8000->8000/tcp
vulture_redis      redis:7-alpine    Up             0.0.0.0:6379->6379/tcp
vulture_worker     docker-worker     Up             8000/tcp
```

### 4. Access the Live Applications
- **Frontend Web Dashboard**: [http://localhost:5173](http://localhost:5173)
- **Interactive Backend API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redis Service**: `localhost:6379`

---

## 🧪 Manual Testing Guide

### A. Testing via the Web UI (Browser)

1. Open **[http://localhost:5173](http://localhost:5173)** in your browser.
2. **Trigger a Scan**:
   - In the target input box, enter a public URL such as `https://example.com` or click one of the quick test chips (`wordpress.org`, `github.com`).
   - Click **Inspect Target →**.
3. **Observe Scan Progress**:
   - The multi-stage animated progress card will track resolution, SSL inspection, security header checks, and report compilation.
4. **Inspect the Audit Report**:
   - **Score Gauge**: Review the overall score (0–100) and color-coded letter grade (**A**, **B**, **C**, **D**, or **F**).
   - **Header Tab**: Review which headers are configured or missing, their risk severity, and remediation advice.
   - **SSL/TLS Tab**: Inspect certificate validity, CA issuer, expiration date, and TLS cipher strength.
   - **Tech Stack Tab**: Inspect detected web servers and framework signatures.
   - **Cookies Tab**: Review cookie security flags (`Secure`, `HttpOnly`, `SameSite`).
   - **Remediations Tab**: View actionable server configuration recommendations.
5. **Download PDF Report**:
   - Click **⬇ Export PDF Report** to download the styled executive audit report (`vulture_report_<domain>.pdf`).
6. **Browse Scan History**:
   - Click **📜 Scan History** in the top navigation bar to open the slide-over drawer.
   - Click any past scan to reload its report instantly, or click 🗑️ to delete a record from the database.

---

### B. Testing via Command Line / REST API

You can execute manual API tests using PowerShell or cURL:

#### 1. Submit a Scan Job
```powershell
docker exec vulture_backend python -c "import httpx; r = httpx.post('http://localhost:8000/api/scan/', json={'url': 'https://example.com/'}); print(r.json())"
```
*Response:*
```json
{"task_id": "05519f8e-372c-4eb4-9d0e-cd0cae953039", "status": "PENDING", "result": null, "error": null}
```

#### 2. Poll Scan Status and Results
```powershell
docker exec vulture_backend python -c "import httpx; r = httpx.get('http://localhost:8000/api/scan/<task_id>/status'); print(r.json())"
```

#### 3. Test SSRF Guard (Private IP Rejection)
Attempting to scan localhost or private addresses is blocked:
```powershell
docker exec vulture_backend python -c "import httpx; r = httpx.post('http://localhost:8000/api/scan/', json={'url': 'http://127.0.0.1/'}); print(r.json())"
```
*Polling result:*
```json
{"error": "Scanning internal, local, or private IP addresses is blocked for security (SSRF prevention)."}
```

#### 4. Test PDF Export Endpoint
```powershell
docker exec vulture_backend python -c "import httpx; r = httpx.get('http://localhost:8000/api/scan/<task_id>/pdf'); print('Status:', r.status_code, 'Content-Type:', r.headers.get('content-type'), 'Size:', len(r.content), 'bytes')"
```
*Expected output:* `Status: 200 Content-Type: application/pdf Size: ~26000 bytes`

#### 5. List Persistent Scan Records
```powershell
docker exec vulture_backend python -c "import httpx; r = httpx.get('http://localhost:8000/api/scans/'); print('Total scans in DB:', len(r.json()))"
```

---

## 🔬 Automated Unit Testing

Run the included automated unit test suite inside the backend container:

```bash
docker exec vulture_backend python -m unittest discover tests
```

*Expected output:*
```text
.....
----------------------------------------------------------------------
Ran 5 tests in 0.084s

OK
```

The test suite covers:
- Letter grade calculations and threshold mapping
- SSRF filtering for loopback, RFC 1918 private IPs, and cloud metadata addresses
- Security header evaluations (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, etc.)
- Cookie hygiene flag parsing (`Secure`, `HttpOnly`, `SameSite`)
- CMS and server technology detection with version leakage identification

---

## 📁 Repository Structure

```text
VulTure/
├── README.md                          # Project documentation and usage guide
├── requirements.txt                   # Python backend dependencies
├── .env                               # Environment configurations
├── .gitignore                         # Git exclusion rules
│
├── backend/                           # FastAPI application package
│   ├── main.py                        # FastAPI entrypoint, CORS, rate limiter
│   ├── api/
│   │   ├── routes.py                  # API endpoints (scan, status, PDF, history)
│   │   └── schemas.py                 # Pydantic validation models
│   ├── db/
│   │   └── database.py                # SQLite persistence manager
│   ├── services/
│   │   └── pdf_generator.py           # WeasyPrint PDF report builder
│   └── worker/
│       └── celery_app.py              # Celery worker initialization
│
├── scanner/                           # Passive security scanning modules
│   ├── __init__.py                    # Scanner package exports
│   ├── header_analysis.py             # Security header analysis and remediation rules
│   ├── ssl_inspection.py              # TLS handshake, cipher strength, cert expiry
│   ├── cms_detection.py               # Web server, CMS, and tech fingerprinting
│   ├── cookie_analysis.py             # Set-Cookie flags verification
│   ├── tasks.py                       # Celery task definitions
│   └── utils.py                       # SSRF validation, scoring aggregator, grade calculator
│
├── frontend/                          # React + Vite application
│   ├── Dockerfile                     # Multi-stage production Nginx build
│   ├── package.json                   # Node.js dependencies
│   ├── vite.config.js                 # Vite bundler configuration
│   ├── index.html                     # HTML root template with Inter font
│   └── src/
│       ├── App.jsx                    # Primary application component
│       ├── App.css                    # Cyber Dark design system
│       ├── index.css                  # CSS reset and base styles
│       ├── main.jsx                   # React DOM render entrypoint
│       └── components/
│           ├── Navbar.jsx             # Top branding and history navigation
│           ├── ScanForm.jsx           # Target URL input with sample chips
│           ├── ScanProgress.jsx       # Multi-stage animated scan stepper
│           ├── ScoreGauge.jsx         # Circular SVG score meter & grade badge
│           ├── ReportView.jsx         # Tabbed findings, remediation checklist, PDF export
│           └── HistoryDrawer.jsx      # Slide-over past scans history manager
│
├── docker/                            # Container orchestration
│   ├── Dockerfile.backend             # Python 3.11 + WeasyPrint Debian image
│   └── docker-compose.yml             # Full-stack multi-container specification
│
├── tests/                             # Automated test suite
│   └── test_scanner.py                # Unit tests for scoring, SSRF, headers, cookies
│
└── docs/                              # Architecture and design notes
    └── README_ROOT.md                 # Detailed module specifications
```

---

## 🛠️ Configuration & Environment Variables

Key settings can be modified via environment variables or in `.env`:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `REDIS_URL` | `redis://redis:6379/0` | Connection string for Redis broker |
| `PYTHONPATH` | `/app` | Python module import path |
| `VULTURE_DB_PATH` | `/app/data/vulture.db` | Location of the persistent SQLite database file |
| `VITE_BACKEND_URL` | `http://localhost:8000/api` | Backend API base URL consumed by the React frontend |

---

## 🛑 Stopping or Restarting Services

```bash
# Restart all containers
docker compose -f docker/docker-compose.yml restart

# Stop all containers (preserves database volume)
docker compose -f docker/docker-compose.yml down

# Stop all containers and remove volumes (resets database)
docker compose -f docker/docker-compose.yml down -v
```

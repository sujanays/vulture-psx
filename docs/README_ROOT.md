# VulTure Security Scanner

> **⚠️ Only scan websites you own. This tool performs passive analysis only.**

## Overview

VulTure is a full‑stack web application that performs passive security scans of a target website. It evaluates:
- HTTP security headers (CSP, X‑Frame‑Options, HSTS)
- SSL/TLS certificate validity and cipher strength
- CMS detection via meta tags and server headers

The scan runs asynchronously using **Celery** + **Redis**, exposing a clean **FastAPI** backend and a modern **React** frontend built with **Vite**.

## Tech Stack
- **Backend**: FastAPI, Celery, Redis, Python 3.11
- **Frontend**: React.js (Vite), CSS (custom premium design), Chart.js for gauge
- **PDF Export**: WeasyPrint (HTML → PDF)
- **Rate Limiting**: slowapi (10 requests/min per IP)

---

*See the other README files in the `docs/` folder for detailed module docs, API specs, and deployment instructions.*

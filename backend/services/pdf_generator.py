"""PDF Export service for VulTure Security Reports.

Uses WeasyPrint to transform scan results into an executive PDF audit report.
"""

from typing import Dict, Any
from datetime import datetime
import weasyprint

def generate_pdf_report(scan_data: Dict[str, Any]) -> bytes:
    result = scan_data.get("result") or {}
    url = scan_data.get("url", result.get("url", "N/A"))
    score = result.get("score", scan_data.get("score", 0))
    grade = result.get("grade", scan_data.get("grade", "F"))
    timestamp = scan_data.get("created_at") or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    details = result.get("details", {})
    headers_data = details.get("headers", {}).get("items", [])
    ssl_data = details.get("ssl", {})
    tech_data = details.get("cms", {}).get("technologies", [])
    remediations = result.get("remediations", [])

    grade_colors = {
        "A": "#10b981",
        "B": "#06b6d4",
        "C": "#f59e0b",
        "D": "#f97316",
        "F": "#ef4444"
    }
    badge_color = grade_colors.get(grade, "#ef4444")

    # Build Header rows
    header_rows = ""
    for h in headers_data:
        status_badge = '<span class="badge badge-pass">PASSED</span>' if h.get("present") else '<span class="badge badge-fail">MISSING</span>'
        header_rows += f"""
        <tr>
            <td><strong>{h.get('title')}</strong><br><small style="color: #64748b;">{h.get('header')}</small></td>
            <td>{status_badge}</td>
            <td><span class="severity severity-{h.get('severity', '').lower()}">{h.get('severity')}</span></td>
            <td>{h.get('description', '')}</td>
        </tr>
        """

    # Build Remediation items
    remediation_items = ""
    for r in remediations:
        remediation_items += f"""
        <div class="remediation-card">
            <h4>[{r.get('category')}] {r.get('title')} <span class="severity severity-{r.get('severity', '').lower()}">{r.get('severity')}</span></h4>
            <p>{r.get('advice')}</p>
        </div>
        """
    if not remediation_items:
        remediation_items = "<p>No critical remediation items detected. Good job!</p>"

    # Build Tech Stack tags
    tech_tags = "".join(f'<span class="tech-tag">{t.get("name")} ({t.get("category")})</span>' for t in tech_data) or "<span>No signatures identified.</span>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>VulTure Security Audit Report - {url}</title>
        <style>
            @page {{
                size: A4;
                margin: 20mm;
                @bottom-right {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 9pt;
                    color: #94a3b8;
                }}
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                color: #0f172a;
                line-height: 1.5;
                font-size: 10pt;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                border-bottom: 2px solid #0284c7;
                padding-bottom: 12px;
                margin-bottom: 20px;
            }}
            .title {{
                font-size: 20pt;
                font-weight: 800;
                color: #0f172a;
                margin: 0;
            }}
            .subtitle {{
                font-size: 10pt;
                color: #64748b;
                margin-top: 4px;
            }}
            .summary-box {{
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 24px;
                display: table;
                width: 100%;
            }}
            .summary-col {{
                display: table-cell;
                vertical-align: middle;
            }}
            .grade-badge {{
                display: inline-block;
                width: 70px;
                height: 70px;
                line-height: 70px;
                text-align: center;
                background-color: {badge_color};
                color: white;
                font-size: 32pt;
                font-weight: 800;
                border-radius: 50%;
            }}
            .score-text {{
                font-size: 24pt;
                font-weight: 700;
                color: #0f172a;
            }}
            h2 {{
                font-size: 14pt;
                color: #0f172a;
                border-bottom: 1px solid #cbd5e1;
                padding-bottom: 4px;
                margin-top: 24px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 8px;
                font-size: 9pt;
            }}
            th, td {{
                border: 1px solid #e2e8f0;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background: #f1f5f9;
                font-weight: 600;
            }}
            .badge {{
                display: inline-block;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 8pt;
                font-weight: 700;
            }}
            .badge-pass {{ background: #dcfce7; color: #15803d; }}
            .badge-fail {{ background: #fee2e2; color: #b91c1c; }}
            .severity {{
                display: inline-block;
                padding: 1px 6px;
                border-radius: 4px;
                font-size: 8pt;
                font-weight: 600;
            }}
            .severity-high {{ background: #fecaca; color: #991b1b; }}
            .severity-medium {{ background: #fef3c7; color: #92400e; }}
            .severity-low {{ background: #e0f2fe; color: #075985; }}
            .remediation-card {{
                background: #ffffff;
                border-left: 4px solid #0284c7;
                border-top: 1px solid #e2e8f0;
                border-right: 1px solid #e2e8f0;
                border-bottom: 1px solid #e2e8f0;
                padding: 10px 14px;
                margin-bottom: 10px;
                border-radius: 0 6px 6px 0;
            }}
            .remediation-card h4 {{
                margin: 0 0 4px 0;
                font-size: 10pt;
            }}
            .remediation-card p {{
                margin: 0;
                color: #334155;
                font-size: 9pt;
            }}
            .tech-tag {{
                display: inline-block;
                background: #e2e8f0;
                color: #1e293b;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 8.5pt;
                margin-right: 6px;
                margin-bottom: 6px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1 class="title">VulTure Security Scanner</h1>
                <div class="subtitle">Automated Passive Vulnerability & Architecture Audit</div>
            </div>
            <div style="text-align: right;">
                <div style="font-weight: 600;">Confidential Audit Report</div>
                <div style="font-size: 8.5pt; color: #64748b;">Generated: {timestamp}</div>
            </div>
        </div>

        <div class="summary-box">
            <div class="summary-col" style="width: 100px; text-align: center;">
                <div class="grade-badge">{grade}</div>
            </div>
            <div class="summary-col" style="padding-left: 20px;">
                <div style="font-size: 9pt; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Target Scanned</div>
                <div style="font-size: 13pt; font-weight: 700; word-break: break-all;">{url}</div>
                <div class="score-text">{score} <span style="font-size: 12pt; color: #64748b;">/ 100 Overall Score</span></div>
            </div>
        </div>

        <h2>1. SSL/TLS Certificate & Transport Encryption</h2>
        <table>
            <tr>
                <th style="width: 25%;">Valid Certificate</th>
                <td>{'Yes' if ssl_data.get('valid') else 'No (Risk: Insecure Transport)'}</td>
            </tr>
            <tr>
                <th>Certificate Issuer</th>
                <td>{ssl_data.get('issuer', 'N/A')}</td>
            </tr>
            <tr>
                <th>Expiration Date</th>
                <td>{ssl_data.get('expiration_date', 'N/A')} ({ssl_data.get('days_left', 0)} days remaining)</td>
            </tr>
            <tr>
                <th>Protocol & Cipher</th>
                <td>{ssl_data.get('protocol', 'N/A')} &mdash; {ssl_data.get('cipher_name', 'N/A')} ({ssl_data.get('cipher_strength', 'N/A')} suite)</td>
            </tr>
        </table>

        <h2>2. HTTP Security Headers Audit</h2>
        <table>
            <thead>
                <tr>
                    <th style="width: 25%;">Header Policy</th>
                    <th style="width: 15%;">Status</th>
                    <th style="width: 15%;">Severity</th>
                    <th style="width: 45%;">Impact & Protection</th>
                </tr>
            </thead>
            <tbody>
                {header_rows}
            </tbody>
        </table>

        <h2>3. Identified Technology Stack</h2>
        <div style="margin-top: 8px;">
            {tech_tags}
        </div>

        <h2>4. Actionable Remediation Guidance</h2>
        <div style="margin-top: 10px;">
            {remediation_items}
        </div>
    </body>
    </html>
    """

    return weasyprint.HTML(string=html_content).write_pdf()

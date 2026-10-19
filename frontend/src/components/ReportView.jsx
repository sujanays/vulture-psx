import React, { useState } from 'react';
import ScoreGauge from './ScoreGauge';

export default function ReportView({ result, taskId, onRescan }) {
  const [activeTab, setActiveTab] = useState('headers');
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api';

  if (!result) return null;

  const {
    url,
    score = 0,
    grade = 'F',
    passed = [],
    failed = [],
    remediations = [],
    details = {}
  } = result;

  const headersItems = details.headers?.items || [];
  const sslData = details.ssl || {};
  const cmsData = details.cms || {};
  const cookiesData = details.cookies || {};
  const technologies = cmsData.technologies || [];

  const handleDownloadPdf = async () => {
    if (!taskId) return;
    setIsDownloadingPdf(true);
    try {
      const response = await fetch(`${backendUrl}/scan/${taskId}/pdf`);
      if (!response.ok) throw new Error('PDF generation failed');
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      const cleanHost = (url || 'report').replace(/https?:\/\//, '').replace(/[/\\?%*:|"<>]/g, '_');
      link.setAttribute('download', `vulture_report_${cleanHost}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Could not download PDF report: ' + err.message);
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  return (
    <div className="report-container">
      {/* Hero Summary Card */}
      <div className="report-hero">
        <div className="hero-left">
          <ScoreGauge score={score} grade={grade} />
        </div>
        <div className="hero-center">
          <div className="target-url-badge">
            <span className="live-dot"></span>
            {url}
          </div>
          <h2 className="report-target-title">Security Posture Assessment</h2>
          <div className="stats-pills">
            <div className="stat-pill pill-pass">
              <span className="stat-num">{passed.length}</span>
              <span className="stat-text">Checks Passed</span>
            </div>
            <div className="stat-pill pill-fail">
              <span className="stat-num">{failed.length}</span>
              <span className="stat-text">Issues Detected</span>
            </div>
            <div className="stat-pill pill-warn">
              <span className="stat-num">{remediations.length}</span>
              <span className="stat-text">Remediations</span>
            </div>
          </div>
        </div>
        <div className="hero-actions">
          <button
            className="action-btn btn-pdf"
            onClick={handleDownloadPdf}
            disabled={isDownloadingPdf}
          >
            {isDownloadingPdf ? 'Generating PDF...' : '⬇ Export PDF Report'}
          </button>
          {onRescan && (
            <button className="action-btn btn-rescan" onClick={() => onRescan(url)}>
              🔄 Re-scan Target
            </button>
          )}
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="report-tabs">
        <button
          className={`tab-btn ${activeTab === 'headers' ? 'active' : ''}`}
          onClick={() => setActiveTab('headers')}
        >
          🛡️ Security Headers ({headersItems.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'ssl' ? 'active' : ''}`}
          onClick={() => setActiveTab('ssl')}
        >
          🔒 SSL / TLS
        </button>
        <button
          className={`tab-btn ${activeTab === 'tech' ? 'active' : ''}`}
          onClick={() => setActiveTab('tech')}
        >
          ⚙️ Tech Stack & CMS ({technologies.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'cookies' ? 'active' : ''}`}
          onClick={() => setActiveTab('cookies')}
        >
          🍪 Cookies ({cookiesData.cookies?.length || 0})
        </button>
        <button
          className={`tab-btn ${activeTab === 'remediations' ? 'active' : ''}`}
          onClick={() => setActiveTab('remediations')}
        >
          💡 Actionable Fixes ({remediations.length})
        </button>
      </div>

      {/* Tab 1: Headers */}
      {activeTab === 'headers' && (
        <div className="tab-pane">
          <div className="table-wrapper">
            <table className="vul-table">
              <thead>
                <tr>
                  <th>Header Directive</th>
                  <th>Status</th>
                  <th>Severity</th>
                  <th>Description & Mitigation</th>
                </tr>
              </thead>
              <tbody>
                {headersItems.map((h, i) => (
                  <tr key={i} className={h.present ? 'row-pass' : 'row-fail'}>
                    <td className="cell-header-name">
                      <strong>{h.title}</strong>
                      <code>{h.header}</code>
                    </td>
                    <td>
                      <span className={`badge ${h.present ? 'badge-pass' : 'badge-fail'}`}>
                        {h.present ? 'PRESENT' : 'MISSING'}
                      </span>
                    </td>
                    <td>
                      <span className={`severity-tag severity-${h.severity.toLowerCase()}`}>
                        {h.severity}
                      </span>
                    </td>
                    <td className="cell-desc">
                      <p className="desc-text">{h.description}</p>
                      {!h.present && (
                        <div className="remediation-snippet">
                          <strong>Fix: </strong>
                          <code>{h.remediation}</code>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: SSL/TLS */}
      {activeTab === 'ssl' && (
        <div className="tab-pane">
          <div className="grid-2col">
            <div className="card">
              <h3>Certificate Validity</h3>
              <div className="ssl-status-row">
                <span className={`status-indicator ${sslData.valid ? 'ind-pass' : 'ind-fail'}`}></span>
                <span className="ssl-status-text">
                  {sslData.valid ? 'Certificate is Valid & Trusted' : 'Certificate Error or Insecure'}
                </span>
              </div>
              <ul className="info-list">
                <li>
                  <span className="info-label">Issuer:</span>
                  <span className="info-val">{sslData.issuer || 'N/A'}</span>
                </li>
                <li>
                  <span className="info-label">Expires:</span>
                  <span className="info-val">{sslData.expiration_date || 'N/A'} ({sslData.days_left || 0} days remaining)</span>
                </li>
              </ul>
            </div>

            <div className="card">
              <h3>Cipher & Protocol</h3>
              <ul className="info-list">
                <li>
                  <span className="info-label">Protocol:</span>
                  <span className="info-val highlight">{sslData.protocol || 'N/A'}</span>
                </li>
                <li>
                  <span className="info-label">Cipher Suite:</span>
                  <span className="info-val">{sslData.cipher_name || 'N/A'}</span>
                </li>
                <li>
                  <span className="info-label">Cipher Strength:</span>
                  <span className={`severity-tag severity-${sslData.cipher_strength === 'strong' ? 'pass' : 'high'}`}>
                    {sslData.cipher_strength?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Tech & CMS */}
      {activeTab === 'tech' && (
        <div className="tab-pane">
          <div className="card">
            <h3>Detected Technologies & Frameworks</h3>
            {technologies.length > 0 ? (
              <div className="tech-tags-grid">
                {technologies.map((t, idx) => (
                  <div key={idx} className="tech-card">
                    <span className="tech-category">{t.category}</span>
                    <span className="tech-name">{t.name}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-msg">No overt technology signatures detected in HTML or headers.</p>
            )}

            {cmsData.findings && cmsData.findings.length > 0 && (
              <div className="findings-subbox">
                <h4>Fingerprint Details & Disclosure Warnings</h4>
                <ul className="findings-list">
                  {cmsData.findings.map((f, idx) => (
                    <li key={idx} className={f.includes('Information Disclosure') ? 'warn-item' : 'info-item'}>
                      {f}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 4: Cookies */}
      {activeTab === 'cookies' && (
        <div className="tab-pane">
          <div className="card">
            <h3>Cookie Security Flags</h3>
            {cookiesData.cookies && cookiesData.cookies.length > 0 ? (
              <table className="vul-table">
                <thead>
                  <tr>
                    <th>Cookie Name</th>
                    <th>Secure</th>
                    <th>HttpOnly</th>
                    <th>SameSite</th>
                  </tr>
                </thead>
                <tbody>
                  {cookiesData.cookies.map((c, i) => (
                    <tr key={i}>
                      <td><code>{c.name}</code></td>
                      <td>
                        <span className={`badge ${c.secure ? 'badge-pass' : 'badge-fail'}`}>
                          {c.secure ? 'YES' : 'NO'}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${c.httponly ? 'badge-pass' : 'badge-fail'}`}>
                          {c.httponly ? 'YES' : 'NO'}
                        </span>
                      </td>
                      <td>
                        <span className="badge badge-neutral">{c.samesite}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="empty-msg">No Set-Cookie headers were returned on the root response.</p>
            )}
          </div>
        </div>
      )}

      {/* Tab 5: Remediations */}
      {activeTab === 'remediations' && (
        <div className="tab-pane">
          {remediations.length > 0 ? (
            <div className="remediations-list">
              {remediations.map((rem, i) => (
                <div key={i} className="remediation-item">
                  <div className="rem-header">
                    <span className={`severity-tag severity-${rem.severity.toLowerCase()}`}>
                      {rem.severity}
                    </span>
                    <span className="rem-category">[{rem.category}]</span>
                    <h4 className="rem-title">{rem.title}</h4>
                  </div>
                  <div className="rem-body">
                    <p>{rem.advice}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="card text-center">
              <span className="all-clear-icon">🎉</span>
              <h3>No Actionable Deficiencies Detected</h3>
              <p>The scanned target meets all core passive security standards.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

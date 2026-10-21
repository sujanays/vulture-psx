import React, { useState } from 'react';
import axios from 'axios';

const SAMPLE_TARGETS = [
  'https://www.amazon.com',
  'https://wordpress.org',
  'https://github.com',
  'https://example.com'
];

/**
 * Normalizes user input into a valid URL.
 * e.g.:
 *  - "abc.com" -> "https://www.abc.com"
 *  - "amazon.com" -> "https://www.amazon.com"
 *  - "https://amazon.com" -> "https://www.amazon.com"
 *  - "http://sub.domain.com" -> "http://sub.domain.com"
 */
export function normalizeTargetUrl(input) {
  let clean = (input || '').trim();
  if (!clean) return '';

  let scheme = 'https://';
  let rest = clean;

  if (clean.toLowerCase().startsWith('http://')) {
    scheme = 'http://';
    rest = clean.slice(7);
  } else if (clean.toLowerCase().startsWith('https://')) {
    scheme = 'https://';
    rest = clean.slice(8);
  }

  // Separate domain and path/query
  const slashIdx = rest.indexOf('/');
  let domain = slashIdx !== -1 ? rest.slice(0, slashIdx) : rest;
  const path = slashIdx !== -1 ? rest.slice(slashIdx) : '';

  // If domain is like abc.com or amazon.com (single dot, no www.), prepend www.
  const domainParts = domain.split('.');
  if (domainParts.length === 2 && !domain.toLowerCase().startsWith('www.')) {
    domain = `www.${domain}`;
  }

  return `${scheme}${domain}${path}`;
}

export default function ScanForm({ onTaskStarted, isLoading }) {
  const [url, setUrl] = useState('');
  const [error, setError] = useState(null);
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api';

  const handleBlur = () => {
    if (url.trim()) {
      const normalized = normalizeTargetUrl(url);
      setUrl(normalized);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    const rawInput = url.trim();
    if (!rawInput) {
      setError('Please provide a URL to scan.');
      return;
    }

    // Transform input to valid canonical URL (e.g. abc.com -> https://www.abc.com)
    const targetUrl = normalizeTargetUrl(rawInput);
    // Update the input box value visually
    setUrl(targetUrl);

    try {
      const resp = await axios.post(`${backendUrl}/scan/`, { url: targetUrl });
      if (resp.data && resp.data.task_id) {
        onTaskStarted(resp.data.task_id, targetUrl);
      }
    } catch (err) {
      const msg = err.response?.data?.detail?.[0]?.msg || err.response?.data?.detail || err.message || 'Failed to trigger scan.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    }
  };

  return (
    <div className="scan-form-container">
      <form onSubmit={handleSubmit} className="scan-form">
        <div className="input-group">
          <span className="input-prefix">TARGET</span>
          <input
            type="text"
            className="scan-input"
            placeholder="Paste the link here..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onBlur={handleBlur}
            disabled={isLoading}
          />
          <button type="submit" className="scan-btn" disabled={isLoading}>
            {isLoading ? 'Scanning...' : 'Inspect Target →'}
          </button>
        </div>
      </form>

      {error && <div className="error-banner">⚠️ {error}</div>}

      <div className="sample-targets">
        <span className="sample-label">Quick Test:</span>
        {SAMPLE_TARGETS.map((sample) => (
          <button
            key={sample}
            type="button"
            className="sample-chip"
            onClick={() => {
              const normalized = normalizeTargetUrl(sample);
              setUrl(normalized);
            }}
            disabled={isLoading}
          >
            {sample.replace('https://', '')}
          </button>
        ))}
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import axios from 'axios';

const SAMPLE_TARGETS = [
  'https://wordpress.org',
  'https://github.com',
  'https://example.com',
  'https://cloudflare.com'
];

export default function ScanForm({ onTaskStarted, isLoading }) {
  const [url, setUrl] = useState('');
  const [error, setError] = useState(null);
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    let targetUrl = url.trim();
    if (!targetUrl) {
      setError('Please provide a URL to scan.');
      return;
    }
    if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
      targetUrl = `https://${targetUrl}`;
    }

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
            placeholder="e.g. https://your-website.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
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
            onClick={() => setUrl(sample)}
            disabled={isLoading}
          >
            {sample.replace('https://', '')}
          </button>
        ))}
      </div>
    </div>
  );
}

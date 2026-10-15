import React, { useState } from 'react';
import axios from 'axios';

function ScanForm({ onTaskStarted }) {
  const [url, setUrl] = useState('');
  const [error, setError] = useState(null);
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const response = await axios.post(`${backendUrl}/scan/`, { url });
      const { task_id } = response.data;
      onTaskStarted(task_id);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    }
  };

  return (
    <div className="scan-form">
      <h2>Start a Security Scan</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="url"
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
          className="url-input"
        />
        <button type="submit" className="submit-btn">Scan</button>
      </form>
      {error && <p className="error-msg">{error}</p>}
    </div>
  );
}

export default ScanForm;

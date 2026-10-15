import React, { useEffect, useState } from 'react';
import axios from 'axios';

function ScanStatus({ taskId, onResult }) {
  const [status, setStatus] = useState('PENDING');
  const [result, setResult] = useState(null);
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api';

  useEffect(() => {
    if (!taskId) return;
    const interval = setInterval(async () => {
      try {
        const resp = await axios.get(`${backendUrl}/scan/${taskId}/status`);
        const data = resp.data;
        setStatus(data.status);
        if (data.status === 'SUCCESS' && data.result) {
          setResult(data.result);
          clearInterval(interval);
          onResult(data.result);
        } else if (data.status === 'FAILURE') {
          clearInterval(interval);
          setStatus('FAILURE');
        }
      } catch (err) {
        console.error('Polling error', err);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [taskId]);

  return (
    <div className="scan-status">
      <p>Scanning status: {status}</p>
      {status === 'FAILURE' && <p className="error-msg">Scan failed.</p>}
    </div>
  );
}

export default ScanStatus;

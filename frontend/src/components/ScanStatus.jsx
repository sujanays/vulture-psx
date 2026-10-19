import React, { useEffect, useState } from 'react';
import axios from 'axios';
import ScanProgress from './ScanProgress';

export default function ScanStatus({ taskId, onResult, onError }) {
  const [status, setStatus] = useState('PENDING');
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api';

  useEffect(() => {
    if (!taskId) return;
    let isMounted = true;

    const interval = setInterval(async () => {
      try {
        const resp = await axios.get(`${backendUrl}/scan/${taskId}/status`);
        const data = resp.data;
        if (!isMounted) return;

        setStatus(data.status);
        if (data.status === 'SUCCESS' && data.result) {
          clearInterval(interval);
          onResult(data.result);
        } else if (data.status === 'FAILURE') {
          clearInterval(interval);
          setStatus('FAILURE');
          if (onError) onError(data.error || 'The security scan encountered an error.');
        }
      } catch (err) {
        console.error('Scan polling error:', err);
      }
    }, 1800);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [taskId]);

  return <ScanProgress status={status} />;
}

import React, { useEffect, useState } from 'react';
import axios from 'axios';

export default function HistoryDrawer({ isOpen, onClose, onSelectScan }) {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(false);
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api';

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const resp = await axios.get(`${backendUrl}/scans/`);
      setScans(resp.data || []);
    } catch (err) {
      console.error('Failed to load history', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen]);

  const handleDelete = async (e, taskId) => {
    e.stopPropagation();
    try {
      await axios.delete(`${backendUrl}/scan/${taskId}`);
      setScans((prev) => prev.filter((s) => s.task_id !== taskId));
    } catch (err) {
      alert('Could not delete scan: ' + err.message);
    }
  };

  if (!isOpen) return null;

  const getGradeColor = (g) => {
    switch (g) {
      case 'A': return '#10b981';
      case 'B': return '#06b6d4';
      case 'C': return '#f59e0b';
      case 'D': return '#f97316';
      default: return '#ef4444';
    }
  };

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div className="drawer-content" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <h3>🕒 Scan History</h3>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        {loading ? (
          <div className="drawer-loading">Loading scan records...</div>
        ) : scans.length === 0 ? (
          <div className="drawer-empty">No scan records found in persistent storage.</div>
        ) : (
          <div className="history-list">
            {scans.map((s) => (
              <div
                key={s.task_id}
                className="history-item"
                onClick={() => {
                  onSelectScan(s);
                  onClose();
                }}
              >
                <div
                  className="history-grade-tag"
                  style={{ backgroundColor: getGradeColor(s.grade) }}
                >
                  {s.grade || '?'}
                </div>
                <div className="history-info">
                  <div className="history-url">{s.url}</div>
                  <div className="history-meta">
                    <span>Score: {s.score ?? 'N/A'}/100</span>
                    <span>•</span>
                    <span>{s.created_at ? new Date(s.created_at).toLocaleDateString() : 'Recent'}</span>
                    <span>•</span>
                    <span className="history-status">{s.status}</span>
                  </div>
                </div>
                <button
                  className="history-del-btn"
                  title="Delete record"
                  onClick={(e) => handleDelete(e, s.task_id)}
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

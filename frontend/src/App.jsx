import React, { useState } from 'react';
import ScanForm from './components/ScanForm';
import ScanStatus from './components/ScanStatus';
import ReportView from './components/ReportView';
import HistoryDrawer from './components/HistoryDrawer';
import './App.css';

function App() {
  const [taskId, setTaskId] = useState(null);
  const [currentUrl, setCurrentUrl] = useState('');
  const [result, setResult] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [scanError, setScanError] = useState(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  const handleTaskStarted = (id, targetUrl) => {
    setTaskId(id);
    setCurrentUrl(targetUrl);
    setResult(null);
    setScanError(null);
    setIsScanning(true);
  };

  const handleResult = (data) => {
    setResult(data);
    setIsScanning(false);
  };

  const handleScanError = (err) => {
    setScanError(err);
    setIsScanning(false);
  };

  const handleSelectScan = (scanRecord) => {
    setTaskId(scanRecord.task_id);
    setCurrentUrl(scanRecord.url);
    setResult(scanRecord.result);
    setScanError(scanRecord.error || null);
    setIsScanning(false);
  };

  return (
    <div className="vulture-app">
      {/* Top Navigation */}
      <header className="app-header">
        <div className="header-brand">
          <div className="logo-icon">🦅</div>
          <div>
            <h1 className="brand-title">VulTure</h1>
            <p className="brand-subtitle">Passive Vulnerability & Security Posture Scanner</p>
          </div>
        </div>
        <div className="header-nav">
          <div className="status-pill">
            <span className="live-dot"></span>
            <span>Engine Active</span>
          </div>
          <button
            className="history-nav-btn"
            onClick={() => setIsHistoryOpen(true)}
          >
            📜 Scan History
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Scan Input Section */}
        <section className="scan-hero-section">
          <ScanForm onTaskStarted={handleTaskStarted} isLoading={isScanning} />
        </section>

        {/* Scan Progress State */}
        {isScanning && taskId && (
          <section className="progress-section">
            <ScanStatus
              taskId={taskId}
              onResult={handleResult}
              onError={handleScanError}
            />
          </section>
        )}

        {/* Scan Error State */}
        {scanError && !isScanning && (
          <div className="error-card">
            <h3>❌ Scan Interrupted</h3>
            <p>{scanError}</p>
          </div>
        )}

        {/* Scan Report State */}
        {result && !isScanning && (
          <section className="report-section">
            <ReportView
              result={result}
              taskId={taskId}
              onRescan={(targetUrl) => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }}
            />
          </section>
        )}
      </main>

      {/* History Slide-over Drawer */}
      <HistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectScan={handleSelectScan}
      />

      <footer className="app-footer">
        <p>VulTure Security Scanner &bull; Passive Non-Intrusive Assessment Engine</p>
        <p className="disclaimer">Only evaluate domains you own or have explicit authorization to test.</p>
      </footer>
    </div>
  );
}

export default App;

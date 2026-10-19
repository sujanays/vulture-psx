import React, { useEffect, useState } from 'react';

const STEPS = [
  { id: 1, label: 'Host Resolution & SSRF Validation' },
  { id: 2, label: 'SSL/TLS Handshake & Cipher Suite Analysis' },
  { id: 3, label: 'HTTP Security Headers Verification' },
  { id: 4, label: 'Cookie Security & Tech Stack Fingerprinting' },
  { id: 5, label: 'Compiling Final Audit Report' }
];

export default function ScanProgress({ status }) {
  const [activeStep, setActiveStep] = useState(1);

  useEffect(() => {
    const timer = setInterval(() => {
      setActiveStep((prev) => (prev < 5 ? prev + 1 : prev));
    }, 1200);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="scan-progress-box">
      <div className="progress-header">
        <div className="spinner"></div>
        <div>
          <h3 className="progress-title">Scanning Target Website...</h3>
          <p className="progress-sub">Status: <span className="status-badge">{status}</span></p>
        </div>
      </div>
      <div className="steps-list">
        {STEPS.map((step) => {
          const isDone = activeStep > step.id;
          const isCurrent = activeStep === step.id;
          return (
            <div
              key={step.id}
              className={`step-item ${isDone ? 'step-done' : ''} ${isCurrent ? 'step-current' : ''}`}
            >
              <div className="step-icon">
                {isDone ? '✓' : isCurrent ? '●' : '○'}
              </div>
              <span className="step-label">{step.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

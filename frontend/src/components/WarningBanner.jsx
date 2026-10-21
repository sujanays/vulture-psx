import React from 'react';

/**
 * Compliance & Safety Disclaimer Warning Banner
 * 
 * Required for safe and authorized usage of the scanner.
 * Displayed prominently above the URL submission form input.
 */
export default function WarningBanner() {
  return (
    <div
      className="compliance-warning-banner"
      role="alert"
      aria-label="Legal and ethical usage disclaimer"
    >
      <div className="warning-banner-icon" aria-hidden="true">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="warning-icon-svg"
        >
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      </div>
      <span className="warning-banner-text">
        Only scan websites you own. This tool performs passive analysis only.
      </span>
    </div>
  );
}

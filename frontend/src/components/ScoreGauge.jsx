import React from 'react';

export default function ScoreGauge({ score = 0, grade = 'F' }) {
  const radius = 72;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const getGradeColor = (g) => {
    switch (g) {
      case 'A': return '#10b981'; // emerald
      case 'B': return '#06b6d4'; // cyan
      case 'C': return '#f59e0b'; // amber
      case 'D': return '#f97316'; // orange
      default: return '#ef4444'; // crimson
    }
  };

  const color = getGradeColor(grade);

  return (
    <div className="gauge-container">
      <svg className="gauge-svg" width="180" height="180" viewBox="0 0 180 180">
        <circle
          className="gauge-bg"
          cx="90"
          cy="90"
          r={radius}
          strokeWidth="14"
        />
        <circle
          className="gauge-progress"
          cx="90"
          cy="90"
          r={radius}
          strokeWidth="14"
          stroke={color}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform="rotate(-90 90 90)"
        />
      </svg>
      <div className="gauge-center">
        <span className="gauge-grade" style={{ color }}>{grade}</span>
        <span className="gauge-score">{score}<span>/100</span></span>
      </div>
    </div>
  );
}

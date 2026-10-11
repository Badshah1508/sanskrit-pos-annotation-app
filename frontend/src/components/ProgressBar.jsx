import React from 'react';

export default function ProgressBar({ completed, total, percentage }) {
  const percent = percentage !== undefined ? percentage : (total > 0 ? ((completed / total) * 100).toFixed(1) : 0);

  return (
    <div style={{ width: '100%', margin: '0.75rem 0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', marginBottom: '0.35rem' }}>
        <span style={{ fontWeight: 500, color: 'var(--text-muted)' }}>Progress: {completed} / {total} sentences</span>
        <span style={{ fontWeight: 700, color: 'var(--primary-color)' }}>{percent}%</span>
      </div>
      <div style={{
        width: '100%',
        height: '10px',
        backgroundColor: '#e2e8f0',
        borderRadius: '9999px',
        overflow: 'hidden'
      }}>
        <div
          style={{
            width: `${Math.min(100, Math.max(0, percent))}%`,
            height: '100%',
            backgroundColor: '#16a34a',
            transition: 'width 0.4s ease-in-out'
          }}
        />
      </div>
    </div>
  );
}

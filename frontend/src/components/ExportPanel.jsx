import React, { useState } from 'react';
import { exportApi } from '../api';

export default function ExportPanel({ onBack }) {
  const [downloading, setDownloading] = useState(false);
  const [status, setStatus] = useState(null);

  const handleDownload = async () => {
    setDownloading(true);
    setStatus(null);
    try {
      const data = await exportApi.downloadVerifiedCsv();

      // Create download link
      const blob = new Blob([data], { type: 'text/csv;charset=utf-8;' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'final_pos_verified.csv');
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);

      setStatus({ type: 'success', text: 'Verified CSV downloaded successfully from database!' });
    } catch (err) {
      console.error('Export download error:', err);
      setStatus({
        type: 'error',
        text: 'Failed to download verified CSV: ' + (err.response?.data?.detail || err.message || 'Server error')
      });
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div style={{ background: 'white', padding: '2rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', maxWidth: '700px', margin: '0 auto' }}>
      <button className="btn btn-secondary" onClick={onBack} style={{ marginBottom: '1.5rem' }}>
        ← Back to Dashboard
      </button>

      <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--primary-color)', marginBottom: '0.5rem' }}>
        Verified Dataset Export (CSV)
      </h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: 1.6 }}>
        Download the gold-standard verified Sanskrit POS dataset for your dissertation.
        The export includes only sentences that have been reviewed and verified by an expert, along with their approved Sanskrit Consortium tags and full provenance metadata.
      </p>

      {status && (
        <div className={`alert alert-${status.type}`}>
          {status.text}
        </div>
      )}

      <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: 'var(--radius-sm)', border: '1px solid #e2e8f0', marginBottom: '1.5rem' }}>
        <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.5rem', color: '#1e293b' }}>
          Export File Specifications:
        </h4>
        <ul style={{ paddingLeft: '1.25rem', color: '#475569', fontSize: '0.85rem', lineHeight: 1.6 }}>
          <li><strong>Format:</strong> UTF-8 encoded CSV (Preserves Devanagari script accurately).</li>
          <li><strong>Filename:</strong> <code>final_pos_verified.csv</code></li>
          <li><strong>Columns included:</strong> <code>doc_id, sentence_id, annotation_id, sentence_text, token_id, token, lemma, upos, stanza_upos, xpos, feats, gold_sanskrit_tag, annotation_status, annotation_note, verified_by, verified_at</code></li>
        </ul>
      </div>

      <button
        className="btn btn-primary"
        onClick={handleDownload}
        disabled={downloading}
        style={{ padding: '0.8rem 1.75rem', fontSize: '1rem' }}
      >
        {downloading ? 'Preparing CSV...' : '📥 Download final_pos_verified.csv'}
      </button>
    </div>
  );
}

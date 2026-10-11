import React, { useState, useEffect } from 'react';
import { datasetApi } from '../api';
import ProgressBar from './ProgressBar';

export default function Dashboard({ user, onStartAnnotation, onNavigateExport }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoading(true);
    try {
      const data = await datasetApi.getStats();
      setStats(data);
    } catch (err) {
      setError('Could not load statistics. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading dataset statistics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-error" style={{ margin: '2rem' }}>
        {error}
      </div>
    );
  }

  return (
    <div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        <div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--primary-color)' }}>
            Welcome, {user?.username || 'Expert'}!
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Sanskrit News-Domain POS Annotation Status (70% Portion)
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            className="btn btn-primary"
            onClick={onStartAnnotation}
            style={{ padding: '0.75rem 1.5rem', fontSize: '1rem' }}
          >
            ▶ Resume Annotation
          </button>
          {user?.role === 'admin' && (
            <button
              className="btn btn-secondary"
              onClick={onNavigateExport}
            >
              📥 Export CSV
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar Card */}
      <div style={{
        background: 'white',
        padding: '1.5rem',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-color)',
        boxShadow: 'var(--shadow-sm)',
        marginBottom: '1.5rem'
      }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '0.5rem' }}>
          Overall Corpus Verification Progress
        </h3>
        <ProgressBar
          completed={stats?.verified_sentences || 0}
          total={stats?.total_sentences || 0}
          percentage={stats?.completion_percentage || 0}
        />
      </div>

      {/* Stats Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '1.25rem',
        marginBottom: '2rem'
      }}>
        <div style={{
          background: 'white',
          padding: '1.25rem',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-color)',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase' }}>
            Total Sentences
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#1e293b', marginTop: '0.25rem' }}>
            {stats?.total_sentences || 0}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem' }}>
            {stats?.total_tokens || 0} total tokens
          </div>
        </div>

        <div style={{
          background: 'white',
          padding: '1.25rem',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-color)',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <div style={{ color: '#d97706', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase' }}>
            Pending Verification
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#b45309', marginTop: '0.25rem' }}>
            {stats?.pending_sentences || 0}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem' }}>
            Awaiting expert review
          </div>
        </div>

        <div style={{
          background: 'white',
          padding: '1.25rem',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-color)',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <div style={{ color: '#0284c7', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase' }}>
            In Progress (Drafts)
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#0369a1', marginTop: '0.25rem' }}>
            {stats?.in_progress_sentences || 0}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem' }}>
            Saved partial edits
          </div>
        </div>

        <div style={{
          background: 'white',
          padding: '1.25rem',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-color)',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <div style={{ color: '#16a34a', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase' }}>
            Verified Sentences
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#15803d', marginTop: '0.25rem' }}>
            {stats?.verified_sentences || 0}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem' }}>
            Gold-standard validated
          </div>
        </div>
      </div>

      {/* Instructions Card for Experts */}
      <div style={{
        background: '#f8fafc',
        border: '1px solid #e2e8f0',
        borderRadius: 'var(--radius-md)',
        padding: '1.5rem'
      }}>
        <h4 style={{ fontWeight: 600, marginBottom: '0.5rem', color: '#334155' }}>
          💡 Instructions for Sanskrit Language Experts
        </h4>
        <ul style={{ paddingLeft: '1.25rem', color: '#475569', fontSize: '0.9rem', lineHeight: 1.6 }}>
          <li>Examine the Sanskrit sentence and each individual token in Devanagari script.</li>
          <li>The Stanza UPOS tag is provided as an automated baseline hint — please do not assume it is authoritative.</li>
          <li>Assign the appropriate <strong>Sanskrit Consortium POS tag</strong> (e.g., <code>N, KP, A, AVN</code>) from the dropdown.</li>
          <li>Click <strong>Save Draft</strong> if you want to pause your work without marking the sentence verified.</li>
          <li>Click <strong>Save & Next</strong> to finalize all tags, validate completeness, and move directly to the next pending sentence.</li>
        </ul>
      </div>
    </div>
  );
}

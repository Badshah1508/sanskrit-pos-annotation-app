import React, { useState, useEffect } from 'react';
import { datasetApi } from '../api';
import ProgressBar from './ProgressBar';

const EXPERT_WORKSPACES = [
  { key: 'user1', label: 'User 1', range: 'Sentences 1–1,000', docs: 868, count: 1000 },
  { key: 'user2', label: 'User 2', range: 'Sentences 1,001–2,000', docs: 874, count: 1000 },
  { key: 'user3', label: 'User 3', range: 'Sentences 2,001–3,000', docs: 890, count: 1000 },
  { key: 'user4', label: 'User 4', range: 'Sentences 3,001–4,000', docs: 883, count: 1000 },
  { key: 'user5', label: 'User 5', range: 'Sentences 4,001–5,000', docs: 879, count: 1000 },
  { key: 'user6', label: 'User 6', range: 'Sentences 5,001–6,000', docs: 866, count: 1000 },
  { key: 'user7', label: 'User 7', range: 'Sentences 6,001–7,000', docs: 889, count: 1000 }
];

export default function Dashboard({
  user,
  workspace,
  activeUserLabel,
  activeRangeLabel,
  onSelectWorkspace,
  onStartAnnotation,
  onNavigateExport
}) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStats();
  }, [workspace]);

  const loadStats = async () => {
    setLoading(true);
    setError('');
    try {
      const queryWs = (workspace === 'all') ? null : workspace;
      const data = await datasetApi.getStats(queryWs);
      setStats(data);
    } catch (err) {
      setError('Could not load statistics. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const displayName = activeUserLabel || user?.display_name || user?.username || 'Expert';
  const displayRange = stats?.assigned_range || activeRangeLabel || 'doc_id 1–1,000';

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading {displayName} dataset statistics...</p>
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
            Welcome, {displayName}!
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginTop: '0.2rem' }}>
            Current Workspace: <strong style={{ color: '#1e293b' }}>{displayName}</strong> • Assigned Range: <strong style={{ color: '#1e293b' }}>{displayRange}</strong>
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
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>
            {displayName} Verification Progress
          </h3>
          <span style={{ fontSize: '0.9rem', color: '#64748b', fontWeight: 500 }}>
            Assigned Range: <strong>{displayRange}</strong>
          </span>
        </div>
        <ProgressBar
          completed={stats?.verified_sentences || 0}
          total={stats?.total_sentences || 1000}
          percentage={stats?.completion_percentage || 0}
        />
      </div>

      {/* Stats Cards Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
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
          <div style={{ color: '#6366f1', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase' }}>
            Assigned Documents
          </div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: '#312e81', marginTop: '0.25rem' }}>
            {stats?.total_documents ?? 0}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem' }}>
            Unique news articles
          </div>
        </div>

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
            {stats?.total_tokens || 0} tokens in range
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

      {/* 7 Expert Workspace Switcher Overview */}
      <div style={{
        background: 'white',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-md)',
        padding: '1.25rem',
        marginBottom: '2rem',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#1e293b' }}>
            👥 7 Expert Workspaces (Click to Switch Range)
          </h4>
          <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
            Assigned by sentence position (1,000 sentences each) • Simultaneous expert verification
          </span>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
          gap: '0.75rem'
        }}>
          {EXPERT_WORKSPACES.map((w) => (
            <div
              key={w.key}
              onClick={() => onSelectWorkspace(w.key)}
              style={{
                padding: '0.75rem',
                borderRadius: '6px',
                border: workspace === w.key ? '2px solid var(--primary-color)' : '1px solid #e2e8f0',
                background: workspace === w.key ? '#eff6ff' : '#f8fafc',
                cursor: 'pointer',
                textAlign: 'center',
                transition: 'all 0.15s ease'
              }}
            >
              <div style={{ fontWeight: 700, fontSize: '0.9rem', color: '#1e3a8a' }}>
                {w.label}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.2rem' }}>
                {w.range}
              </div>
              <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#047857', marginTop: '0.25rem' }}>
                {w.docs} docs • {w.count.toLocaleString()} sents
              </div>
            </div>
          ))}
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
          <li>You are assigned a dedicated 1,000-sentence workspace (e.g. User 1: 1–1,000, User 2: 1,001–2,000).</li>
          <li>Examine the Sanskrit sentence and each individual token in Devanagari script.</li>
          <li>Assign the appropriate <strong>Sanskrit Consortium POS tag</strong> (e.g., <code>N, KP, A, AVN</code>) from the dropdown.</li>
          <li>Click <strong>Save Draft</strong> if you want to pause your work without marking the sentence verified.</li>
          <li>Click <strong>Save & Next</strong> to finalize all tags, validate completeness, save changes into the database, and move directly to your next pending sentence.</li>
        </ul>
      </div>
    </div>
  );
}

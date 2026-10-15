import React, { useState, useEffect } from 'react';
import { datasetApi, annotationApi } from '../api';
import TokenRow from './TokenRow';
import TokenCard from './TokenCard';
import ConfirmDialog from './ConfirmDialog';
import { validateSentenceForVerification } from '../utils/validation';

export default function AnnotationPage({ user, workspace, onSelectWorkspace, onBackToDashboard }) {
  const [sentence, setSentence] = useState(null);
  const [tokens, setTokens] = useState([]);
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState(null); // { type: 'success' | 'error', text: '' }
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [showExitConfirm, setShowExitConfirm] = useState(false);
  const [accessDenied, setAccessDenied] = useState(null);
  const [completedAll, setCompletedAll] = useState(false);
  const [completionMessage, setCompletionMessage] = useState('');

  // Determine user's own workspace key
  const getUserWorkspaceKey = () => {
    const uname = (user?.username || '').toLowerCase().replace(/[\s_]/g, '');
    for (let i = 1; i <= 7; i++) {
      if (uname === `user${i}`) return `user${i}`;
    }
    if (uname === 'sanskritscholar') return 'user1';
    return 'user1';
  };
  const myWorkspaceKey = getUserWorkspaceKey();
  const myWorkspaceLabel = `User ${myWorkspaceKey.replace('user', '')}`;

  useEffect(() => {
    loadNextSentence(workspace);
  }, [workspace]);

  const loadNextSentence = async (targetWs = workspace) => {
    setLoading(true);
    setFeedback(null);
    setAccessDenied(null);
    setCompletedAll(false);
    try {
      const queryWs = (targetWs === 'all') ? null : targetWs;
      const data = await datasetApi.getNextSentence(queryWs);
      if (!data) {
        setSentence(null);
        setCompletedAll(true);
        setCompletionMessage('All pending sentences in this workspace have been verified.');
        return;
      }
      setSentence(data);
      setTokens(data.tokens || []);
      setNote(data.annotation_note || '');
      setHasUnsavedChanges(false);
    } catch (err) {
      if (err.response?.status === 403) {
        setAccessDenied(err.response?.data?.detail || 'Access denied: You do not have permission to view or annotate this workspace.');
        setSentence(null);
      } else if (err.response?.status === 404) {
        setSentence(null);
        setCompletedAll(true);
        setCompletionMessage(err.response?.data?.detail || 'All 1,000 sentences assigned to this workspace have been verified!');
      } else {
        setFeedback({
          type: 'error',
          text: 'Error fetching next sentence: ' + (err.response?.data?.detail || err.message || 'Unknown error')
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTagChange = (tokenIndex, newTag) => {
    const updated = [...tokens];
    updated[tokenIndex] = {
      ...updated[tokenIndex],
      gold_sanskrit_tag: newTag
    };
    setTokens(updated);
    setHasUnsavedChanges(true);
  };

  const handleNoteChange = (e) => {
    setNote(e.target.value);
    setHasUnsavedChanges(true);
  };

  const handleSaveDraft = async () => {
    if (!sentence) return;
    setSaving(true);
    setFeedback(null);
    try {
      await annotationApi.saveDraft(sentence.annotation_id, {
        tokens,
        note
      });
      setHasUnsavedChanges(false);
      setSentence(prev => ({ ...prev, status: 'in_progress', annotation_note: note }));
      setFeedback({ type: 'success', text: 'Draft saved successfully. Sentence marked as In Progress.' });
    } catch (err) {
      setFeedback({ type: 'error', text: 'Failed to save draft: ' + (err.response?.data?.detail || err.message) });
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAndNext = async () => {
    if (!sentence) return;

    // Validate that every token has an assigned Sanskrit Consortium tag
    const validation = validateSentenceForVerification(tokens);
    if (!validation.isValid) {
      setFeedback({
        type: 'error',
        text: `Cannot verify sentence: ${validation.errors.join(' ')} Please assign all tags before clicking Save & Next.`
      });
      return;
    }

    setSaving(true);
    setFeedback(null);
    try {
      await annotationApi.verifySentence(sentence.annotation_id, {
        tokens,
        note
      });
      setHasUnsavedChanges(false);
      setFeedback({ type: 'success', text: `Sentence ${sentence.annotation_id} verified and saved!` });

      // Immediate transition to next sentence for fast and smooth navigation
      await loadNextSentence(workspace);
    } catch (err) {
      setFeedback({ type: 'error', text: 'Failed to verify sentence: ' + (err.response?.data?.detail || err.message) });
    } finally {
      setSaving(false);
    }
  };

  const handleRequestDashboard = () => {
    if (hasUnsavedChanges) {
      setShowExitConfirm(true);
    } else {
      onBackToDashboard();
    }
  };

  // Compute unassigned count
  const unassignedCount = tokens.filter(t => !t.gold_sanskrit_tag || t.gold_sanskrit_tag.trim() === '').length;

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem' }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>Loading Sanskrit sentence...</p>
      </div>
    );
  }

  // Access Denied (expert selected another expert's workspace)
  if (accessDenied) {
    return (
      <div style={{
        background: '#fef2f2',
        border: '1.5px solid #f87171',
        borderRadius: 'var(--radius-md)',
        padding: '2.5rem 2rem',
        margin: '2rem auto',
        maxWidth: '700px',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🔒</div>
        <h3 style={{ color: '#991b1b', fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.75rem' }}>
          Workspace Access Restricted
        </h3>
        <p style={{ color: '#7f1d1d', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '1.5rem' }}>
          {accessDenied}
        </p>
        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button
            className="btn btn-primary"
            onClick={() => onSelectWorkspace(myWorkspaceKey)}
            style={{ padding: '0.65rem 1.4rem' }}
          >
            ← Switch to My Workspace ({myWorkspaceLabel})
          </button>
          <button
            className="btn btn-secondary"
            onClick={onBackToDashboard}
            style={{ padding: '0.65rem 1.4rem' }}
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  // All sentences verified in this workspace
  if (completedAll || !sentence) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 2rem', background: 'white', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', maxWidth: '700px', margin: '2rem auto' }}>
        <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>🎉</div>
        <h3 style={{ fontSize: '1.5rem', color: '#15803d', marginBottom: '0.75rem', fontWeight: 700 }}>
          Congratulations!
        </h3>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', fontSize: '1.05rem', lineHeight: 1.6 }}>
          {completionMessage || 'All 1,000 sentences assigned to this workspace have been verified.'}
        </p>
        <button className="btn btn-primary" onClick={onBackToDashboard} style={{ padding: '0.65rem 1.5rem' }}>
          Return to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* Navigation & Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <button className="btn btn-secondary" onClick={handleRequestDashboard}>
          ← Back to Dashboard
        </button>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          {hasUnsavedChanges && (
            <span style={{ fontSize: '0.85rem', color: '#b45309', background: '#fef3c7', padding: '0.2rem 0.6rem', borderRadius: '4px', fontWeight: 500 }}>
              ● Unsaved changes
            </span>
          )}
          <span className={`badge badge-${sentence.status || 'pending'}`}>
            {sentence.status || 'pending'}
          </span>
        </div>
      </div>

      {/* Feedback Messages */}
      {feedback && (
        <div className={`alert alert-${feedback.type}`}>
          {feedback.text}
        </div>
      )}

      {/* Main Annotation Panel */}
      <div className="annotation-panel">
        {/* Panel Header */}
        <div className="panel-header">
          <div className="meta-info">
            <span className="meta-item">Document: <strong>{sentence.doc_id}</strong></span>
            <span className="meta-item">Sentence #{sentence.sentence_id}</span>
            <span className="meta-item">Global Position: <strong>#{sentence.sentence_position || sentence.id}</strong> / 7,000</span>
            <span className="meta-item">Annotation ID: <strong>{sentence.annotation_id}</strong></span>
          </div>

          <div style={{ fontSize: '0.875rem' }}>
            {unassignedCount === 0 ? (
              <span style={{ color: '#15803d', fontWeight: 600 }}>✓ All {tokens.length} tokens assigned</span>
            ) : (
              <span style={{ color: '#b45309', fontWeight: 600 }}>⚠️ {unassignedCount} of {tokens.length} tokens unassigned</span>
            )}
          </div>
        </div>

        {/* Original Sentence in Devanagari */}
        <div className="sentence-display-box">
          <div className="sentence-label">Original Sanskrit Sentence (मूलवाक्यम्):</div>
          <div className="sanskrit-sentence sanskrit-text">
            {sentence.sentence_text}
          </div>
        </div>

        {/* Tokens Desktop View */}
        <div className="tokens-container">
          <div className="token-table-wrapper">
            <table className="token-table">
              <thead>
                <tr>
                  <th style={{ width: '40px' }}>#</th>
                  <th>Token (पदम्)</th>
                  <th>Lemma (मूलरूपम्)</th>
                  <th>Stanza UPOS (अनुमानितम्)</th>
                  <th>Morphological Feats</th>
                  <th>Expert Sanskrit POS Tag</th>
                </tr>
              </thead>
              <tbody>
                {tokens.map((token, idx) => (
                  <TokenRow
                    key={token.token_id || idx}
                    token={token}
                    index={idx}
                    onTagChange={handleTagChange}
                  />
                ))}
              </tbody>
            </table>
          </div>

          {/* Tokens Mobile / Tablet Card View */}
          <div className="token-cards-list">
            {tokens.map((token, idx) => (
              <TokenCard
                key={token.token_id || idx}
                token={token}
                index={idx}
                onTagChange={handleTagChange}
              />
            ))}
          </div>
        </div>

        {/* Optional Sentence-Level Annotation Note */}
        <div className="note-container">
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
            Annotation Note / Scholar Remarks (optional):
          </label>
          <textarea
            className="note-textarea"
            value={note}
            onChange={handleNoteChange}
            placeholder="Add any linguistic observations, samasa ambiguity, or sandhi notes here..."
          />
        </div>

        {/* Action Bar */}
        <div className="action-bar">
          <div style={{ fontSize: '0.85rem', color: '#64748b' }}>
            Expert: <strong>{user?.display_name || user?.username || 'Current Scholar'}</strong>
          </div>

          <div className="action-buttons-group">
            <button
              className="btn btn-secondary"
              onClick={handleSaveDraft}
              disabled={saving}
            >
              {saving ? 'Saving...' : '💾 Save Draft'}
            </button>

            <button
              className="btn btn-success"
              onClick={handleSaveAndNext}
              disabled={saving}
            >
              {saving ? 'Verifying...' : '✓ Save & Next'}
            </button>
          </div>
        </div>
      </div>

      {/* Confirmation Dialog on Unsaved Navigation */}
      <ConfirmDialog
        isOpen={showExitConfirm}
        title="Discard Unsaved Changes?"
        message="You have unsaved tag modifications in this sentence. If you leave now without saving, your changes will be lost."
        onConfirm={() => {
          setShowExitConfirm(false);
          setHasUnsavedChanges(false);
          onBackToDashboard();
        }}
        onCancel={() => setShowExitConfirm(false)}
      />
    </div>
  );
}

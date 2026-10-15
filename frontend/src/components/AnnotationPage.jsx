import React, { useState, useEffect } from 'react';
import { datasetApi, annotationApi } from '../api';
import TokenRow from './TokenRow';
import TokenCard from './TokenCard';
import ConfirmDialog from './ConfirmDialog';
import { validateSentenceForVerification } from '../utils/validation';

export default function AnnotationPage({
  user,
  workspace,
  activeUserLabel,
  activeRangeLabel,
  onSelectWorkspace,
  onBackToDashboard
}) {
  const [sentence, setSentence] = useState(null);
  const [tokens, setTokens] = useState([]);
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState(null); // { type: 'success' | 'error', text: '' }
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [showExitConfirm, setShowExitConfirm] = useState(false);
  const [completedAll, setCompletedAll] = useState(false);
  const [completionMessage, setCompletionMessage] = useState('');

  const [nextSentenceError, setNextSentenceError] = useState(null);

  const displayName = activeUserLabel || user?.display_name || user?.username || 'Current Scholar';
  const displayRange = activeRangeLabel || '1,000 sentences';

  useEffect(() => {
    // Immediately clear current sentence so stale data is never shown
    setSentence(null);
    setTokens([]);
    setNote('');
    setNextSentenceError(null);
    loadNextSentence(workspace);
  }, [workspace]);

  const loadNextSentence = async (targetWs = workspace, isAfterSave = false, savedInfo = null) => {
    setLoading(true);
    if (!isAfterSave) {
      setFeedback(null);
    }
    setNextSentenceError(null);
    setCompletedAll(false);
    try {
      const queryWs = (targetWs === 'all') ? null : targetWs;
      const data = await datasetApi.getNextSentence(queryWs);
      if (!data) {
        setSentence(null);
        setTokens([]);
        setCompletedAll(true);
        setCompletionMessage(`All 1,000 sentences assigned to ${displayName} (${displayRange}) have been verified!`);
        return;
      }
      setSentence(data);
      setTokens(data.tokens || []);
      setNote(data.annotation_note || '');
      setHasUnsavedChanges(false);
      if (isAfterSave && savedInfo) {
        setFeedback({
          type: 'success',
          text: `✓ Sentence #${savedInfo.pos} (${savedInfo.annId}) verified & saved! Loaded next pending sentence #${data.sentence_position || data.id}.`
        });
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setSentence(null);
        setTokens([]);
        setCompletedAll(true);
        setCompletionMessage(err.response?.data?.detail || `All 1,000 sentences assigned to ${displayName} (${displayRange}) have been verified!`);
      } else {
        const errorDetail = err.response?.data?.detail || err.message || 'Unknown network error';
        if (isAfterSave) {
          // Keep save intact! Inform user that save succeeded, and provide retry button
          setNextSentenceError(`Saved successfully! Failed to fetch next sentence: ${errorDetail}`);
        } else {
          setSentence(null);
          setTokens([]);
          setFeedback({
            type: 'error',
            text: 'Error fetching next sentence: ' + errorDetail
          });
        }
      }
    } finally {
      setLoading(false);
      setSaving(false);
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
    setNextSentenceError(null);
    try {
      await annotationApi.saveDraft(sentence.annotation_id, {
        tokens,
        note
      }, workspace);
      setHasUnsavedChanges(false);
      setSentence(prev => ({ ...prev, status: 'in_progress', annotation_note: note }));
      setFeedback({
        type: 'success',
        text: `Draft saved to database for sentence #${sentence.sentence_position || sentence.sentence_id}. Status: In Progress.`
      });
    } catch (err) {
      setFeedback({
        type: 'error',
        text: 'Failed to save draft to database: ' + (err.response?.data?.detail || err.message)
      });
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAndNext = async () => {
    if (!sentence) return;

    // 1. Client-side Completeness Validation
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
    setNextSentenceError(null);

    const savedPos = sentence.sentence_position || sentence.sentence_id;
    const savedAnnId = sentence.annotation_id;

    // 2. Commit verification to database
    try {
      await annotationApi.verifySentence(savedAnnId, {
        tokens,
        note
      }, workspace);

      setHasUnsavedChanges(false);
      setFeedback({
        type: 'success',
        text: `✓ Sentence #${savedPos} (${savedAnnId}) successfully verified and committed to database!`
      });
    } catch (err) {
      // Step 5 failure handling: Keep current selections, show clear message, do not advance
      const status = err.response?.status;
      let errorDetail = err.response?.data?.detail || err.message || 'Unknown error';
      if (status === 401) {
        errorDetail = 'Session expired. Please log in again to save verification.';
      } else if (status === 403) {
        errorDetail = `Authorization error: ${errorDetail}`;
      } else if (status === 422 || status === 400) {
        errorDetail = `Validation error: ${errorDetail}`;
      } else {
        errorDetail = `Database save error: ${errorDetail}`;
      }
      setFeedback({
        type: 'error',
        text: `Save & Next failed for sentence #${savedPos}: ${errorDetail}`
      });
      setSaving(false);
      return;
    }

    // 3. Save succeeded! Now fetch the next sentence in this expert's workspace
    await loadNextSentence(workspace, true, { pos: savedPos, annId: savedAnnId });
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
        <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem' }}>
          Loading Sanskrit sentence for {displayName} ({displayRange})...
        </p>
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
          {completionMessage || `All 1,000 sentences assigned to ${displayName} have been verified.`}
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
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--primary-color)', background: '#eff6ff', padding: '0.2rem 0.6rem', borderRadius: '4px', border: '1px solid #bfdbfe' }}>
            {displayName} • Range: {displayRange}
          </span>
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

      {/* Next sentence fetch error banner with Retry button */}
      {nextSentenceError && (
        <div className="alert alert-warning" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1rem', background: '#fffbeb', border: '1px solid #fde68a', color: '#92400e', borderRadius: 'var(--radius-md)', padding: '0.75rem 1rem' }}>
          <div>
            <strong>✓ Annotation saved successfully!</strong> {nextSentenceError}
          </div>
          <button
            className="btn btn-primary"
            style={{ padding: '0.4rem 1rem', fontSize: '0.875rem' }}
            onClick={() => loadNextSentence(workspace)}
          >
            ↻ Retry Loading Next Sentence
          </button>
        </div>
      )}

      {/* Main Annotation Panel */}
      <div className="annotation-panel">
        {/* Panel Header */}
        <div className="panel-header">
          <div className="meta-info">
            <span className="meta-item">Workspace: <strong>{displayName}</strong></span>
            <span className="meta-item">Global Position: <strong>#{sentence.sentence_position || sentence.id}</strong> / 7,000</span>
            <span className="meta-item">Document: <strong>{sentence.doc_id}</strong></span>
            <span className="meta-item">Sentence #{sentence.sentence_id}</span>
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
            Active Expert: <strong>{displayName}</strong> ({displayRange})
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
              {saving ? 'Verifying & Saving...' : '✓ Save & Next'}
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

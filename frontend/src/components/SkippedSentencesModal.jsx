import React from 'react';

export default function SkippedSentencesModal({
  isOpen,
  onClose,
  skippedList = [],
  onResume,
  displayName,
  displayRange,
  loadingResume = false
}) {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(15, 23, 42, 0.65)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1100,
      padding: '1.5rem',
      backdropFilter: 'blur(2px)'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: 'var(--radius-md)',
        maxWidth: '850px',
        width: '100%',
        maxHeight: '85vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: 'var(--shadow-lg)',
        overflow: 'hidden'
      }}>
        {/* Modal Header */}
        <div style={{
          padding: '1.25rem 1.5rem',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#fffbeb'
        }}>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#92400e', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>⏭</span> Skipped Sentences Queue ({skippedList.length})
            </h3>
            <p style={{ margin: '0.25rem 0 0', fontSize: '0.85rem', color: '#78350f' }}>
              Workspace: <strong>{displayName}</strong> • Range: <strong>{displayRange}</strong>
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: '1.5rem',
              color: '#92400e',
              cursor: 'pointer',
              lineHeight: 1,
              padding: '0.25rem 0.5rem',
              borderRadius: 'var(--radius-sm)'
            }}
            title="Close modal"
          >
            ✕
          </button>
        </div>

        {/* Modal Body */}
        <div style={{
          padding: '1.5rem',
          overflowY: 'auto',
          flex: 1
        }}>
          {skippedList.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>✨</div>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>
                No Skipped Sentences
              </h4>
              <p style={{ fontSize: '0.9rem' }}>
                You have not skipped any sentences in your workspace. When you click "Skip Sentence" on difficult items, they will appear here.
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <p style={{ fontSize: '0.875rem', color: '#64748b', margin: 0 }}>
                These sentences were temporarily set aside. Select any sentence to resume verification at any time:
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {skippedList.map((item) => {
                  const pos = item.sentence_position || item.id;
                  const tokenCount = item.tokens ? item.tokens.length : (item.token_count || 0);
                  const formattedTime = item.skipped_at ? new Date(item.skipped_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' }) : null;

                  return (
                    <div
                      key={item.annotation_id || item.id}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '1rem 1.25rem',
                        backgroundColor: '#fafaf9',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid #e7e5e4',
                        gap: '1rem',
                        flexWrap: 'wrap'
                      }}
                    >
                      <div style={{ flex: '1 1 350px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem', flexWrap: 'wrap' }}>
                          <span style={{
                            backgroundColor: '#ffedd5',
                            color: '#c2410c',
                            fontWeight: 700,
                            fontSize: '0.8rem',
                            padding: '0.2rem 0.5rem',
                            borderRadius: '4px',
                            border: '1px solid #fed7aa'
                          }}>
                            Sentence #{pos}
                          </span>
                          <span style={{ fontSize: '0.8rem', color: '#78716c' }}>
                            Doc: <strong>{item.doc_id}</strong>
                          </span>
                          <span style={{ fontSize: '0.8rem', color: '#78716c' }}>
                            • {tokenCount} tokens
                          </span>
                          {formattedTime && (
                            <span style={{ fontSize: '0.75rem', color: '#a8a29e' }}>
                              • Skipped: {formattedTime}
                            </span>
                          )}
                        </div>

                        <div className="sanskrit-text" style={{ fontSize: '1.05rem', color: '#1c1917', lineHeight: 1.5 }}>
                          {item.sentence_text}
                        </div>

                        {item.annotation_note && (
                          <div style={{ fontSize: '0.8rem', color: '#78716c', marginTop: '0.35rem', fontStyle: 'italic' }}>
                            Note: {item.annotation_note}
                          </div>
                        )}
                      </div>

                      <div>
                        <button
                          className="btn btn-primary"
                          onClick={() => onResume(item)}
                          disabled={loadingResume}
                          style={{
                            padding: '0.5rem 1.1rem',
                            fontSize: '0.875rem',
                            whiteSpace: 'nowrap',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.35rem'
                          }}
                        >
                          ▶ Resume
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div style={{
          padding: '1rem 1.5rem',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'flex-end',
          backgroundColor: '#f8fafc'
        }}>
          <button className="btn btn-secondary" onClick={onClose} style={{ padding: '0.5rem 1.25rem' }}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

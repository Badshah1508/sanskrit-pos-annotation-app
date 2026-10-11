import React from 'react';
import TagDropdown from './TagDropdown';

export default function TokenCard({ token, index, onTagChange }) {
  return (
    <div className="token-card">
      <div className="token-card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600 }}>
            #{token.token_id}
          </span>
          <span className="token-devanagari sanskrit-text" style={{ fontSize: '1.4rem' }}>
            {token.token}
          </span>
        </div>
        <span className="stanza-badge" title="Stanza automatic prediction">
          Stanza: {token.stanza_upos || token.upos || '—'}
        </span>
      </div>

      <div className="token-card-body">
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>Lemma (मूलरूपम्):</span>
          <strong className="sanskrit-text">{token.lemma || '—'}</strong>
        </div>

        {token.feats && token.feats !== '_' && (
          <div style={{ fontSize: '0.75rem', color: '#64748b', background: '#f8fafc', padding: '0.4rem', borderRadius: '4px' }}>
            {token.feats}
          </div>
        )}

        <div style={{ marginTop: '0.5rem' }}>
          <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.3rem', color: 'var(--text-muted)' }}>
            Expert POS Tag:
          </label>
          <TagDropdown
            value={token.gold_sanskrit_tag}
            onChange={(newTag) => onTagChange(index, newTag)}
          />
        </div>
      </div>
    </div>
  );
}

import React from 'react';
import TagDropdown from './TagDropdown';

export default function TokenRow({ token, index, onTagChange }) {
  return (
    <tr key={token.token_id || index}>
      <td style={{ color: 'var(--text-muted)', fontWeight: 500 }}>
        {token.token_id}
      </td>
      <td>
        <span className="token-devanagari sanskrit-text">{token.token}</span>
      </td>
      <td style={{ color: 'var(--text-muted)' }}>
        <span className="sanskrit-text">{token.lemma || '—'}</span>
      </td>
      <td>
        <span className="stanza-badge" title="Stanza automatic prediction">
          {token.stanza_upos || token.upos || '—'}
        </span>
      </td>
      <td style={{ fontSize: '0.8rem', color: '#64748b', maxWidth: '200px', wordBreak: 'break-word' }}>
        {token.feats && token.feats !== '_' ? token.feats : '—'}
      </td>
      <td style={{ minWidth: '180px' }}>
        <TagDropdown
          value={token.gold_sanskrit_tag}
          onChange={(newTag) => onTagChange(index, newTag)}
        />
      </td>
    </tr>
  );
}

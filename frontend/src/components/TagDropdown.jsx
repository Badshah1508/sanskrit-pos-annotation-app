import React from 'react';
import { SANSKRIT_CONSORTIUM_TAGS } from '../config/tags';

export default function TagDropdown({ value, onChange, disabled = false, id }) {
  const isAssigned = Boolean(value && value.trim() !== '');

  return (
    <div className="tag-dropdown-wrapper">
      <select
        id={id}
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={`tag-select ${isAssigned ? 'assigned' : 'unassigned'}`}
        aria-label="Sanskrit Consortium POS Tag"
      >
        <option value="">-- Select Tag (अनिश्चितम्) --</option>
        {SANSKRIT_CONSORTIUM_TAGS.map((item) => (
          <option key={item.tag} value={item.tag}>
            {item.tag} — {item.name}
          </option>
        ))}
      </select>
    </div>
  );
}

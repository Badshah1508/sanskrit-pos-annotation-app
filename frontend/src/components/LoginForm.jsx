import React, { useState } from 'react';
import { authApi, getMockMode, setMockMode } from '../api';

const QUICK_ACCOUNTS = [
  { username: 'user1', label: 'User 1 (1–1k)', pw: 'password123' },
  { username: 'user2', label: 'User 2 (1k–2k)', pw: 'password123' },
  { username: 'user3', label: 'User 3 (2k–3k)', pw: 'password123' },
  { username: 'user4', label: 'User 4 (3k–4k)', pw: 'password123' },
  { username: 'user5', label: 'User 5 (4k–5k)', pw: 'password123' },
  { username: 'user6', label: 'User 6 (5k–6k)', pw: 'password123' },
  { username: 'user7', label: 'User 7 (6k–7k)', pw: 'password123' },
  { username: 'admin', label: 'Admin (All)', pw: 'admin123' }
];

export default function LoginForm({ onLoginSuccess }) {
  const [username, setUsername] = useState('user1');
  const [password, setPassword] = useState('password123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isMock, setIsMock] = useState(getMockMode());

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setError('');

    if (!username.trim() || !password.trim()) {
      setError('Please provide both username and password.');
      return;
    }

    setLoading(true);
    try {
      const data = await authApi.login(username, password);
      onLoginSuccess(data.user);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickSelect = (acc) => {
    setUsername(acc.username);
    setPassword(acc.pw);
    setError('');
  };

  const toggleMock = (e) => {
    const val = e.target.checked;
    setIsMock(val);
    setMockMode(val);
  };

  return (
    <div style={{ maxWidth: '440px', width: '100%', margin: '0 auto' }}>
      <form onSubmit={handleSubmit} style={{
        background: 'white',
        padding: '2.2rem',
        borderRadius: 'var(--radius-md)',
        boxShadow: 'var(--shadow-md)',
        border: '1px solid var(--border-color)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--primary-color)' }}>
            Expert Login
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            Sanskrit POS Annotation & Verification Portal
          </p>
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {/* Quick select buttons */}
        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#475569', marginBottom: '0.4rem' }}>
            Select Expert Workspace to Sign In:
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.35rem' }}>
            {QUICK_ACCOUNTS.map((acc) => (
              <button
                key={acc.username}
                type="button"
                onClick={() => handleQuickSelect(acc)}
                style={{
                  padding: '0.35rem 0.2rem',
                  fontSize: '0.75rem',
                  fontWeight: username === acc.username ? 700 : 500,
                  borderRadius: '4px',
                  border: username === acc.username ? '1.5px solid var(--primary-color)' : '1px solid #cbd5e1',
                  background: username === acc.username ? '#eff6ff' : '#f8fafc',
                  color: username === acc.username ? 'var(--primary-color)' : '#334155',
                  cursor: 'pointer',
                  textAlign: 'center'
                }}
              >
                {acc.username}
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: '1.2rem' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.4rem' }}>
            Username or Email
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="e.g. user1, user2, user3..."
            style={{
              width: '100%',
              padding: '0.65rem 0.85rem',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid #cbd5e1',
              fontSize: '0.95rem'
            }}
            disabled={loading}
          />
        </div>

        <div style={{ marginBottom: '1.4rem' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.4rem' }}>
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            style={{
              width: '100%',
              padding: '0.65rem 0.85rem',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid #cbd5e1',
              fontSize: '0.95rem'
            }}
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: '100%', padding: '0.75rem', fontSize: '1rem', fontWeight: 600 }}
          disabled={loading}
        >
          {loading ? 'Authenticating...' : `Sign In as ${username}`}
        </button>

        <div style={{
          marginTop: '1.25rem',
          padding: '0.75rem 0.85rem',
          backgroundColor: '#f8fafc',
          border: '1px solid #e2e8f0',
          borderRadius: 'var(--radius-sm)',
          fontSize: '0.8rem',
          color: '#475569',
          lineHeight: 1.5
        }}>
          <div><strong>7 Dedicated Workspaces:</strong> <code>user1</code>–<code>user7</code> (pw: <code>password123</code>)</div>
          <div style={{ marginTop: '0.2rem' }}><strong>Admin:</strong> <code>admin</code> (pw: <code>admin123</code>)</div>
        </div>

        <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)', fontSize: '0.85rem', color: '#64748b' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={isMock}
              onChange={toggleMock}
            />
            <span>Enable Local Mock Mode (Frontend Testing)</span>
          </label>
          <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            Uncheck once FastAPI backend is running on port 8000.
          </p>
        </div>
      </form>
    </div>
  );
}

import React, { useState } from 'react';
import { authApi, getMockMode, setMockMode } from '../api';

export default function LoginForm({ onLoginSuccess }) {
  const [username, setUsername] = useState('sanskrit_scholar');
  const [password, setPassword] = useState('password123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isMock, setIsMock] = useState(getMockMode());

  const handleSubmit = async (e) => {
    e.preventDefault();
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

  const toggleMock = (e) => {
    const val = e.target.checked;
    setIsMock(val);
    setMockMode(val);
  };

  return (
    <div style={{ maxWidth: '420px', width: '100%', margin: '0 auto' }}>
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

        <div style={{ marginBottom: '1.2rem' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.4rem' }}>
            Username or Email
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="e.g. vidwan_expert"
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
          {loading ? 'Authenticating...' : 'Sign In'}
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
          <div><strong>Expert Accounts:</strong> <code>user1</code> to <code>user7</code> (password: <code>password123</code>)</div>
          <div style={{ marginTop: '0.2rem' }}><strong>Administrator:</strong> <code>admin</code> (password: <code>admin123</code>)</div>
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

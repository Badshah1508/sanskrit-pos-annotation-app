import React from 'react';
import LoginForm from '../components/LoginForm';

export default function LoginPage({ onLoginSuccess }) {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'linear-gradient(135deg, #f0f4f8 0%, #d9e2ec 100%)',
      padding: '1.5rem'
    }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: '#102a43', letterSpacing: '-0.02em' }}>
          संस्कृतपदविभागपरियोजना
        </h1>
        <p style={{ fontSize: '1.1rem', color: '#486581', marginTop: '0.5rem' }}>
          Cross-Domain Sanskrit POS Tagging & Expert Verification Portal
        </p>
      </div>

      <LoginForm onLoginSuccess={onLoginSuccess} />

      <div style={{ marginTop: '2.5rem', textAlign: 'center', fontSize: '0.85rem', color: '#627d98' }}>
        M.Tech Data Science Dissertation • 70% Stanza-Assisted Annotation Queue
      </div>
    </div>
  );
}

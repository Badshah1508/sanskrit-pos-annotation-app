import React, { useState, useEffect } from 'react';
import LoginPage from './pages/LoginPage';
import Dashboard from './components/Dashboard';
import AnnotationPage from './components/AnnotationPage';
import ExportPanel from './components/ExportPanel';
import { authApi } from './api';
import './styles/global.css';
import './styles/annotation.css';

export default function App() {
  const [user, setUser] = useState(null);
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard' | 'annotate' | 'export'
  const [loadingUser, setLoadingUser] = useState(true);

  useEffect(() => {
    // Check if user session already exists
    const checkAuth = async () => {
      try {
        const currentUser = await authApi.getCurrentUser();
        if (currentUser) {
          setUser(currentUser);
        }
      } catch (err) {
        console.error('Session check failed', err);
      } finally {
        setLoadingUser(false);
      }
    };
    checkAuth();
  }, []);

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    authApi.logout();
    setUser(null);
    setCurrentView('dashboard');
  };

  if (loadingUser) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: 'var(--text-muted)' }}>
        Loading application...
      </div>
    );
  }

  // Show login page if unauthenticated
  if (!user) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="app-container">
      {/* Top Navigation Bar */}
      <nav className="navbar">
        <div
          className="navbar-brand"
          style={{ cursor: 'pointer' }}
          onClick={() => setCurrentView('dashboard')}
        >
          <span>संस्कृत</span>
          <span style={{ fontWeight: 400, color: 'var(--text-muted)' }}>POS Annotation</span>
        </div>

        <div className="nav-links">
          <button
            className={`btn ${currentView === 'dashboard' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setCurrentView('dashboard')}
            style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
          >
            Dashboard
          </button>

          <button
            className={`btn ${currentView === 'annotate' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setCurrentView('annotate')}
            style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
          >
            Annotate
          </button>

          {user.role === 'admin' && (
            <button
              className={`btn ${currentView === 'export' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setCurrentView('export')}
              style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
            >
              Export
            </button>
          )}

          <div className="user-badge">
            <span>👤 <strong>{user.username}</strong></span>
            <span style={{ fontSize: '0.75rem', background: '#e2e8f0', padding: '0.1rem 0.4rem', borderRadius: '4px' }}>
              {user.role}
            </span>
          </div>

          <button
            className="btn btn-secondary"
            onClick={handleLogout}
            style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem', color: 'var(--danger-color)' }}
          >
            Sign Out
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="main-content">
        {currentView === 'dashboard' && (
          <Dashboard
            user={user}
            onStartAnnotation={() => setCurrentView('annotate')}
            onNavigateExport={() => setCurrentView('export')}
          />
        )}

        {currentView === 'annotate' && (
          <AnnotationPage
            user={user}
            onBackToDashboard={() => setCurrentView('dashboard')}
          />
        )}

        {currentView === 'export' && (
          <ExportPanel
            onBack={() => setCurrentView('dashboard')}
          />
        )}
      </main>
    </div>
  );
}

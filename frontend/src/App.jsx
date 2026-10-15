import React, { useState, useEffect } from 'react';
import LoginPage from './pages/LoginPage';
import Dashboard from './components/Dashboard';
import AnnotationPage from './components/AnnotationPage';
import ExportPanel from './components/ExportPanel';
import { authApi } from './api';
import './styles/global.css';
import './styles/annotation.css';

const WORKSPACE_MAP = {
  user1: { label: 'User 1', range: '1–1,000', start: 1, end: 1000 },
  user2: { label: 'User 2', range: '1,001–2,000', start: 1001, end: 2000 },
  user3: { label: 'User 3', range: '2,001–3,000', start: 2001, end: 3000 },
  user4: { label: 'User 4', range: '3,001–4,000', start: 3001, end: 4000 },
  user5: { label: 'User 5', range: '4,001–5,000', start: 4001, end: 5000 },
  user6: { label: 'User 6', range: '5,001–6,000', start: 5001, end: 6000 },
  user7: { label: 'User 7', range: '6,001–7,000', start: 6001, end: 7000 },
  all:   { label: 'All Users', range: '1–7,000', start: 1, end: 7000 }
};

// Helper to determine initial workspace key from user account
const resolveInitialWorkspace = (userData) => {
  if (!userData) return 'user1';
  const uname = (userData.username || '').toLowerCase().replace(/[\s_]/g, '');
  for (let i = 1; i <= 7; i++) {
    if (uname === `user${i}`) return `user${i}`;
  }
  if (uname === 'sanskritscholar') return 'user1';
  if (userData.role === 'admin') {
    return localStorage.getItem('last_admin_workspace') || 'user1';
  }
  return 'user1';
};

export default function App() {
  const [user, setUser] = useState(null);
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard' | 'annotate' | 'export'
  const [selectedWorkspace, setSelectedWorkspace] = useState('user1');
  const [loadingUser, setLoadingUser] = useState(true);
  const [isWakingServer, setIsWakingServer] = useState(false);

  useEffect(() => {
    // Show polite server wake-up notice if initial auth takes > 1.5s
    const wakeTimer = setTimeout(() => {
      setIsWakingServer(true);
    }, 1500);

    const checkAuth = async () => {
      try {
        const currentUser = await authApi.getCurrentUser();
        if (currentUser) {
          setUser(currentUser);
          const initWs = resolveInitialWorkspace(currentUser);
          setSelectedWorkspace(initWs);
        }
      } catch (err) {
        console.error('Session check failed', err);
      } finally {
        clearTimeout(wakeTimer);
        setLoadingUser(false);
      }
    };
    checkAuth();
  }, []);

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    const initWs = resolveInitialWorkspace(userData);
    setSelectedWorkspace(initWs);
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    authApi.logout();
    setUser(null);
    setCurrentView('dashboard');
  };

  const handleWorkspaceChange = (e) => {
    const ws = e.target.value;
    setSelectedWorkspace(ws);
    if (user?.role === 'admin') {
      localStorage.setItem('last_admin_workspace', ws);
    }
  };

  // Compute active user label and range for the selected workspace
  const activeWsInfo = WORKSPACE_MAP[selectedWorkspace] || WORKSPACE_MAP.user1;
  const activeUserLabel = user?.role === 'admin' && selectedWorkspace === 'all'
    ? 'All Users (Admin)'
    : activeWsInfo.label;
  const activeRangeLabel = activeWsInfo.range;

  if (loadingUser) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        gap: '1rem',
        padding: '2rem',
        textAlign: 'center'
      }}>
        <div style={{
          width: '38px',
          height: '38px',
          border: '3px solid #cbd5e1',
          borderTopColor: 'var(--primary-color)',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
        <div style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--primary-color)' }}>
          Loading Sanskrit POS Annotation Portal...
        </div>
        {isWakingServer && (
          <div style={{ maxWidth: '380px', fontSize: '0.85rem', color: '#64748b', lineHeight: 1.5 }}>
            Connecting to cloud service... On first load after inactivity, free cloud services take a few moments to spin up.
          </div>
        )}
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
          {/* User Dropdown */}
          <div className="workspace-selector-container">
            <label htmlFor="user-workspace-select" className="workspace-label">
              User
            </label>
            <select
              id="user-workspace-select"
              className="workspace-select"
              value={selectedWorkspace}
              onChange={handleWorkspaceChange}
            >
              <option value="user1">User 1</option>
              <option value="user2">User 2</option>
              <option value="user3">User 3</option>
              <option value="user4">User 4</option>
              <option value="user5">User 5</option>
              <option value="user6">User 6</option>
              <option value="user7">User 7</option>
              {user.role === 'admin' && (
                <option value="all">All Users (Admin Overview)</option>
              )}
            </select>
          </div>

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
            <span>👤 <strong>{activeUserLabel}</strong></span>
            <span style={{ fontSize: '0.75rem', background: '#e2e8f0', padding: '0.1rem 0.4rem', borderRadius: '4px' }}>
              {activeRangeLabel}
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
            workspace={selectedWorkspace}
            activeUserLabel={activeUserLabel}
            activeRangeLabel={activeRangeLabel}
            onSelectWorkspace={setSelectedWorkspace}
            onStartAnnotation={() => setCurrentView('annotate')}
            onNavigateExport={() => setCurrentView('export')}
          />
        )}

        {currentView === 'annotate' && (
          <AnnotationPage
            user={user}
            workspace={selectedWorkspace}
            activeUserLabel={activeUserLabel}
            activeRangeLabel={activeRangeLabel}
            onSelectWorkspace={setSelectedWorkspace}
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

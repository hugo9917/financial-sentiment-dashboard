import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import Login from './Login';
import './Navbar.css';

const Navbar = ({ apiStatus }) => {
  const location = useLocation();
  const [showLogin, setShowLogin] = useState(false);
  const [user, setUser] = useState(null);
  const [showUserMenu, setShowUserMenu] = useState(false);

  useEffect(() => {
    // Verificar si hay un usuario logueado
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleLogin = (loginData) => {
    setUser(loginData.user);
    setShowLogin(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setShowUserMenu(false);
  };

  const getStatusColor = () => {
    switch (apiStatus) {
      case 'healthy':
        return '#10B981'; // green
      case 'unhealthy':
        return '#EF4444'; // red
      case 'checking':
        return '#F59E0B'; // yellow
      default:
        return '#6B7280'; // gray
    }
  };

  const getStatusText = () => {
    switch (apiStatus) {
      case 'healthy':
        return 'API Online';
      case 'unhealthy':
        return 'API Offline';
      case 'checking':
        return 'Checking...';
      default:
        return 'API Error';
    }
  };

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/sentiment', label: 'Sentimiento', icon: '😊' },
    { path: '/stocks', label: 'Precios', icon: '📈' },
    { path: '/correlation', label: 'Correlación', icon: '🔗' },
    { path: '/news', label: 'Noticias', icon: '📰' },
  ];

  return (
    <>
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>📊 Financial Sentiment</h1>
          <div className="api-status">
            <div 
              className="status-indicator" 
              style={{ backgroundColor: getStatusColor() }}
            ></div>
            <span className="status-text">{getStatusText()}</span>
          </div>
        </div>
        
        <ul className="nav-links">
          {navItems.map((item) => (
            <li key={item.path}>
              <Link 
                to={item.path} 
                className={location.pathname === item.path ? 'active' : ''}
              >
                <span className="nav-icon">{item.icon}</span>
                {item.label}
              </Link>
            </li>
          ))}
        </ul>

        <div className="navbar-auth">
          {user ? (
            <div className="user-menu">
              <button 
                className="user-button"
                onClick={() => setShowUserMenu(!showUserMenu)}
              >
                <span className="user-avatar">👤</span>
                <span className="user-name">{user.full_name}</span>
                <span className="user-role">({user.role})</span>
              </button>
              
              {showUserMenu && (
                <div className="user-dropdown">
                  <div className="user-info">
                    <strong>{user.full_name}</strong>
                    <span>{user.email}</span>
                    <span className="user-role-badge">{user.role}</span>
                  </div>
                  <button className="logout-button" onClick={handleLogout}>
                    Cerrar Sesión
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button 
              className="login-button"
              onClick={() => setShowLogin(true)}
              data-testid="navbar-login-button"
            >
              Iniciar Sesión
            </button>
          )}
        </div>
      </nav>

      {showLogin && (
        <Login 
          onLogin={handleLogin}
          onClose={() => setShowLogin(false)}
        />
      )}
    </>
  );
};

export default Navbar; 
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

const Navbar = ({ apiStatus }) => {
  const location = useLocation();

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
    </nav>
  );
};

export default Navbar; 
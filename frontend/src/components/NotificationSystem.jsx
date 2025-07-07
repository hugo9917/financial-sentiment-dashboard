import React, { useState, createContext, useContext } from 'react';
import './NotificationSystem.css';

// Contexto para las notificaciones
const NotificationContext = createContext();

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);

  const addNotification = (notification) => {
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      ...notification,
      timestamp: new Date(),
    };
    
    setNotifications(prev => [newNotification, ...prev]);
    
    // Auto-remove after duration
    if (notification.duration !== 0) {
      setTimeout(() => {
        removeNotification(id);
      }, notification.duration || 5000);
    }
    
    return id;
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  const value = {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <NotificationContainer />
    </NotificationContext.Provider>
  );
};

const NotificationContainer = () => {
  const { notifications, removeNotification, clearAll } = useNotifications();

  if (notifications.length === 0) return null;

  return (
    <div className="notification-container">
      <div className="notification-header">
        <span>Notifications ({notifications.length})</span>
        <button onClick={clearAll} className="clear-all-btn">
          Clear All
        </button>
      </div>
      <div className="notification-list">
        {notifications.map(notification => (
          <NotificationItem
            key={notification.id}
            notification={notification}
            onRemove={removeNotification}
          />
        ))}
      </div>
    </div>
  );
};

const NotificationItem = ({ notification, onRemove }) => {
  const getIcon = (type) => {
    switch (type) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      default: return '📢';
    }
  };

  const getTypeClass = (type) => {
    switch (type) {
      case 'success': return 'notification-success';
      case 'error': return 'notification-error';
      case 'warning': return 'notification-warning';
      case 'info': return 'notification-info';
      default: return 'notification-default';
    }
  };

  return (
    <div className={`notification-item ${getTypeClass(notification.type)}`}>
      <div className="notification-icon">
        {getIcon(notification.type)}
      </div>
      <div className="notification-content">
        <div className="notification-title">
          {notification.title}
        </div>
        {notification.message && (
          <div className="notification-message">
            {notification.message}
          </div>
        )}
        <div className="notification-time">
          {notification.timestamp.toLocaleTimeString()}
        </div>
      </div>
      <button
        className="notification-close"
        onClick={() => onRemove(notification.id)}
        aria-label="Close notification"
      >
        ×
      </button>
    </div>
  );
};

// Hook helper para crear notificaciones rápidas
export const useQuickNotifications = () => {
  const { addNotification } = useNotifications();

  const success = (title, message = '') => {
    addNotification({
      type: 'success',
      title,
      message,
      duration: 4000,
    });
  };

  const error = (title, message = '') => {
    addNotification({
      type: 'error',
      title,
      message,
      duration: 6000,
    });
  };

  const warning = (title, message = '') => {
    addNotification({
      type: 'warning',
      title,
      message,
      duration: 5000,
    });
  };

  const info = (title, message = '') => {
    addNotification({
      type: 'info',
      title,
      message,
      duration: 4000,
    });
  };

  return { success, error, warning, info };
};

// Definición mínima si no existe
function NotificationSystem() {
  return null;
}
export default NotificationSystem; 
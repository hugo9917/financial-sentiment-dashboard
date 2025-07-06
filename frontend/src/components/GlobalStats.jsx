import React, { useState, useEffect } from 'react';
import './GlobalStats.css';

const GlobalStats = () => {
  const [stats, setStats] = useState({
    totalRecords: 0,
    overallSentiment: 0,
    avgStockPrice: 0,
    latestDataTime: null,
    sentimentDistribution: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/dashboard/stats`);
      const data = await response.json();
      setStats(data);
    } catch (err) {
      setError('Error loading statistics');
      console.error('Stats error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment) => {
    if (sentiment > 0.1) return '#10B981';
    if (sentiment < -0.1) return '#EF4444';
    return '#6B7280';
  };

  const getSentimentIcon = (sentiment) => {
    if (sentiment > 0.1) return '📈';
    if (sentiment < -0.1) return '📉';
    return '➡️';
  };

  const getSentimentLabel = (sentiment) => {
    if (sentiment > 0.1) return 'Positive';
    if (sentiment < -0.1) return 'Negative';
    return 'Neutral';
  };

  if (loading) {
    return (
      <div className="global-stats">
        <div className="stats-loading">
          <div className="loading-spinner"></div>
          <p>Loading statistics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="global-stats">
        <div className="stats-error">
          <p>{error}</p>
          <button onClick={fetchStats}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="global-stats">
      <div className="stats-header">
        <h3>Global Statistics</h3>
        <button 
          className="refresh-button"
          onClick={fetchStats}
          title="Refresh statistics"
        >
          🔄
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h4>Total Records</h4>
            <p className="stat-value">{stats.totalRecords.toLocaleString()}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">😊</div>
          <div className="stat-content">
            <h4>Overall Sentiment</h4>
            <p 
              className="stat-value"
              style={{ color: getSentimentColor(stats.overallSentiment) }}
            >
              {getSentimentIcon(stats.overallSentiment)} {stats.overallSentiment.toFixed(3)}
            </p>
            <small>{getSentimentLabel(stats.overallSentiment)}</small>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <h4>Average Stock Price</h4>
            <p className="stat-value">${stats.avgStockPrice.toFixed(2)}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🕒</div>
          <div className="stat-content">
            <h4>Latest Data</h4>
            <p className="stat-value">
              {stats.latestDataTime 
                ? new Date(stats.latestDataTime).toLocaleString()
                : 'N/A'
              }
            </p>
          </div>
        </div>
      </div>

      {stats.sentimentDistribution && stats.sentimentDistribution.length > 0 && (
        <div className="sentiment-distribution">
          <h4>Sentiment Distribution</h4>
          <div className="distribution-bars">
            {stats.sentimentDistribution.map((item, index) => {
              const total = stats.sentimentDistribution.reduce((sum, i) => sum + i.count, 0);
              const percentage = total > 0 ? (item.count / total) * 100 : 0;
              
              return (
                <div key={index} className="distribution-item">
                  <div className="distribution-label">
                    <span className="sentiment-color" style={{ 
                      backgroundColor: getSentimentColor(item.sentiment_category === 'Positive' ? 0.5 : item.sentiment_category === 'Negative' ? -0.5 : 0)
                    }}></span>
                    {item.sentiment_category}
                  </div>
                  <div className="distribution-bar">
                    <div 
                      className="distribution-fill"
                      style={{ 
                        width: `${percentage}%`,
                        backgroundColor: getSentimentColor(item.sentiment_category === 'Positive' ? 0.5 : item.sentiment_category === 'Negative' ? -0.5 : 0)
                      }}
                    ></div>
                  </div>
                  <div className="distribution-count">
                    {item.count} ({percentage.toFixed(1)}%)
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default GlobalStats; 
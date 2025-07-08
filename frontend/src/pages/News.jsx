import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import './News.css';

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const News = () => {
  const [news, setNews] = useState([]);
  const [filteredNews, setFilteredNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSource, setSelectedSource] = useState('all');
  const [selectedSentiment, setSelectedSentiment] = useState('all');
  const [limit, setLimit] = useState(20);

  useEffect(() => {
    fetchNews();
  }, [limit]);

  useEffect(() => {
    filterNews();
  }, [news, searchTerm, selectedSource, selectedSentiment]);

  const fetchNews = async () => {
    try {
      setLoading(true);
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/news/latest?limit=${limit}`);
      const data = await response.json();
      setNews(data.news || []);
    } catch (err) {
      setError('Error al cargar las noticias');
      console.error('News error:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterNews = () => {
    let filtered = news;

    // Filtrar por término de búsqueda
    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filtrar por fuente
    if (selectedSource !== 'all') {
      filtered = filtered.filter(item => item.source_name === selectedSource);
    }

    // Filtrar por sentimiento
    if (selectedSentiment !== 'all') {
      filtered = filtered.filter(item => {
        const score = item.sentiment_score || 0;
        switch (selectedSentiment) {
          case 'positive':
            return score > 0.1;
          case 'negative':
            return score < -0.1;
          case 'neutral':
            return score >= -0.1 && score <= 0.1;
          default:
            return true;
        }
      });
    }

    setFilteredNews(filtered);
  };

  const getSentimentColor = (score) => {
    if (score > 0.1) return 'text-green-600';
    if (score < -0.1) return 'text-red-600';
    return 'text-gray-600';
  };

  const getSentimentLabel = (score) => {
    if (score > 0.1) return 'Positivo';
    if (score < -0.1) return 'Negativo';
    return 'Neutral';
  };

  const getSentimentIcon = (score) => {
    if (score > 0.1) return '📈';
    if (score < -0.1) return '📉';
    return '➡️';
  };

  // Preparar datos para el gráfico de sentimiento
  const sentimentChartData = {
    labels: filteredNews.slice(0, 10).map(item => 
      new Date(item.published_at).toLocaleDateString('es-ES', { 
        month: 'short', 
        day: 'numeric' 
      })
    ).reverse(),
    datasets: [
      {
        label: 'Sentimiento',
        data: filteredNews.slice(0, 10).map(item => item.sentiment_score || 0).reverse(),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      }
    ]
  };

  const sources = [...new Set(news.map(item => item.source_name).filter(Boolean))];
  const sentimentOptions = [
    { value: 'all', label: 'Todos' },
    { value: 'positive', label: 'Positivo' },
    { value: 'negative', label: 'Negativo' },
    { value: 'neutral', label: 'Neutral' }
  ];

  if (loading) {
    return (
      <div className="news-loading">
        <div className="loading-spinner"></div>
        <p>Cargando noticias...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="news-error">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={fetchNews}>Reintentar</button>
      </div>
    );
  }

  return (
    <div className="news-page">
      <div className="news-header">
        <h1 data-testid="news-title">Noticias Financieras</h1>
        <p>Análisis de sentimiento de las últimas noticias del mercado</p>
      </div>

      {/* Filtros */}
      <div className="news-filters">
        <div className="filter-group">
          <label htmlFor="search">Buscar:</label>
          <input
            type="text"
            id="search"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Buscar en títulos y descripciones..."
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <label htmlFor="source">Fuente:</label>
          <select
            id="source"
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
            className="filter-select"
          >
            <option value="all">Todas las fuentes</option>
            {sources.map(source => (
              <option key={source} value={source}>{source}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="sentiment">Sentimiento:</label>
          <select
            id="sentiment"
            value={selectedSentiment}
            onChange={(e) => setSelectedSentiment(e.target.value)}
            className="filter-select"
          >
            {sentimentOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="limit">Mostrar:</label>
          <select
            id="limit"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="filter-select"
          >
            <option value={10}>10 noticias</option>
            <option value={20}>20 noticias</option>
            <option value={50}>50 noticias</option>
            <option value={100}>100 noticias</option>
          </select>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="news-stats">
        <div className="stat-card">
          <h3>Total de Noticias</h3>
          <p className="stat-value" data-testid="news-total">{filteredNews.length}</p>
        </div>
        <div className="stat-card">
          <h3>Sentimiento Promedio</h3>
          <p className="stat-value" data-testid="news-avg-sentiment">
            {filteredNews.length > 0 
              ? (filteredNews.reduce((sum, item) => sum + (item.sentiment_score || 0), 0) / filteredNews.length).toFixed(3)
              : '0.000'
            }
          </p>
        </div>
        <div className="stat-card">
          <h3>Fuentes Únicas</h3>
          <p className="stat-value" data-testid="news-unique-sources">{sources.length}</p>
        </div>
      </div>

      {/* Gráfico de Sentimiento */}
      <div className="chart-section">
        <h3>Evolución del Sentimiento</h3>
        <div className="chart-container">
          {filteredNews.length > 0 ? (
            <Line 
              data={sentimentChartData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  title: {
                    display: true,
                    text: 'Últimas 10 noticias',
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    min: -1,
                    max: 1,
                  },
                },
              }}
            />
          ) : (
            <p>No hay datos para mostrar</p>
          )}
        </div>
      </div>

      {/* Lista de Noticias */}
      <div className="news-list">
        <h3>Noticias ({filteredNews.length})</h3>
        {filteredNews.length === 0 ? (
          <div className="no-results">
            <p>No se encontraron noticias con los filtros seleccionados.</p>
          </div>
        ) : (
          <div className="news-grid">
            {filteredNews.map((item, index) => (
              <div key={index} className="news-card">
                <div className="news-header">
                  <h4 className="news-title">
                    <a href={item.url} target="_blank" rel="noopener noreferrer">
                      {item.title}
                    </a>
                  </h4>
                  <div className="news-meta">
                    <span className="news-source">{item.source_name}</span>
                    <span className="news-date">
                      {new Date(item.published_at).toLocaleString('es-ES')}
                    </span>
                  </div>
                </div>
                
                <p className="news-description">{item.description}</p>
                
                <div className="news-sentiment">
                  <span className={`sentiment-score ${getSentimentColor(item.sentiment_score)}`}>
                    {getSentimentIcon(item.sentiment_score)} {getSentimentLabel(item.sentiment_score)}
                  </span>
                  <span className="sentiment-value">
                    Score: {item.sentiment_score?.toFixed(3) || '0.000'}
                  </span>
                  <span className="subjectivity">
                    Subjetividad: {item.sentiment_subjectivity?.toFixed(3) || '0.000'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default News; 
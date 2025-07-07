import React, { useState, useEffect } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import GlobalStats from '../components/GlobalStats';
import './Dashboard.css';

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [timeline, setTimeline] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState(24); // Filtro de tiempo en horas

  useEffect(() => {
    fetchDashboardData();
  }, [timeRange]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      // Obtener estadísticas generales
      const statsResponse = await fetch(`${apiUrl}/api/dashboard/stats?hours=${timeRange * 30}`); // Convertir a días
      const statsData = await statsResponse.json();
      setStats(statsData);

      // Obtener línea de tiempo
      const timelineResponse = await fetch(`${apiUrl}/api/sentiment/timeline?hours=${timeRange}`);
      const timelineData = await timelineResponse.json();
      setTimeline(timelineData);

    } catch (err) {
      setError('Error al cargar datos del dashboard');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTimeRangeChange = (newRange) => {
    setTimeRange(newRange);
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Cargando dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={fetchDashboardData}>Reintentar</button>
      </div>
    );
  }

  // Preparar datos para gráficos
  const sentimentTimelineData = timeline?.timeline ? {
    labels: timeline.timeline.slice(0, 12).map(item => 
      new Date(item.time_period).toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    ).reverse(),
    datasets: [
      {
        label: 'Sentimiento',
        data: timeline.timeline.slice(0, 12).map(item => item.sentiment_score).reverse(),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Precio Normalizado',
        data: timeline.timeline.slice(0, 12).map(item => 
          item.avg_price ? (item.avg_price / 100) : 0
        ).reverse(),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
      }
    ]
  } : null;

  const sentimentDistributionData = stats?.sentiment_distribution ? {
    labels: stats.sentiment_distribution.map(item => item.sentiment_category),
    datasets: [{
      data: stats.sentiment_distribution.map(item => item.count),
      backgroundColor: [
        'rgba(34, 197, 94, 0.8)',  // Verde para positivo
        'rgba(239, 68, 68, 0.8)',  // Rojo para negativo
        'rgba(156, 163, 175, 0.8)', // Gris para neutral
      ],
      borderWidth: 2,
      borderColor: '#ffffff',
    }]
  } : null;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard Financiero</h1>
        <p>Análisis de sentimiento y correlación con precios de acciones</p>
        
        {/* Filtros de tiempo */}
        <div className="time-filters">
          <span>Rango de tiempo:</span>
          <button 
            className={timeRange === 24 ? 'active' : ''} 
            onClick={() => handleTimeRangeChange(24)}
          >
            24h
          </button>
          <button 
            className={timeRange === 168 ? 'active' : ''} 
            onClick={() => handleTimeRangeChange(168)}
          >
            7d
          </button>
          <button 
            className={timeRange === 720 ? 'active' : ''} 
            onClick={() => handleTimeRangeChange(720)}
          >
            30d
          </button>
        </div>
      </div>

      {/* Estadísticas principales */}
      {stats?.general_stats && (
        <div className="stats-overview">
          <div className="stat-card">
            <h3>Total de Registros</h3>
            <p className="stat-value">{stats.general_stats.total_records?.toLocaleString()}</p>
          </div>
          <div className="stat-card">
            <h3>Sentimiento General</h3>
            <p className={`stat-value ${stats.general_stats.overall_sentiment > 0 ? 'positive' : 'negative'}`}>
              {stats.general_stats.overall_sentiment?.toFixed(3)}
            </p>
          </div>
          <div className="stat-card">
            <h3>Precio Promedio</h3>
            <p className="stat-value">${stats.general_stats.avg_stock_price?.toFixed(2)}</p>
          </div>
          <div className="stat-card">
            <h3>Última Actualización</h3>
            <p className="stat-value">
              {stats.general_stats.latest_data_time 
                ? new Date(stats.general_stats.latest_data_time).toLocaleString('es-ES')
                : 'N/A'
              }
            </p>
          </div>
        </div>
      )}

      {/* Componente de estadísticas globales */}
      <GlobalStats />

      {/* Gráficos */}
      <div className="charts-grid">
        <div className="chart-card">
          <h3>Línea de Tiempo: Sentimiento vs Precios</h3>
          {sentimentTimelineData ? (
            <Line 
              data={sentimentTimelineData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  title: {
                    display: true,
                    text: `Últimas ${timeRange} horas`,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                  },
                },
              }}
            />
          ) : (
            <p>No hay datos disponibles</p>
          )}
        </div>

        <div className="chart-card">
          <h3>Distribución de Sentimiento</h3>
          {sentimentDistributionData ? (
            <Doughnut 
              data={sentimentDistributionData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'bottom',
                  },
                },
              }}
            />
          ) : (
            <p>No hay datos disponibles</p>
          )}
        </div>
      </div>

      {/* Información adicional */}
      <div className="info-section">
        <h3>Información del Sistema</h3>
        <div className="info-grid">
          <div className="info-item">
            <strong>Estado de la API:</strong> 
            <span className={stats ? 'status-ok' : 'status-error'}>
              {stats ? 'Conectado' : 'Desconectado'}
            </span>
          </div>
          <div className="info-item">
            <strong>Base de Datos:</strong> 
            <span className={stats ? 'status-ok' : 'status-error'}>
              {stats ? 'PostgreSQL' : 'N/A'}
            </span>
          </div>
          <div className="info-item">
            <strong>Registros Procesados:</strong> 
            <span>{stats?.general_stats?.total_records || 0}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 
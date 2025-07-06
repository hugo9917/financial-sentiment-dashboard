import React, { useEffect, useState } from 'react';
import { Scatter, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  CategoryScale,
  Tooltip,
  Legend,
  Title
} from 'chart.js';
import { useQuickNotifications } from '../components/NotificationSystem';

ChartJS.register(LinearScale, PointElement, LineElement, CategoryScale, Tooltip, Legend, Title);

const TIME_OPTIONS = [
  { label: 'Últimas 24h', value: 24 },
  { label: 'Últimos 7 días', value: 168 },
  { label: 'Últimos 30 días', value: 720 },
];

const categoryColors = {
  Positive: 'rgba(0, 200, 83, 0.8)',
  Neutral: 'rgba(128, 128, 128, 0.8)',
  Negative: 'rgba(255, 82, 82, 0.8)',
};

function Correlation() {
  const [data, setData] = useState([]);
  const [timelineData, setTimelineData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [hours, setHours] = useState(720);
  const [viewMode, setViewMode] = useState('scatter'); // 'scatter' or 'timeline'
  const { error: showError, info: showInfo } = useQuickNotifications();

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetch(`${import.meta.env.VITE_API_URL}/api/correlation/analysis?hours=${hours}`),
      fetch(`${import.meta.env.VITE_API_URL}/api/sentiment/timeline?hours=${hours}`)
    ])
      .then(responses => Promise.all(responses.map(res => res.json())))
      .then(([correlationData, timelineData]) => {
        setData(correlationData.correlation_analysis || []);
        setTimelineData(timelineData.timeline || []);
        setLoading(false);
        showInfo('Data loaded', `Loaded correlation data for last ${hours} hours`);
      })
      .catch(err => {
        console.error('Error loading correlation data:', err);
        showError('Data loading failed', 'Could not load correlation data');
        setLoading(false);
      });
  }, [hours, showError, showInfo]);

  // Prepara los datos para el scatter plot
  const scatterData = {
    datasets: [
      {
        label: 'Correlación Sentimiento vs Cambio de Precio',
        data: data.map(row => ({
          x: row.avg_sentiment_change,
          y: row.avg_price_change,
          category: row.sentiment_category
        })),
        backgroundColor: data.map(row => categoryColors[row.sentiment_category] || 'rgba(54, 162, 235, 0.7)'),
        pointRadius: 10,
        pointHoverRadius: 14,
      }
    ]
  };

  const scatterOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: true, text: 'Dispersión: Cambio de Sentimiento vs Cambio de Precio' },
      tooltip: {
        callbacks: {
          label: ctx => {
            const d = ctx.raw;
            return [
              `Categoría: ${d.category}`,
              `Δ Sentimiento: ${d.x?.toFixed(3)}`,
              `Δ Precio: ${d.y?.toFixed(3)}`
            ];
          }
        }
      }
    },
    scales: {
      x: {
        title: { display: true, text: 'Cambio Promedio de Sentimiento' },
        min: -1, max: 1
      },
      y: {
        title: { display: true, text: 'Cambio Promedio de Precio (%)' },
        min: -1, max: 1
      }
    }
  };

  // Preparar datos para el gráfico de línea temporal
  const timelineChartData = timelineData.length > 0 ? {
    labels: timelineData.slice(0, 24).map(item => 
      new Date(item.time_period).toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    ).reverse(),
    datasets: [
      {
        label: 'Sentimiento',
        data: timelineData.slice(0, 24).map(item => item.sentiment_score).reverse(),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Precio Normalizado',
        data: timelineData.slice(0, 24).map(item => 
          item.avg_price ? (item.avg_price / 100) : 0
        ).reverse(),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
      }
    ]
  } : null;

  return (
    <div>
      <h2>Correlación</h2>
      
      <div style={{marginBottom: '1rem', display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap'}}>
        <div>
          <label>Rango de tiempo: </label>
          <select value={hours} onChange={e => setHours(Number(e.target.value))}>
            {TIME_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label>Vista: </label>
          <select value={viewMode} onChange={e => setViewMode(e.target.value)}>
            <option value="scatter">Dispersión</option>
            <option value="timeline">Línea Temporal</option>
          </select>
        </div>
      </div>
      {loading && <p>Cargando...</p>}
      {!loading && data.length > 0 ? (
        <>
          {viewMode === 'scatter' ? (
            <div style={{ maxWidth: 800, margin: '2rem auto' }}>
              <Scatter data={scatterData} options={scatterOptions} />
            </div>
          ) : (
            <div style={{ maxWidth: 800, margin: '2rem auto' }}>
              {timelineChartData ? (
                <Line 
                  data={timelineChartData}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: {
                        position: 'top',
                      },
                      title: {
                        display: true,
                        text: 'Correlación Temporal: Sentimiento vs Precios',
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
                <p>No hay datos de línea temporal disponibles</p>
              )}
            </div>
          )}
          
          <div style={{ maxWidth: 800, margin: '2rem auto' }}>
            <table style={{width: '100%', borderCollapse: 'collapse', background: 'rgba(0,0,0,0.1)', color: '#fff'}}>
              <thead>
                <tr>
                  <th>Categoría</th>
                  <th>Δ Precio (%)</th>
                  <th>Δ Sentimiento</th>
                  <th>Puntos</th>
                  <th>Correlación</th>
                </tr>
              </thead>
              <tbody>
                {data.map((row, idx) => (
                  <tr key={row.sentiment_category + '-' + idx} style={{background: categoryColors[row.sentiment_category] || 'rgba(54,162,235,0.2)'}}>
                    <td><b>{row.sentiment_category}</b></td>
                    <td>{row.avg_price_change?.toFixed(3)}</td>
                    <td>{row.avg_sentiment_change?.toFixed(3)}</td>
                    <td>{row.data_points}</td>
                    <td>{row.correlation_coefficient?.toFixed(3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : !loading && <p>No hay datos de correlación para mostrar.</p>}
    </div>
  );
}

export default Correlation; 
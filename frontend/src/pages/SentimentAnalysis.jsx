import React, { useEffect, useState } from 'react';
import { Bar, Line, Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend);

const TIME_OPTIONS = [
  { label: 'Últimas 24h', value: 24 },
  { label: 'Últimos 7 días', value: 168 },
  { label: 'Últimos 30 días', value: 720 },
];

function exportToCSV(rows) {
  if (!rows.length) return;
  const header = Object.keys(rows[0]);
  const csv = [header.join(',')].concat(
    rows.map(row => header.map(field => JSON.stringify(row[field] ?? '')).join(','))
  ).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'sentiment_analysis.csv';
  a.click();
  window.URL.revokeObjectURL(url);
}

function SentimentAnalysis() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hours, setHours] = useState(24);
  // Paginación
  const [page, setPage] = useState(1);
  const rowsPerPage = 10;
  // Filtros avanzados
  const [search, setSearch] = useState('');
  const [minSent, setMinSent] = useState(-1);
  const [maxSent, setMaxSent] = useState(1);
  // Selector de símbolo
  const symbols = Array.from(new Set(data.map(row => row.symbol)));
  const [selectedSymbol, setSelectedSymbol] = useState('');

  useEffect(() => {
    setLoading(true);
    fetch(`${import.meta.env.VITE_API_URL}/api/sentiment/summary_by_symbol?hours=${hours}`)
      .then(res => res.json())
      .then(res => {
        setData(res.summary || []);
        setLoading(false);
        setPage(1); // Resetear página al cambiar filtro
      })
      .catch(err => {
        setError('Error al cargar los datos');
        setLoading(false);
      });
  }, [hours]);

  // Aplicar filtros avanzados
  const filtered = data.filter(row => {
    const symbolMatch = (row.symbol ?? '').toLowerCase().includes(search.toLowerCase());
    const sent = row.avg_sentiment ?? 0;
    return symbolMatch && sent >= minSent && sent <= maxSent;
  });

  // Para gráficos avanzados: datos del símbolo seleccionado
  const symbolData = selectedSymbol ? filtered.filter(row => row.symbol === selectedSymbol) : [];

  // Datos para el gráfico de barras
  const chartData = {
    labels: filtered.map(row => row.symbol),
    datasets: [
      {
        label: 'Sentimiento Promedio',
        data: filtered.map(row => row.avg_sentiment),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: true, text: 'Sentimiento Promedio por Símbolo' },
    },
    scales: {
      y: {
        min: -1,
        max: 1,
        title: { display: true, text: 'Sentimiento' },
      },
    },
  };

  // Gráfico combinado: sentimiento y cantidad de noticias
  const combinedData = {
    labels: symbolData.map(row => row.symbol),
    datasets: [
      {
        label: 'Sentimiento Promedio',
        data: symbolData.map(row => row.avg_sentiment),
        borderColor: 'rgba(255,99,132,1)',
        backgroundColor: 'rgba(255,99,132,0.2)',
        tension: 0.2,
        yAxisID: 'y',
        type: 'line',
      },
      {
        label: 'Cantidad de Noticias',
        data: symbolData.map(row => row.news_count),
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        yAxisID: 'y1',
        type: 'bar',
      },
    ],
  };

  const combinedOptions = {
    responsive: true,
    plugins: {
      legend: { display: true },
      title: { display: true, text: `Sentimiento y Noticias (${selectedSymbol})` },
      tooltip: { mode: 'index', intersect: false },
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        min: -1,
        max: 1,
        title: { display: true, text: 'Sentimiento Promedio' },
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: { display: true, text: 'Cantidad de Noticias' },
        grid: { drawOnChartArea: false },
      },
    },
  };

  // Gráfico de dispersión: sentimiento vs cantidad de noticias
  const scatterData = {
    datasets: [
      {
        label: 'Sentimiento vs Noticias',
        data: symbolData.map(row => ({ x: row.avg_sentiment, y: row.news_count })),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
      },
    ],
  };

  const scatterOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: true, text: `Correlación Sentimiento vs Noticias (${selectedSymbol})` },
      tooltip: { mode: 'nearest', intersect: false },
    },
    scales: {
      x: {
        title: { display: true, text: 'Sentimiento Promedio' },
        min: -1,
        max: 1,
      },
      y: {
        title: { display: true, text: 'Cantidad de Noticias' },
      },
    },
  };

  // Paginación
  const totalPages = Math.ceil(filtered.length / rowsPerPage);
  const paginatedData = filtered.slice((page - 1) * rowsPerPage, page * rowsPerPage);

  return (
    <div>
      <h2>Análisis de Sentimiento</h2>
      <div style={{marginBottom: '1rem', display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center'}}>
        <label>Rango de tiempo: </label>
        <select value={hours} onChange={e => setHours(Number(e.target.value))}>
          {TIME_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <label>Búsqueda símbolo: </label>
        <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="AAPL, MSFT..." />
        <label>Sentimiento promedio:</label>
        <input type="number" step="0.01" min="-1" max="1" value={minSent} onChange={e => setMinSent(Number(e.target.value))} style={{width: 60}} />
        <span>-</span>
        <input type="number" step="0.01" min="-1" max="1" value={maxSent} onChange={e => setMaxSent(Number(e.target.value))} style={{width: 60}} />
        <label>Selecciona símbolo: </label>
        <select value={selectedSymbol} onChange={e => setSelectedSymbol(e.target.value)}>
          <option value=''>-- Selecciona --</option>
          {symbols.filter(sym => (sym ?? '').toLowerCase().includes(search.toLowerCase())).map(sym => (
            <option key={sym} value={sym}>{sym}</option>
          ))}
        </select>
        <button style={{marginLeft: '1rem'}} onClick={() => exportToCSV(paginatedData)}>
          Exportar CSV
        </button>
      </div>
      {loading && <p>Cargando...</p>}
      {error && <p style={{color: 'red'}}>{error}</p>}
      {!loading && !error && filtered.length > 0 && (
        <>
          <div style={{maxWidth: 800, margin: '0 auto 2rem auto'}}>
            <Bar data={chartData} options={chartOptions} />
          </div>
          {selectedSymbol && symbolData.length > 0 && (
            <>
              <div style={{maxWidth: 800, margin: '0 auto 2rem auto'}}>
                <Line data={combinedData} options={combinedOptions} />
              </div>
              <div style={{maxWidth: 800, margin: '0 auto 2rem auto'}}>
                <Scatter data={scatterData} options={scatterOptions} />
              </div>
            </>
          )}
          <table style={{width: '100%', borderCollapse: 'collapse'}}>
            <thead>
              <tr>
                <th>Símbolo</th>
                <th>Sentimiento Promedio</th>
                <th>Subjetividad Promedio</th>
                <th>Cantidad de Noticias</th>
              </tr>
            </thead>
            <tbody>
              {paginatedData.map((row, idx) => (
                <tr key={row.symbol || idx}>
                  <td>{row.symbol}</td>
                  <td>{row.avg_sentiment?.toFixed(3)}</td>
                  <td>{row.avg_subjectivity?.toFixed(3)}</td>
                  <td>{row.news_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {/* Controles de paginación */}
          <div style={{marginTop: '1rem', textAlign: 'center'}}>
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Anterior</button>
            <span style={{margin: '0 1rem'}}>Página {page} de {totalPages}</span>
            <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Siguiente</button>
          </div>
        </>
      )}
      {!loading && !error && filtered.length === 0 && <p>No hay datos para los filtros seleccionados.</p>}
    </div>
  );
}

export default SentimentAnalysis; 
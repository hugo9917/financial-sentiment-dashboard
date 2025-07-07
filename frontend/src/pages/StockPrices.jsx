import React, { useEffect, useState } from 'react';
import { Line, Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

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
  a.download = 'stock_prices.csv';
  a.click();
  window.URL.revokeObjectURL(url);
}

function StockPrices() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [hours, setHours] = useState(24);
  // Paginación
  const [page, setPage] = useState(1);
  const rowsPerPage = 10;
  // Filtros avanzados
  const [search, setSearch] = useState('');
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(10000);

  useEffect(() => {
    setLoading(true);
    fetch(`${import.meta.env.VITE_API_URL}/api/stocks/prices_by_symbol?hours=${hours}`)
      .then(res => res.json())
      .then(res => {
        setData(res.stock_prices || []);
        setLoading(false);
        setPage(1); // Resetear página al cambiar filtro
      })
      .catch(() => {
        setError('Error al cargar los datos');
        setLoading(false);
      });
  }, [hours]);

  // Obtener lista de símbolos únicos
  const symbols = Array.from(new Set(data.map(row => row.symbol)));

  // Filtro por búsqueda de símbolo y rango de precio
  const filtered = data.filter(row => {
    const symbolMatch = row.symbol.toLowerCase().includes(search.toLowerCase());
    const price = row.close ?? 0;
    return symbolMatch && price >= minPrice && price <= maxPrice;
  });

  // Filtrar datos por símbolo seleccionado
  const symbolFiltered = selectedSymbol ? filtered.filter(row => row.symbol === selectedSymbol) : [];

  // Paginación
  const totalPages = Math.ceil(symbolFiltered.length / rowsPerPage);
  const paginatedData = symbolFiltered.slice((page - 1) * rowsPerPage, page * rowsPerPage);

  // Calcular resumen estadístico
  const precios = symbolFiltered.map(row => row.close).filter(v => v !== undefined && v !== null);
  const avgPrice = precios.length ? (precios.reduce((a, b) => a + b, 0) / precios.length).toFixed(2) : '-';
  const maxPriceStat = precios.length ? Math.max(...precios).toFixed(2) : '-';
  const minPriceStat = precios.length ? Math.min(...precios).toFixed(2) : '-';
  const lastPrice = precios.length ? precios[precios.length - 1].toFixed(2) : '-';

  // Datos para el gráfico de línea (precio de cierre)
  const chartData = {
    labels: symbolFiltered.map(row => row.hour),
    datasets: [
      {
        label: `Precio de Cierre (${selectedSymbol})`,
        data: symbolFiltered.map(row => row.close),
        borderColor: '#00fff7',
        backgroundColor: 'rgba(0,255,247,0.15)',
        borderWidth: 3,
        pointRadius: 5,
        pointHoverRadius: 8,
        tension: 0.3,
        yAxisID: 'y',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { display: true, labels: { color: '#fff' } },
      title: { display: true, text: `Evolución del Precio de Cierre (${selectedSymbol})`, color: '#fff' },
      tooltip: { enabled: true },
    },
    scales: {
      y: {
        title: { display: true, text: 'Precio de Cierre', color: '#fff' },
        ticks: { color: '#fff' },
      },
      x: {
        title: { display: true, text: 'Fecha/Hora', color: '#fff' },
        ticks: {
          color: '#fff',
          callback: function(value) {
            const label = this.getLabelForValue(value);
            return label.length > 10 ? label.slice(0, 10) : label;
          }
        }
      },
    },
  };

  // Gráfico combinado: precio de cierre y sentimiento promedio
  const combinedData = {
    labels: symbolFiltered.map(row => row.hour),
    datasets: [
      {
        label: 'Precio de Cierre',
        data: symbolFiltered.map(row => row.close),
        borderColor: 'rgba(75,192,192,1)',
        backgroundColor: 'rgba(75,192,192,0.2)',
        tension: 0.2,
        yAxisID: 'y',
      },
      {
        label: 'Sentimiento Promedio',
        data: symbolFiltered.map(row => row.avg_sentiment),
        borderColor: 'rgba(255,99,132,1)',
        backgroundColor: 'rgba(255,99,132,0.2)',
        tension: 0.2,
        yAxisID: 'y1',
      },
    ],
  };

  const combinedOptions = {
    responsive: true,
    plugins: {
      legend: { display: true },
      title: { display: true, text: `Precio de Cierre y Sentimiento (${selectedSymbol})` },
      tooltip: { mode: 'index', intersect: false },
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: { display: true, text: 'Precio de Cierre' },
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        min: -1,
        max: 1,
        title: { display: true, text: 'Sentimiento Promedio' },
        grid: { drawOnChartArea: false },
      },
      x: {
        title: { display: true, text: 'Fecha/Hora' },
      },
    },
  };

  // Gráfico de dispersión: sentimiento vs precio de cierre
  const scatterData = {
    datasets: [
      {
        label: 'Sentimiento vs Precio',
        data: symbolFiltered.map(row => ({ x: row.avg_sentiment, y: row.close })),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
      },
    ],
  };

  const scatterOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: true, text: `Correlación Sentimiento vs Precio (${selectedSymbol})` },
      tooltip: { mode: 'nearest', intersect: false },
    },
    scales: {
      x: {
        title: { display: true, text: 'Sentimiento Promedio' },
        min: -1,
        max: 1,
      },
      y: {
        title: { display: true, text: 'Precio de Cierre' },
      },
    },
  };

  return (
    <div>
      <h2>Precios de Acciones</h2>
      <div style={{marginBottom: '1rem', display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center'}}>
        <label>Rango de tiempo: </label>
        <select value={hours} onChange={e => setHours(Number(e.target.value))}>
          {TIME_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <label>Búsqueda símbolo: </label>
        <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="AAPL, MSFT..." />
        <label>Precio cierre:</label>
        <input type="number" step="0.01" min="0" value={minPrice} onChange={e => setMinPrice(Number(e.target.value))} style={{width: 80}} />
        <span>-</span>
        <input type="number" step="0.01" min="0" value={maxPrice} onChange={e => setMaxPrice(Number(e.target.value))} style={{width: 80}} />
        <button style={{marginLeft: '1rem'}} onClick={() => exportToCSV(paginatedData)}>
          Exportar CSV
        </button>
      </div>
      {loading && <p>Cargando...</p>}
      {error && <p style={{color: 'red'}}>{error}</p>}
      {!loading && !error && (
        <>
          <div style={{marginBottom: '1rem'}}>
            <label>Selecciona un símbolo: </label>
            <select value={selectedSymbol} onChange={e => setSelectedSymbol(e.target.value)}>
              <option value=''>-- Selecciona --</option>
              {symbols.filter(sym => sym.toLowerCase().includes(search.toLowerCase())).map(sym => (
                <option key={sym} value={sym}>{sym}</option>
              ))}
            </select>
          </div>
          {selectedSymbol && symbolFiltered.length > 0 && (
            <>
              <div style={{
                color: '#fff', background: 'rgba(0,0,0,0.3)', borderRadius: 8, padding: 12, margin: '0 auto 1rem auto', maxWidth: 800
              }}>
                <b>Resumen {selectedSymbol}:</b>
                &nbsp;Precio promedio: <b>${avgPrice}</b>
                &nbsp;| Máximo: <b>${maxPriceStat}</b>
                &nbsp;| Mínimo: <b>${minPriceStat}</b>
                &nbsp;| Último: <b>${lastPrice}</b>
                {symbolFiltered.length === 1 && (
                  <span style={{ color: 'yellow', marginLeft: 16 }}>⚠️ Solo hay un dato disponible para este período.</span>
                )}
              </div>
              <div style={{maxWidth: 800, margin: '0 auto 2rem auto'}}>
                <Line data={chartData} options={chartOptions} />
              </div>
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
                <th>Fecha/Hora</th>
                <th>Cierre</th>
                <th>Máximo</th>
                <th>Mínimo</th>
                <th>Volumen</th>
              </tr>
            </thead>
            <tbody>
              {paginatedData.map((row, idx) => (
                <tr key={`${row.symbol ?? ''}-${row.hour ?? ''}-${idx}`}>
                  <td>{row.symbol}</td>
                  <td>{row.hour}</td>
                  <td>{row.close}</td>
                  <td>{row.high}</td>
                  <td>{row.low}</td>
                  <td>{row.volume}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {/* Controles de paginación */}
          {selectedSymbol && totalPages > 1 && (
            <div style={{marginTop: '1rem', textAlign: 'center'}}>
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Anterior</button>
              <span style={{margin: '0 1rem'}}>Página {page} de {totalPages}</span>
              <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Siguiente</button>
            </div>
          )}
        </>
      )}
      {!loading && !error && symbolFiltered.length === 0 && <p>No hay datos para los filtros seleccionados.</p>}
    </div>
  );
}

export default StockPrices; 
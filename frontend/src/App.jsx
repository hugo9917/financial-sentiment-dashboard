import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import SentimentAnalysis from './pages/SentimentAnalysis';
import StockPrices from './pages/StockPrices';
import Correlation from './pages/Correlation';
import News from './pages/News';
import './App.css';

function App() {
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    // Verificar estado de la API al cargar
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/health`);
      const data = await response.json();
      setApiStatus(data.status);
    } catch (error) {
      setApiStatus('error');
      console.error('Error checking API health:', error);
    }
  };

  return (
    <Router>
      <div className="App">
        <Navbar apiStatus={apiStatus} />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/sentiment" element={<SentimentAnalysis />} />
            <Route path="/stocks" element={<StockPrices />} />
            <Route path="/correlation" element={<Correlation />} />
            <Route path="/news" element={<News />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 
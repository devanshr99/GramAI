import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function WeatherWidget({ isOnline, t }) {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchWeather() {
      setLoading(true);
      try {
        // Try to fetch from backend API if online
        if (isOnline) {
          const API_BASE = import.meta.env.VITE_API_URL || 'https://gramai-0n2o.onrender.com';
          const res = await fetch(`${API_BASE}/api/weather?city=New+Delhi`);
          if (res.ok) {
            const data = await res.json();
            setWeather({ ...data, source: 'live' });
            // Save to frontend localStorage for True Offline fallback
            localStorage.setItem('gramai_weather', JSON.stringify({ ...data, source: 'cached' }));
            setLoading(false);
            return;
          }
        }
        throw new Error("Offline or API failed");
      } catch (err) {
        // Offline Fallback
        const cached = localStorage.getItem('gramai_weather');
        if (cached) {
          setWeather(JSON.parse(cached));
        } else {
          setError("No offline data available");
        }
      } finally {
        setLoading(false);
      }
    }

    fetchWeather();
    // Refresh weather if online status changes to true
  }, [isOnline]);

  if (loading) {
    return (
      <div className="weather-widget loading">
        <div className="skeleton-line" />
        <div className="skeleton-line short" />
      </div>
    );
  }

  if (error && !weather) {
    return (
      <div className="weather-widget error">
        <span>⚠️ {t('No offline weather data')}</span>
      </div>
    );
  }

  if (!weather) return null;

  return (
    <motion.div 
      className={`weather-widget ${weather.source === 'live' ? 'live' : 'cached'}`}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
    >
      <div className="weather-header">
        <span className="city-name">📍 {weather.city}</span>
        <span className={`status-badge ${weather.source}`}>
          {weather.source === 'live' ? '🟢 Live' : '🟠 Offline/Cached'}
        </span>
      </div>
      
      <div className="weather-body">
        <div className="weather-main">
          <span className="condition-icon">{weather.condition.split(' ')[0]}</span>
          <div className="temp-block">
            <span className="temperature">{weather.temperature}°C</span>
            <span className="condition-text">{weather.condition.replace(/^[^\w\s]+/u, '').trim()}</span>
          </div>
        </div>
      </div>
      
      {weather.prediction && (
        <div className="weather-footer">
          <span className="prediction-text">🤖 AI: {weather.prediction}</span>
        </div>
      )}
    </motion.div>
  );
}

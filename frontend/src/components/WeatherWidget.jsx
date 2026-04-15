import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function WeatherWidget({ isOnline, t }) {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // UI States
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Location Preferences
  const [locPrefs, setLocPrefs] = useState(() => {
    // Check localStorage first
    const saved = localStorage.getItem('gramai_loc_prefs');
    return saved ? JSON.parse(saved) : { lat: 28.6139, lon: 77.2090, city: "New Delhi" };
  });

  const fetchWeather = async (lat, lon, city) => {
    setLoading(true);
    setError(null);
    try {
      if (isOnline) {
        const API_BASE = import.meta.env.VITE_API_URL || 'https://gramai-0n2o.onrender.com';
        const url = `${API_BASE}/api/weather?lat=${lat}&lon=${lon}&city=${encodeURIComponent(city)}`;
        
        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          setWeather({ ...data, source: 'live' });
          localStorage.setItem('gramai_weather', JSON.stringify({ ...data, source: 'cached' }));
          setLoading(false);
          return;
        }
      }
      throw new Error("Offline or API failed");
    } catch (err) {
      // Offline format
      const cached = localStorage.getItem('gramai_weather');
      if (cached) {
        setWeather(JSON.parse(cached));
      } else {
        setError("No offline data available");
      }
    } finally {
      setLoading(false);
    }
  };

  // Re-fetch when connection comes back or location preferences change
  useEffect(() => {
    fetchWeather(locPrefs.lat, locPrefs.lon, locPrefs.city);
    // eslint-disable-next-line
  }, [isOnline, locPrefs]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim() || !isOnline) return;
    
    setLoading(true);
    try {
      // Use Open-Meteo free geocoding to get lat long from city name
      const geoRes = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(searchQuery)}&count=1&language=en&format=json`);
      const geoData = await geoRes.json();
      
      if (geoData.results && geoData.results.length > 0) {
        const result = geoData.results[0];
        const newPrefs = { lat: result.latitude, lon: result.longitude, city: result.name };
        
        setLocPrefs(newPrefs);
        localStorage.setItem('gramai_loc_prefs', JSON.stringify(newPrefs));
        setShowSearch(false);
        setSearchQuery('');
      } else {
        alert("City not found. Please try another name.");
      }
    } catch (err) {
      alert("Error searching city. Check your internet connection.");
    }
    setLoading(false);
  };

  const handleCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser");
      return;
    }
    
    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        let cityName = "My Location";
        
        try {
          if (isOnline) {
            // Reverse geocode to get a named locality
            const res = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`);
            const data = await res.json();
            cityName = data.locality || data.city || data.principalSubdivision || "My Location";
          }
        } catch (e) {
          console.warn("Reverse geocode failed", e);
        }

        const newPrefs = { lat, lon, city: cityName };
        setLocPrefs(newPrefs);
        localStorage.setItem('gramai_loc_prefs', JSON.stringify(newPrefs));
        setShowSearch(false);
      },
      (err) => {
        setLoading(false);
        if (err.code === 1) alert("Please allow location access to use this feature.");
        else alert("Failed to get location.");
      },
      { timeout: 10000 }
    );
  };

  if (loading && !weather) {
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
    >
      <div className="weather-header">
        <span className="city-name" onClick={() => setShowSearch(!showSearch)} style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}>
          📍 {weather.city} 
          <span style={{ fontSize: '0.6rem', opacity: 0.6 }}>▼</span>
        </span>
        <span className={`status-badge ${weather.source}`}>
          {weather.source === 'live' ? '🟢 Live' : '🟠 Offline/Cached'}
        </span>
      </div>

      <AnimatePresence>
        {showSearch && (
          <motion.div 
            className="weather-search-box"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
          >
            <form onSubmit={handleSearch} style={{ display: 'flex', gap: '6px', marginBottom: '10px' }}>
              <input 
                type="text" 
                placeholder="Enter city name..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                disabled={!isOnline}
                style={{ flex: 1, padding: '6px 12px', borderRadius: '20px', border: '1px solid var(--border)', background: 'var(--surface-2)', color: 'var(--text-primary)', fontSize: '0.8rem', outline: 'none' }}
              />
              <button 
                type="submit" 
                disabled={!isOnline || !searchQuery.trim()}
                style={{ padding: '6px 14px', borderRadius: '20px', border: 'none', background: 'var(--primary)', color: 'white', cursor: 'pointer', fontSize: '0.8rem' }}
              >
                Search
              </button>
            </form>
            
            <button 
              onClick={handleCurrentLocation}
              style={{ width: '100%', padding: '8px', borderRadius: '20px', border: '1px solid var(--border)', background: 'rgba(59,130,246,0.1)', color: '#93c5fd', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', fontSize: '0.8rem' }}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
              Use Current Location
            </button>
          </motion.div>
        )}
      </AnimatePresence>
      
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

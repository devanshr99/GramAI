import { motion } from 'framer-motion';
import { createPortal } from 'react-dom';

export default function ForecastPage({ dailyForecast, cityName, onClose, t }) {
  return createPortal(
    <motion.div 
      className="forecast-page-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(5, 5, 5, 0.85)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        zIndex: 9999,
        overflowY: 'auto',
        padding: '24px 16px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}
    >
      <div style={{ width: '100%', maxWidth: '500px', paddingBottom: '40px' }}>
        <motion.div 
          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px', padding: '0 8px' }}
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
        >
          <div>
            <h2 style={{ margin: 0, color: 'var(--text-primary)', fontSize: '1.6rem', fontWeight: 800 }}>
              7-Day Forecast
            </h2>
            <p style={{ margin: '4px 0 0 0', color: 'var(--primary-light)', fontSize: '0.9rem', fontWeight: 600 }}>
              📍 {cityName}
            </p>
          </div>
          <button 
            onClick={onClose}
            style={{ 
              background: 'rgba(255, 255, 255, 0.1)', 
              border: '1px solid rgba(255,255,255,0.1)', 
              color: 'var(--text-primary)', 
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.3s ease'
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </motion.div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {dailyForecast.map((day, idx) => {
            const dateObj = new Date(day.date);
            const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'long' });
            const dateString = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            const isToday = idx === 0;
            
            return (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.08, duration: 0.4 }}
                whileHover={{ scale: 1.02 }}
                style={{
                  background: isToday ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05))' : 'var(--surface-2)',
                  border: isToday ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid var(--border)',
                  borderRadius: '20px',
                  padding: '20px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  boxShadow: isToday ? '0 8px 32px rgba(16, 185, 129, 0.1)' : '0 4px 16px rgba(0,0,0,0.2)',
                  position: 'relative',
                  overflow: 'hidden'
                }}
              >
                {isToday && <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', background: 'var(--primary)' }} />}
                
                <div style={{ flex: 1.2 }}>
                  <div style={{ fontWeight: '700', fontSize: '1.1rem', color: isToday ? 'var(--primary-light)' : 'var(--text-primary)' }}>
                    {isToday ? "Today" : dayName}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>{dateString}</div>
                </div>
                
                <div style={{ flex: 1.5, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{ fontSize: '2.2rem', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' }}>{day.condition.split(' ')[0]}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 500, marginTop: '4px', textTransform: 'capitalize' }}>
                    {day.condition.replace(/^[^\w\s]+/u, '').trim()}
                  </div>
                </div>
                
                <div style={{ flex: 1, textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                    <span style={{ fontWeight: '800', color: '#f87171', fontSize: '1.2rem' }}>{day.max_temp}°</span>
                    <span style={{ color: '#60a5fa', fontSize: '0.95rem', fontWeight: '600' }}>{day.min_temp}°</span>
                  </div>
                  <div style={{ display: 'flex', gap: '8px', fontSize: '0.7rem', color: 'var(--text-muted)', background: 'rgba(0,0,0,0.2)', padding: '4px 8px', borderRadius: '12px' }}>
                    <span title="Wind speed">💨 {day.wind}km/h</span>
                    <span title="Precipitation">💧 {day.rain}mm</span>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </motion.div>,
    document.body
  );
}

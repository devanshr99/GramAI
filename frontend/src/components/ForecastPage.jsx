import { motion } from 'framer-motion';

export default function ForecastPage({ dailyForecast, cityName, onClose, t }) {
  return (
    <motion.div 
      className="forecast-page-overlay"
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 50 }}
      style={{
        position: 'fixed',
        top: 0, left: 0, right: 0, bottom: 0,
        background: 'linear-gradient(135deg, var(--surface-1) 0%, var(--surface-2) 100%)',
        zIndex: 1000,
        overflowY: 'auto',
        padding: '20px'
      }}
    >
      <div style={{ maxWidth: '600px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ margin: 0, color: 'var(--text-primary)', fontSize: '1.5rem' }}>
            📅 7-Day Forecast: {cityName}
          </h2>
          <button 
            onClick={onClose}
            style={{ 
              background: 'rgba(255, 255, 255, 0.1)', 
              border: 'none', 
              color: 'var(--text-primary)', 
              padding: '8px 16px', 
              borderRadius: '20px',
              cursor: 'pointer',
              fontSize: '1rem',
              backdropFilter: 'blur(10px)'
            }}
          >
            ❌ Close
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          {dailyForecast.map((day, idx) => {
            const dateObj = new Date(day.date);
            const dayName = dateObj.toLocaleDateString('en-US', { weekday: 'long' });
            const dateString = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            
            return (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                style={{
                  background: 'var(--surface-2)',
                  border: '1px solid var(--border)',
                  borderRadius: '16px',
                  padding: '15px 20px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  boxShadow: '0 4px 6px rgba(0,0,0,0.05)'
                }}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 'bold', fontSize: '1.1rem', color: 'var(--text-primary)' }}>{idx === 0 ? "Today" : dayName}</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{dateString}</div>
                </div>
                
                <div style={{ flex: 1, textAlign: 'center', fontSize: '1.8rem' }}>
                  {day.condition.split(' ')[0]} {/* Emoji only */}
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    {day.condition.replace(/^[^\w\s]+/u, '').trim()}
                  </div>
                </div>
                
                <div style={{ flex: 1, textAlign: 'right' }}>
                  <div style={{ fontWeight: 'bold', color: '#ef4444', fontSize: '1.1rem' }}>{day.max_temp}°</div>
                  <div style={{ color: '#3b82f6', fontSize: '0.9rem' }}>{day.min_temp}°</div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}

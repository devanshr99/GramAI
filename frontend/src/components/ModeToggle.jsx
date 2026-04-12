import { motion } from 'framer-motion';
import { Wifi, WifiOff, Sparkles, Database } from 'lucide-react';

export default function ModeToggle({ mode, onSwitch, t }) {
  return (
    <div className="mode-toggle-bar">
      <motion.button
        className={`mode-btn ${mode === 'offline' ? 'active' : ''}`}
        onClick={() => onSwitch('offline')}
        whileTap={{ scale: 0.95 }}
      >
        <WifiOff size={14} />
        <span>{t('offlineMode')}</span>
        <Database size={11} style={{ opacity: 0.5 }} />
      </motion.button>
      <motion.button
        className={`mode-btn online ${mode === 'online' ? 'active' : ''}`}
        onClick={() => onSwitch('online')}
        whileTap={{ scale: 0.95 }}
      >
        <Wifi size={14} />
        <span>{t('onlineMode')}</span>
        <Sparkles size={11} style={{ opacity: 0.5 }} />
      </motion.button>
    </div>
  );
}

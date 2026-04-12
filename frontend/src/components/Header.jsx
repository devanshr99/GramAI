import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LANG_NAMES, LANG_ENGLISH } from '../i18n/translations';
import { Globe, ChevronDown, Check } from 'lucide-react';

export default function Header({ lang, t, changeLanguage, isOnline, showToast }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const close = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, []);

  return (
    <header className="header">
      <motion.div className="header-logo"
        animate={{ y: [0, -3, 0] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      >
        🌾
      </motion.div>
      <div className="header-info">
        <h1>GramAI</h1>
        <p>{t('subtitle')}</p>
      </div>

      {/* Language Selector */}
      <div ref={ref} style={{ position: 'relative' }}>
        <button className={`lang-toggle ${open ? 'open' : ''}`} onClick={() => setOpen(!open)}>
          <Globe size={13} />
          <span>{LANG_NAMES[lang]}</span>
          <ChevronDown size={11} className="arrow" />
        </button>

        <AnimatePresence>
          {open && (
            <motion.div
              className="lang-dropdown"
              initial={{ opacity: 0, y: -8, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -8, scale: 0.96 }}
              transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
            >
              {Object.entries(LANG_NAMES).map(([code, name]) => (
                <div
                  key={code}
                  className={`lang-item ${lang === code ? 'active' : ''}`}
                  onClick={() => {
                    changeLanguage(code);
                    setOpen(false);
                    showToast(`${t('langChanged')}: ${name}`);
                  }}
                >
                  <span className="lang-item-name">{name}</span>
                  <span className="lang-item-en">{LANG_ENGLISH[code]}</span>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="status-pill">
        <span className={`status-dot ${isOnline ? '' : 'offline'}`} />
        <span>{isOnline ? t('online') : t('offline')}</span>
      </div>
    </header>
  );
}

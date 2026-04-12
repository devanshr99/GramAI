import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function InstallBanner({ t }) {
  const [show, setShow] = useState(false);
  const [prompt, setPrompt] = useState(null);

  useEffect(() => {
    const handler = (e) => {
      e.preventDefault();
      setPrompt(e);
      if (!localStorage.getItem('gramai_install_dismissed')) {
        setTimeout(() => setShow(true), 3000);
      }
    };
    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = async () => {
    if (!prompt) return;
    prompt.prompt();
    await prompt.userChoice;
    setShow(false);
    setPrompt(null);
  };

  const handleDismiss = () => {
    setShow(false);
    localStorage.setItem('gramai_install_dismissed', '1');
  };

  return (
    <AnimatePresence>
      {show && (
        <motion.div className="install-bar"
          initial={{ y: 120 }}
          animate={{ y: 0 }}
          exit={{ y: 120 }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="install-bar-inner">
            <img src="/assets/icon-96.png" alt="GramAI" />
            <div className="install-bar-text">
              <strong>{t('installTitle')}</strong>
              <p>{t('installDesc')}</p>
            </div>
            <button className="install-bar-btn" onClick={handleInstall}>
              {t('installBtn')}
            </button>
            <button className="install-bar-close" onClick={handleDismiss}>✕</button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

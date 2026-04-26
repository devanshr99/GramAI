import { useState, useEffect, useCallback } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useLanguage } from './hooks/useLanguage';
import { api } from './api';
import Header from './components/Header';
import CategoryGrid from './components/CategoryGrid';
import CategoryDetailView from './components/CategoryDetailView';
import WeatherWidget from './components/WeatherWidget';
import ChatArea from './components/ChatArea';
import InputArea from './components/InputArea';
import ModeToggle from './components/ModeToggle';
import Toast from './components/Toast';
import InstallBanner from './components/InstallBanner';
import './index.css';

export default function App() {
  const { lang, t, changeLanguage } = useLanguage();

  // Separate chat histories for each mode
  const [offlineMessages, setOfflineMessages] = useState([]);
  const [onlineMessages, setOnlineMessages] = useState([]);

  const [category, setCategory] = useState(null);
  const [isOnline, setIsOnline] = useState(false);
  const [useLLM, setUseLLM] = useState(true);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [toast, setToast] = useState('');
  const [mode, setMode] = useState('offline');
  const [onlineAIAvailable, setOnlineAIAvailable] = useState(false);

  // Get current messages based on mode
  const messages = mode === 'online' ? onlineMessages : offlineMessages;
  // setMessages handled inline 

  const showToast = useCallback((msg) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3500);
  }, []);

  // Server health check
  useEffect(() => {
    // Dismiss loading screen quickly to open app fast
    const timer = setTimeout(() => setLoading(false), 200);

    // Perform health checks in background
    (async () => {
      try {
        const ok = await api.health();
        setIsOnline(ok);
        if (ok) {
          const status = await api.status();
          if (status && !status.services?.llm?.available) {
            setUseLLM(false);
          }
          const aiStatus = await api.onlineStatus();
          setOnlineAIAvailable(aiStatus.available);
        }
      } catch { setIsOnline(false); }
    })();

    return () => clearTimeout(timer);
  }, []);

  const handleSend = useCallback(async (text) => {
    if (!text.trim() || processing) return;
    const userMsg = { role: 'user', text, time: new Date() };

    // Add to the correct message list
    const currentSetMessages = mode === 'online' ? setOnlineMessages : setOfflineMessages;
    const currentMessages = mode === 'online' ? onlineMessages : offlineMessages;

    currentSetMessages(prev => [...prev, userMsg]);
    setProcessing(true);

    try {
      const result = await api.query(
        text,
        mode === 'offline' ? category : null,
        useLLM,
        lang,
        mode,
        currentMessages
      );
      currentSetMessages(prev => [...prev, {
        role: 'bot',
        text: result.response,
        sources: result.sources || [],
        time: new Date(),
        mode: result.mode
      }]);
    } catch (e) {
      currentSetMessages(prev => [...prev, {
        role: 'bot', text: `⚠️ ${t('error')}\n${e.message}`, sources: [], time: new Date()
      }]);
    }
    setProcessing(false);
  }, [processing, category, useLLM, lang, mode, onlineMessages, offlineMessages, t]);

  const handleCategorySelect = useCallback((cat) => {
    if (category === cat) {
      setCategory(null);
      showToast(t('allTopics'));
    } else {
      setCategory(cat);
      showToast(t('topicSelected'));
    }
  }, [category, t, showToast]);

  const handleModeSwitch = useCallback((newMode) => {
    if (newMode === mode) return;
    setMode(newMode);
    if (newMode === 'online' && !onlineAIAvailable) {
      showToast(t('onlineNotConfigured'));
    } else {
      showToast(newMode === 'online' ? `🌐 ${t('onlineMode')}` : `📴 ${t('offlineMode')}`);
    }
  }, [mode, onlineAIAvailable, t, showToast]);

  // Clear current mode's chat
  const handleClearChat = useCallback(() => {
    if (mode === 'online') {
      setOnlineMessages([]);
    } else {
      setOfflineMessages([]);
    }
    showToast('🗑️ Chat cleared');
  }, [mode, showToast]);

  return (
    <>
      <AnimatePresence>
        {loading && (
          <motion.div className="loader-screen" exit={{ opacity: 0 }} transition={{ duration: 0.3 }}>
            <div className="loader-ring" />
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{t('loading')}</p>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="app-shell">
        <Header
          lang={lang} t={t} changeLanguage={changeLanguage}
          isOnline={isOnline} showToast={showToast}
        />
        <WeatherWidget isOnline={isOnline} t={t} />
        <ModeToggle mode={mode} onSwitch={handleModeSwitch} t={t} onlineAvailable={onlineAIAvailable} />

        {mode === 'offline' && !category && (
          <CategoryGrid t={t} category={category} onSelect={handleCategorySelect} />
        )}

        <AnimatePresence mode="wait">
          {mode === 'offline' && category && (
            <CategoryDetailView 
              category={category} 
              t={t} 
              onBack={() => {
                setCategory(null);
                showToast(t('allTopics'));
              }} 
              onFaqClick={(faqText) => handleSend(faqText)} 
            />
          )}
        </AnimatePresence>

        <ChatArea
          messages={messages}
          processing={processing}
          t={t}
          lang={lang}
          mode={mode}
          onClearChat={handleClearChat}
        />
        <InputArea
          t={t} onSend={handleSend} processing={processing}
          showToast={showToast} lang={lang} mode={mode}
        />
      </div>

      <Toast message={toast} />
      <InstallBanner t={t} />
    </>
  );
}

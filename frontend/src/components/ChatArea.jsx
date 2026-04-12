import { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../api';
import { TTS_CODES } from '../i18n/translations';

function formatText(text) {
  let html = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/^### (.+)$/gm, '<strong style="font-size:0.95rem;display:block;margin-top:8px;">$1</strong>');
  html = html.replace(/^## (.+)$/gm, '<strong style="font-size:1rem;display:block;margin-top:10px;">$1</strong>');
  html = html.replace(/^[•\-*] (.+)$/gm, '<span style="display:block;padding-left:12px;">• $1</span>');
  html = html.replace(/^(\d+)\. (.+)$/gm, '<span style="display:block;padding-left:12px;">$1. $2</span>');
  html = html.replace(/\n/g, '<br/>');
  return html;
}

function Message({ msg, t, lang }) {
  const isBot = msg.role === 'bot';
  const time = msg.time.toLocaleTimeString(TTS_CODES[lang] || 'hi-IN', { hour: '2-digit', minute: '2-digit' });

  const handleSpeak = async (e) => {
    const btn = e.currentTarget;
    const clean = msg.text.replace(/<[^>]*>/g, '').replace(/\*\*/g, '').replace(/#{1,3} /g, '')
      .replace(/(⚠️|✅|📖|🌾|🏥|📚|🏛️|💰|🤒|🎓|🌿|🌱|🌐)/gu, '').trim();
    if (!clean) return;
    btn.innerHTML = '⏳';
    try {
      const blob = await api.speak(clean);
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.play();
      audio.onended = () => { btn.innerHTML = '🔊'; URL.revokeObjectURL(url); };
    } catch {
      if ('speechSynthesis' in window) {
        const utter = new SpeechSynthesisUtterance(clean);
        utter.lang = TTS_CODES[lang] || 'hi-IN';
        utter.rate = 0.9;
        utter.onend = () => { btn.innerHTML = '🔊'; };
        speechSynthesis.speak(utter);
      } else { btn.innerHTML = '🔊'; }
    }
  };

  return (
    <motion.div
      className={`msg ${msg.role}`}
      initial={{ opacity: 0, y: 16, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="msg-avatar">{isBot ? '🌾' : '👤'}</div>
      <div className="msg-bubble">
        <div className="msg-text" dangerouslySetInnerHTML={{ __html: formatText(msg.text) }} />
        {isBot && msg.sources?.length > 0 && (
          <div className="msg-sources">
            📖 {t('source')}:
            {msg.sources.filter(s => s.title).map((s, i) => (
              <span className="source-tag" key={i}>{s.category}: {s.title}</span>
            ))}
          </div>
        )}
        <div className="msg-time">
          {msg.mode && (
            <span className={`mode-badge ${msg.mode}`}>
              {msg.mode === 'online' ? '🌐 AI' : '📴 KB'}
            </span>
          )}
          {' '}{time}
        </div>
        {isBot && (
          <div className="msg-actions">
            <button className="speak-btn" onClick={handleSpeak} title="🔊">🔊</button>
          </div>
        )}
      </div>
    </motion.div>
  );
}

function TypingIndicator() {
  return (
    <motion.div className="msg bot"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="msg-avatar">🌾</div>
      <div className="msg-bubble">
        <div className="typing"><span /><span /><span /></div>
      </div>
    </motion.div>
  );
}

export default function ChatArea({ messages, processing, t, lang, mode, onClearChat }) {
  const endRef = useRef(null);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, processing]);

  const isOnline = mode === 'online';

  return (
    <main className="chat-area">
      {/* Clear chat button - only show when there are messages */}
      {messages.length > 0 && (
        <motion.button
          className="clear-chat-btn"
          onClick={onClearChat}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          🗑️ Clear Chat
        </motion.button>
      )}

      {messages.length === 0 && !processing && (
        <motion.div className="welcome"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.span className="welcome-emoji"
            animate={{ rotate: [0, 12, -12, 0] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
          >{isOnline ? '🌐' : '🙏'}</motion.span>

          <h3>{isOnline ? (t('onlineGreeting') || '🤖 Online AI Mode') : t('greeting')}</h3>

          <p>{isOnline
            ? (t('onlineWelcome') || 'Ask me anything! I\'m powered by DeepSeek AI and can answer any question.')
            : t('welcomeMsg')
          }</p>

          <p className="hint">{isOnline
            ? (t('onlineHint') || '💡 Try: "How does photosynthesis work?" or "Explain gravity"')
            : t('welcomeHint')
          }</p>

          <div style={{ marginTop: '12px' }}>
            <span className={`mode-badge ${mode}`} style={{ fontSize: '0.72rem', padding: '4px 14px' }}>
              {isOnline ? '🌐 Online AI — Any Question' : '📴 Offline KB — Agriculture, Health, Education, Schemes'}
            </span>
          </div>
        </motion.div>
      )}

      <AnimatePresence>
        {messages.map((msg, i) => (
          <Message key={`${mode}-${i}`} msg={msg} t={t} lang={lang} />
        ))}
      </AnimatePresence>
      {processing && <TypingIndicator />}
      <div ref={endRef} />
    </main>
  );
}

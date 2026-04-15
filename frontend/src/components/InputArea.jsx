import { useState, useRef, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Mic, MicOff, Send } from 'lucide-react';
import { TTS_CODES } from '../i18n/translations';

const QUICK_ACTIONS = [
  { key: 'quickWheat', emoji: '🌾', query: 'गेहूं की खेती कैसे करें?' },
  { key: 'quickPM', emoji: '💰', query: 'PM-KISAN योजना क्या है?' },
  { key: 'quickFever', emoji: '🤒', query: 'बुखार का इलाज' },
  { key: 'quickScholar', emoji: '🎓', query: 'छात्रवृत्ति कैसे मिलेगी?' },
  { key: 'quickOrganic', emoji: '🌿', query: 'जैविक खेती कैसे करें?' },
  { key: 'quickAyush', emoji: '🏥', query: 'आयुष्मान भारत कार्ड कैसे बनवाएं?' },
];

// Browser-native speech recognition (works without any backend)
function getSpeechRecognition() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return null;
  return new SR();
}

export default function InputArea({ t, onSend, processing, showToast, lang }) {
  const [text, setText] = useState('');
  const [listening, setListening] = useState(false);
  const [interimText, setInterimText] = useState('');
  const recognitionRef = useRef(null);
  const textareaRef = useRef(null);

  // Cleanup recognition on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  const handleSend = () => {
    if (!text.trim() || processing) return;
    onSend(text.trim());
    setText('');
    setInterimText('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e) => {
    setText(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px';
  };

  const startListening = useCallback(() => {
    const recognition = getSpeechRecognition();
    if (!recognition) {
      showToast(`⚠️ ${t('micUnavailable')} - Browser does not support Speech Recognition`);
      return;
    }

    // Configure recognition
    recognition.lang = TTS_CODES[lang] || 'hi-IN';
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setListening(true);
      setInterimText('');
      showToast(`🎤 ${t('speak')}`);
    };

    recognition.onresult = (event) => {
      let interim = '';
      let final = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript;
        } else {
          interim += transcript;
        }
      }

      if (final) {
        // Final result - set text and auto-send
        showToast(`✅ ${t('recognized')}: "${final}"`);
        setText('');
        setInterimText('');
        setListening(false);
        // Send directly
        onSend(final.trim());
      } else if (interim) {
        setInterimText(interim);
      }
    };

    recognition.onerror = (event) => {
      setListening(false);
      setInterimText('');
      if (event.error === 'no-speech') {
        showToast(`⚠️ ${t('noSpeech')}`);
      } else if (event.error === 'not-allowed') {
        showToast(`⚠️ ${t('micUnavailable')} - Permission denied`);
      } else if (event.error === 'network') {
        // Native browser STT fails offline without device language packs
        showToast(`⚠️ Offline Voice: Please download 'Hindi' offline speech pack in your phone's Google Voice settings.`);
        console.warn('Speech recognition network error: Offline mode requires device language packs.');
      } else {
        showToast(`⚠️ ${t('voiceUnavailable')}: ${event.error}`);
      }
    };

    recognition.onend = () => {
      setListening(false);
      // If there was interim text but no final result, use the interim text
      if (interimText) {
        setText(interimText);
        setInterimText('');
      }
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch (err) {
      console.error(err);
      showToast(`⚠️ ${t('micUnavailable')}`);
      setListening(false);
    }
  }, [lang, t, showToast, onSend, interimText]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setListening(false);
  }, []);

  return (
    <footer className="input-area">
      <div className="input-row">
        <textarea
          ref={textareaRef}
          value={listening ? (interimText || text) : text}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder={listening ? `🎤 ${t('speak')}` : t('inputPlaceholder')}
          rows={1}
          readOnly={listening}
          style={listening ? { color: '#fbbf24', fontStyle: 'italic' } : undefined}
        />
        <motion.button
          className={`icon-btn mic-btn ${listening ? 'recording' : ''}`}
          onClick={listening ? stopListening : startListening}
          whileTap={{ scale: 0.9 }}
          title={listening ? 'Stop listening' : 'Start voice input'}
        >
          {listening ? <MicOff size={18} /> : <Mic size={18} />}
        </motion.button>
        <motion.button
          className="icon-btn send-btn"
          onClick={handleSend}
          disabled={(!text.trim() && !interimText) || processing}
          whileTap={{ scale: 0.9 }}
          title="Send message"
        >
          <Send size={18} />
        </motion.button>
      </div>

      <div className="quick-actions">
        {QUICK_ACTIONS.map((qa) => (
          <motion.button
            key={qa.key}
            className="quick-chip"
            onClick={() => onSend(qa.query)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {qa.emoji} {t(qa.key)}
          </motion.button>
        ))}
      </div>
    </footer>
  );
}

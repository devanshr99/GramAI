import { useState, useRef, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Mic, MicOff, Send, Image as ImageIcon, X } from 'lucide-react';
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

// Client-side image compression & resizing utility
const compressImage = (file, maxWidth = 1024, maxHeight = 1024, quality = 0.7) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = (event) => {
      const img = new window.Image();
      img.src = event.target.result;
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;

        if (width > height) {
          if (width > maxWidth) {
            height = Math.round((height * maxWidth) / width);
            width = maxWidth;
          }
        } else {
          if (height > maxHeight) {
            width = Math.round((width * maxHeight) / height);
            height = maxHeight;
          }
        }

        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        
        // Convert canvas image to base64 JPEG with specified quality
        const dataUrl = canvas.toDataURL('image/jpeg', quality);
        resolve(dataUrl);
      };
      img.onerror = (err) => reject(err);
    };
    reader.onerror = (err) => reject(err);
  });
};

export default function InputArea({ t, onSend, processing, showToast, lang, mode }) {
  const [text, setText] = useState('');
  const [listening, setListening] = useState(false);
  const [interimText, setInterimText] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  
  const recognitionRef = useRef(null);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  // Cleanup recognition on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  const handleSend = () => {
    if ((!text.trim() && !selectedImage) || processing) return;
    
    // If user uploaded an image but provided no text query, send a default prompt
    const finalQuery = text.trim() || (lang === 'hi' ? 'इस चित्र का विश्लेषण करें' : 'Analyze this image');
    
    onSend(finalQuery, selectedImage);
    
    setText('');
    setSelectedImage(null);
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

  const handleImageClick = () => {
    if (mode !== 'online') {
      showToast(lang === 'hi' 
        ? '⚠️ फोटो अपलोड केवल ऑनलाइन AI मोड में समर्थित है। कृपया ऑनलाइन मोड चालू करें।' 
        : '⚠️ Photo upload is only supported in Online AI Mode. Switch mode to upload.'
      );
      return;
    }
    fileInputRef.current?.click();
  };

  const handleImageChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      showToast(lang === 'hi' ? '⚠️ कृपया एक चित्र फ़ाइल चुनें' : '⚠️ Please select an image file');
      return;
    }

    try {
      showToast(lang === 'hi' ? '⏳ चित्र को अनुकूलित किया जा रहा है...' : '⏳ Optimizing image...');
      const compressed = await compressImage(file);
      setSelectedImage(compressed);
      showToast(lang === 'hi' ? '✅ चित्र सफलतापूर्वक अपलोड हुआ' : '✅ Image loaded successfully');
    } catch (err) {
      console.error(err);
      showToast(lang === 'hi' ? '⚠️ चित्र लोड करने में विफल' : '⚠️ Failed to load image');
    }
    
    // Clear input value so same file can be reselected if deleted
    e.target.value = '';
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
        // Send directly (with selected image if any)
        onSend(final.trim(), selectedImage);
        setSelectedImage(null);
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
  }, [lang, t, showToast, onSend, interimText, selectedImage]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setListening(false);
  }, []);

  return (
    <footer className="input-area">
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleImageChange}
        accept="image/*"
        style={{ display: 'none' }}
      />

      {/* Selected Image Preview Container */}
      {selectedImage && (
        <div className="image-preview-wrapper">
          <div className="image-preview-card">
            <img src={selectedImage} alt="Selected preview" />
            <button className="remove-image-btn" onClick={() => setSelectedImage(null)} title="Remove photo">
              <X size={14} />
            </button>
          </div>
        </div>
      )}

      <div className="input-row">
        {/* Attachment Button */}
        <motion.button
          className={`icon-btn attach-btn ${mode !== 'online' ? 'offline' : ''}`}
          onClick={handleImageClick}
          whileTap={{ scale: 0.9 }}
          title={mode === 'online' ? 'Attach photo' : 'Photo upload (Online only)'}
          type="button"
          style={{
            marginRight: '4px',
            background: 'none',
            border: 'none',
            color: mode === 'online' ? 'var(--primary-light)' : 'var(--text-muted)',
            boxShadow: 'none',
            width: '32px',
            height: '32px'
          }}
        >
          <ImageIcon size={20} />
        </motion.button>

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
          disabled={(!text.trim() && !selectedImage && !interimText) || processing}
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

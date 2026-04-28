import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CATEGORY_FAQS, fallbackSearch } from '../offlineDB.js';

const CATEGORIES = {
  'कृषि': { icon: '🌱', key: 'catAgri', en: 'Agriculture', color: 'var(--primary)' },
  'स्वास्थ्य': { icon: '🏥', key: 'catHealth', en: 'Health', color: '#ff4d4f' },
  'शिक्षा': { icon: '📚', key: 'catEdu', en: 'Education', color: '#1890ff' },
  'सरकारी योजना': { icon: '🏛️', key: 'catSchemes', en: 'Govt. Schemes', color: '#faad14' },
};

export default function CategoryDetailView({ category, t, onBack, onFaqClick }) {
  const [expandedIndex, setExpandedIndex] = useState(null);

  if (!category || !CATEGORIES[category]) return null;
  const catInfo = CATEGORIES[category];
  const faqs = CATEGORY_FAQS[catInfo.key] || [];

  const handleToggle = (i) => {
    setExpandedIndex(expandedIndex === i ? null : i);
  };

  return (
    <motion.div 
      className="category-detail-view"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3 }}
    >
      <div className="cat-detail-header" style={{ borderLeftColor: catInfo.color }}>
        <button className="back-btn" onClick={onBack}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M15 18l-6-6 6-6" /></svg>
          {t('Back') || 'Back'}
        </button>
        <div className="cat-detail-title-wrapper">
          <span className="cat-detail-icon" style={{ background: catInfo.color + '22' }}>{catInfo.icon}</span>
          <div className="cat-detail-text">
            <h2>{t(catInfo.key)}</h2>
            <span>{catInfo.en}</span>
          </div>
        </div>
      </div>
      
      <div className="faq-section">
        <p className="faq-prompt">👉 {t('Frequently Asked Questions') || 'Frequently Asked Questions (Click to View)'}</p>
        <div className="faq-chips">
          {faqs.map((faq, i) => {
            const isExpanded = expandedIndex === i;
            // Get offline answer and strip the wrapper prefix
            const answerText = fallbackSearch(faq).replace('(Offline Mode)\\nज्ञान आधार से प्रमाणित जानकारी:\\n\\n', '');
            
            return (
              <motion.div 
                key={i} 
                className={`faq-chip-wrapper ${isExpanded ? 'expanded' : ''}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1, duration: 0.3 }}
              >
                <button 
                  className="faq-chip"
                  onClick={() => handleToggle(i)}
                >
                  <span style={{flex: 1, textAlign: 'left'}}>{faq}</span>
                  <motion.span 
                    animate={{ rotate: isExpanded ? 180 : 0 }}
                    transition={{ duration: 0.3 }}
                    style={{ fontSize: '0.8rem', opacity: 0.7 }}
                  >
                    ▼
                  </motion.span>
                </button>
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      style={{ overflow: 'hidden' }}
                    >
                      <div className="faq-answer">
                        {answerText}
                        <br/>
                        <button className="ask-ai-btn" onClick={() => onFaqClick(faq)}>
                          Ask AI in Chat 💬
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}

import { motion } from 'framer-motion';

const CATEGORIES = [
  { id: 'कृषि', icon: '🌱', key: 'catAgri', en: 'Agriculture' },
  { id: 'स्वास्थ्य', icon: '🏥', key: 'catHealth', en: 'Health' },
  { id: 'शिक्षा', icon: '📚', key: 'catEdu', en: 'Education' },
  { id: 'सरकारी योजना', icon: '🏛️', key: 'catSchemes', en: 'Govt. Schemes' },
];

export default function CategoryGrid({ t, category, onSelect }) {
  return (
    <section className="categories">
      <h2>{t('selectTopic')}</h2>
      <div className="cat-grid">
        {CATEGORIES.map((cat, i) => (
          <motion.div
            key={cat.id}
            className={`cat-card ${category === cat.id ? 'active' : ''}`}
            onClick={() => onSelect(cat.id)}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            whileHover={{ scale: 1.03, y: -3 }}
            whileTap={{ scale: 0.97 }}
          >
            <span className="cat-icon">{cat.icon}</span>
            <span className="cat-name">{t(cat.key)}</span>
            <span className="cat-en">{cat.en}</span>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

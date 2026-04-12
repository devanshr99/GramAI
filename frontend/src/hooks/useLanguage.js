import { useState, useCallback } from 'react';
import TRANSLATIONS from '../i18n/translations';

export function useLanguage() {
  const [lang, setLang] = useState(() => localStorage.getItem('gramai_lang') || 'hi');

  const t = useCallback((key) => {
    return TRANSLATIONS[lang]?.[key] || TRANSLATIONS['hi']?.[key] || key;
  }, [lang]);

  const changeLanguage = useCallback((newLang) => {
    setLang(newLang);
    localStorage.setItem('gramai_lang', newLang);
  }, []);

  return { lang, t, changeLanguage };
}

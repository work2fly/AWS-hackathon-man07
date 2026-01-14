'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import en from '../../messages/en.json';
import ar from '../../messages/ar.json';
import zh from '../../messages/zh.json';
import fr from '../../messages/fr.json';
import es from '../../messages/es.json';
import ro from '../../messages/ro.json';

type Messages = typeof en;
type Locale = 'en' | 'ar' | 'zh' | 'fr' | 'es' | 'ro';

const messages: Record<Locale, Messages> = {
  en,
  ar,
  zh,
  fr,
  es,
  ro,
};

interface LanguageContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string) => string;
  dir: 'ltr' | 'rtl';
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>('en');

  useEffect(() => {
    // Load saved locale from localStorage
    const saved = localStorage.getItem('locale') as Locale;
    if (saved && messages[saved]) {
      setLocaleState(saved);
      document.documentElement.lang = saved;
      document.documentElement.dir = saved === 'ar' ? 'rtl' : 'ltr';
    }
  }, []);

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
    localStorage.setItem('locale', newLocale);
    document.documentElement.lang = newLocale;
    document.documentElement.dir = newLocale === 'ar' ? 'rtl' : 'ltr';
  };

  const t = (key: string): string => {
    const keys = key.split('.');
    let value: any = messages[locale];
    
    for (const k of keys) {
      value = value?.[k];
    }
    
    return value || key;
  };

  const dir = locale === 'ar' ? 'rtl' : 'ltr';

  return (
    <LanguageContext.Provider value={{ locale, setLocale, t, dir }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
}

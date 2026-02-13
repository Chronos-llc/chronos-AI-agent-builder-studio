import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import {
  MARKETING_LANG_STORAGE_KEY,
  MARKETING_LANGUAGE_LABELS,
  marketingMessages,
  type MarketingLanguage,
} from './marketingMessages'

type MarketingLanguageContextValue = {
  language: MarketingLanguage
  setLanguage: (language: MarketingLanguage) => void
  t: (key: string, fallback: string) => string
  availableLanguages: Array<{ value: MarketingLanguage; label: string }>
}

const MarketingLanguageContext = createContext<MarketingLanguageContextValue | undefined>(undefined)

const isMarketingLanguage = (value: string | null): value is MarketingLanguage => {
  return value === 'en' || value === 'fr' || value === 'es' || value === 'pt'
}

export const MarketingLanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<MarketingLanguage>('en')

  useEffect(() => {
    const stored = localStorage.getItem(MARKETING_LANG_STORAGE_KEY)
    if (isMarketingLanguage(stored)) {
      setLanguageState(stored)
    }
  }, [])

  const setLanguage = (next: MarketingLanguage) => {
    setLanguageState(next)
    localStorage.setItem(MARKETING_LANG_STORAGE_KEY, next)
  }

  const t = (key: string, fallback: string) => {
    if (language === 'en') return fallback
    return marketingMessages[language]?.[key] ?? fallback
  }

  const availableLanguages = useMemo(
    () =>
      (Object.keys(MARKETING_LANGUAGE_LABELS) as MarketingLanguage[]).map((value) => ({
        value,
        label: MARKETING_LANGUAGE_LABELS[value],
      })),
    []
  )

  return (
    <MarketingLanguageContext.Provider value={{ language, setLanguage, t, availableLanguages }}>
      {children}
    </MarketingLanguageContext.Provider>
  )
}

export const useMarketingLanguageContext = () => {
  const context = useContext(MarketingLanguageContext)
  if (!context) {
    throw new Error('useMarketingLanguageContext must be used within MarketingLanguageProvider')
  }
  return context
}

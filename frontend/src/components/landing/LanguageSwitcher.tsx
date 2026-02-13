import React from 'react'
import { useMarketingI18n } from '../../hooks/useMarketingI18n'
import type { MarketingLanguage } from '../../i18n/marketingMessages'

export const LanguageSwitcher: React.FC = () => {
  const { language, setLanguage, availableLanguages } = useMarketingI18n()

  return (
    <label className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-3 py-1.5 text-xs text-white/80">
      <span className="uppercase tracking-[0.12em] text-white/60">Lang</span>
      <select
        aria-label="Language selector"
        value={language}
        onChange={(event) => setLanguage(event.target.value as MarketingLanguage)}
        className="bg-transparent text-xs font-medium text-white outline-none"
      >
        {availableLanguages.map((option) => (
          <option key={option.value} value={option.value} className="bg-[#06080D] text-white">
            {option.label}
          </option>
        ))}
      </select>
    </label>
  )
}

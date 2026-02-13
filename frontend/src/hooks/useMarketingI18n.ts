import { useMarketingLanguageContext } from '../i18n/MarketingLanguageProvider'

export const useMarketingI18n = () => {
  const { language, setLanguage, t, availableLanguages } = useMarketingLanguageContext()

  return {
    language,
    setLanguage,
    t,
    availableLanguages,
  }
}

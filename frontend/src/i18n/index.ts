import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from './en'
import it from './it'

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    it: { translation: it },
  },
  lng: localStorage.getItem('financebot-lang') ?? 'it',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
})

export default i18n

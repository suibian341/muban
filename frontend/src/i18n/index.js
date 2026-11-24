import { createI18n } from 'vue-i18n'
import zh from './zh'
import en from './en'
import es from './es'
import ar from './ar'
import ru from './ru'

const saved = localStorage.getItem('lang') || 'en'
// Ensure default is persisted so LanguageSwitcher shows correct state
if (!localStorage.getItem('lang')) {
  localStorage.setItem('lang', 'en')
}

const i18n = createI18n({
  legacy: false,
  locale: saved,
  fallbackLocale: 'en',
  messages: { zh, en, es, ar, ru }
})

// 初始化 RTL
if (saved === 'ar') {
  document.documentElement.dir = 'rtl'
  document.documentElement.lang = 'ar'
}

export function setLanguage(lang) {
  i18n.global.locale.value = lang
  localStorage.setItem('lang', lang)
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr'
  document.documentElement.lang = lang
}

export default i18n

import { ref, computed } from 'vue'
import api from '@/api'

// 全局状态
const siteMode = ref('b2b') // 'b2c' or 'b2b'
const siteConfig = ref({})
const isLoaded = ref(false)

export function useSiteMode() {
  const isB2C = computed(() => siteMode.value === 'b2c')
  const isB2B = computed(() => siteMode.value === 'b2b')

  /**
   * 加载站点模式配置
   */
  async function loadSiteMode() {
    try {
      const { data } = await api.get('/site-settings')
      siteMode.value = data.site_mode || 'b2b'
      siteConfig.value = data
      isLoaded.value = true
      return data
    } catch (error) {
      console.error('Failed to load site mode:', error)
      // 默认使用 B2B 模式
      siteMode.value = 'b2b'
      isLoaded.value = true
      return {}
    }
  }

  /**
   * 更新站点模式（仅开发者可用）
   */
  async function updateSiteMode(newMode) {
    try {
      await api.put('/dev/mode', { mode: newMode })
      siteMode.value = newMode
      // 重新加载配置
      await loadSiteMode()
      // 触发全局刷新事件
      window.dispatchEvent(new CustomEvent('site-mode-changed', { detail: { mode: newMode } }))
      return true
    } catch (error) {
      console.error('Failed to update site mode:', error)
      return false
    }
  }

  /**
   * 获取配置值
   */
  function getConfig(key, defaultValue = '') {
    return siteConfig.value[key] || defaultValue
  }

  /**
   * 获取Logo URL
   */
  function getLogo(type = 'light') {
    const key = `logo_${type}`
    return getConfig(key)
  }

  /**
   * 获取页脚配置
   */
  function getFooterConfig() {
    return {
      companyName: getConfig('footer_company_name'),
      companyInfo: getConfig('footer_company_info'),
      links: getConfig('footer_links'),
      copyright: getConfig('footer_copyright')
    }
  }

  return {
    siteMode,
    isB2C,
    isB2B,
    siteConfig,
    isLoaded,
    loadSiteMode,
    updateSiteMode,
    getConfig,
    getLogo,
    getFooterConfig
  }
}

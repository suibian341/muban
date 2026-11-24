import { ref } from 'vue'
import api from '@/api'

const clearanceEnabled = ref(false)
let initialized = false

function doLoad() {
  api.get('/clearance-categories').then(({ data }) => {
    clearanceEnabled.value = !!data.enabled
  }).catch(() => {
    clearanceEnabled.value = false
  })
}

// 全局监听分类变更事件，自动刷新清仓状态
if (typeof window !== 'undefined') {
  window.addEventListener('categories-updated', doLoad)
}

export function useClearance() {
  // 首次使用时自动加载
  if (!initialized) {
    initialized = true
    doLoad()
  }

  return {
    clearanceEnabled,
    loadClearanceStatus: doLoad
  }
}

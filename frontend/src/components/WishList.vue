<template>
  <transition name="slide">
    <div v-if="isOpen" class="wishlist-panel">
      <div class="panel-header">
        <h3>{{ t('wishlist.title') }} ({{ items.length }})</h3>
        <button @click="close" class="panel-close">✕</button>
      </div>

      <div v-if="!items.length" class="wishlist-empty">
        {{ t('wishlist.empty') }}
      </div>
      <div v-else class="wishlist-items">
        <div v-for="item in items" :key="item.id" class="wishlist-item">
          <img :src="item.product.images?.[0] || placeholder" :alt="item.product.title_en" />
          <div class="item-info">
            <h4>{{ localTitle(item.product) }}</h4>
            <div class="qty-row">
              <button class="qty-btn" @click="changeQty(item, -1)">−</button>
              <span class="qty-val">{{ item.quantity }}</span>
              <button class="qty-btn" @click="changeQty(item, 1)">+</button>
              <button @click="removeItem(item.id)" class="btn-remove">✕</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="items.length && !showSubmitForm" class="wishlist-actions">
        <el-button @click="clearAll" type="info" size="small">{{ t('wishlist.clear') }}</el-button>
        <el-button @click="openSubmitForm" type="primary" size="small">{{ t('wishlist.submit') }}</el-button>
      </div>

      <div v-if="showSubmitForm" class="wishlist-submit-form">
        <div class="submit-form-header">
          <h4>{{ t('product.inquire.title') }}</h4>
          <button @click="showSubmitForm = false" class="panel-close">✕</button>
        </div>
        <form @submit.prevent="submitWishlist" class="submit-form">
          <input v-model="submitForm.contact_name" :placeholder="t('product.inquire.name')" required />
          <input v-model="submitForm.email" :placeholder="t('product.inquire.email')" type="email" required />
          <input v-model="submitForm.company_name" :placeholder="t('product.inquire.company')" />
          <input v-model="submitForm.phone" :placeholder="t('product.inquire.phone')" />
          <el-select v-model="submitForm.source" :placeholder="isZh ? '您从哪里了解到我们？' : 'How did you find us?'" clearable style="width:100%">
            <el-option value="tiktok" label="TikTok" />
            <el-option value="facebook" label="Facebook" />
            <el-option value="google" label="Google" />
            <el-option value="instagram" label="Instagram" />
            <el-option value="referral" :label="isZh ? '朋友推荐' : 'Referral'" />
            <el-option value="other" :label="isZh ? '其他' : 'Other'" />
          </el-select>
          <textarea v-model="submitForm.message" :placeholder="t('product.inquire.msg')" rows="2"></textarea>
          <el-button type="primary" native-type="submit" :loading="submitting" size="small" style="width:100%">
            {{ submitting ? t('product.inquire.sending') : t('product.inquire.send') }}
          </el-button>
        </form>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDisplay } from '../utils/display'
import { useAuth } from '../store/auth'
import { ElMessage } from 'element-plus'
import api from '../api'

const { t } = useI18n()
const { localTitle } = useDisplay()
const { state: authState } = useAuth()
const isZh = localStorage.getItem('lang') === 'zh' || !localStorage.getItem('lang')
const isOpen = ref(false)
const items = ref([])
const showSubmitForm = ref(false)
const submitting = ref(false)
const submitForm = reactive({
  contact_name: '',
  email: '',
  company_name: '',
  phone: '',
  message: '',
  source: ''
})

const emit = defineEmits(['update:count'])

watch(() => items.value.length, (n) => emit('update:count', n), { immediate: true })

const placeholder = 'data:image/svg+xml,' + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect fill="#e2e8f0" width="100" height="100"/></svg>'
)

function toggle() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    loadWishlist()
    window.dispatchEvent(new CustomEvent('floating-panel-open', { detail: 'wishlist' }))
  }
}

function close() {
  isOpen.value = false
  showSubmitForm.value = false
}

function onOtherPanelOpen(e) {
  if (e.detail !== 'wishlist') {
    isOpen.value = false
    showSubmitForm.value = false
  }
}

function onWishlistUpdated() {
  loadWishlist()
}

function openSubmitForm() {
  const u = authState.user
  Object.assign(submitForm, {
    contact_name: u?.username || '',
    email: u?.email || '',
    company_name: u?.company_name || '',
    phone: u?.phone || '',
    message: '',
    source: u?.source || ''
  })
  showSubmitForm.value = true
}

defineExpose({ toggle })

onMounted(async () => {
  window.addEventListener('floating-panel-open', onOtherPanelOpen)
  window.addEventListener('wishlist-updated', onWishlistUpdated)
  await loadWishlist()
})
onUnmounted(() => {
  window.removeEventListener('floating-panel-open', onOtherPanelOpen)
  window.removeEventListener('wishlist-updated', onWishlistUpdated)
})

async function loadWishlist() {
  try {
    const res = await api.get('/wishlist')
    items.value = res.data || []
  } catch (e) {
    console.error('Failed to load wishlist:', e)
  }
}

async function changeQty(item, delta) {
  const newQty = item.quantity + delta
  if (newQty < 1) return
  try {
    await api.put(`/wishlist/${item.id}`, { quantity: newQty })
    item.quantity = newQty
  } catch (e) {
    ElMessage.error('Failed to update quantity')
  }
}

async function removeItem(id) {
  try {
    await api.delete(`/wishlist/${id}`)
    items.value = items.value.filter(i => i.id !== id)
  } catch (e) {
    ElMessage.error('Failed to remove item')
  }
}

async function clearAll() {
  if (!confirm(t('wishlist.confirmClear'))) return
  try {
    await api.post('/wishlist/clear')
    items.value = []
  } catch (e) {
    ElMessage.error('Failed to clear wishlist')
  }
}

async function submitWishlist() {
  submitting.value = true
  try {
    await api.post('/wishlist/submit', { ...submitForm })
    ElMessage.success(t('product.inquire.success'))
    items.value = []
    showSubmitForm.value = false
    isOpen.value = false
    Object.assign(submitForm, { contact_name: '', email: '', company_name: '', phone: '', message: '', source: '' })
  } catch (e) {
    ElMessage.error(e.response?.data?.error || 'Failed to submit inquiry')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.wishlist-panel {
  position: fixed;
  bottom: 84px;
  right: 24px;
  z-index: 999;
  width: 320px;
  background: var(--surface, #fff);
  border: 1px solid var(--border, #ddd);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,.15);
  display: flex;
  flex-direction: column;
  max-height: 480px;
  overflow: hidden;
}
[dir="rtl"] .wishlist-panel { right: auto; left: 24px; }

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border, #eee);
}
.panel-header h3 { margin: 0; font-size: 15px; font-weight: 700; }
.panel-close {
  background: none; border: none; font-size: 18px;
  cursor: pointer; color: #999; line-height: 1;
}

.wishlist-empty {
  padding: 36px 16px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

.wishlist-items { flex: 1; overflow-y: auto; padding: 8px; }

.wishlist-item {
  display: flex; gap: 10px; padding: 8px;
  border-bottom: 1px solid var(--border, #eee);
}
.wishlist-item img {
  width: 56px; height: 56px; object-fit: cover; border-radius: 4px;
}
.item-info { flex: 1; display: flex; flex-direction: column; }
.item-info h4 {
  margin: 0; font-size: 13px; font-weight: 600; line-height: 1.3;
  display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden;
}
.qty-row { display: flex; align-items: center; gap: 6px; margin-top: 6px; }
.qty-btn {
  width: 24px; height: 24px; border-radius: 4px; border: 1px solid #ddd;
  background: #fff; font-size: 14px; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; justify-content: center; color: #333;
}
.qty-btn:hover { background: #f0f0f0; }
.qty-val { font-size: 13px; font-weight: 600; min-width: 20px; text-align: center; }
.btn-remove {
  background: none; border: 1px solid #ddd; color: #999;
  width: 24px; height: 24px; border-radius: 4px; font-size: 12px;
  cursor: pointer; margin-left: auto;
  display: flex; align-items: center; justify-content: center;
}
.btn-remove:hover { background: #fee; color: #e55; border-color: #e55; }

.wishlist-actions {
  display: flex; gap: 8px; padding: 10px 16px;
  border-top: 1px solid var(--border, #eee);
}
.wishlist-actions button { flex: 1; }

.wishlist-submit-form {
  border-top: 1px solid var(--border, #eee);
  padding: 12px 16px;
}
.submit-form-header {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 10px;
}
.submit-form-header h4 { margin: 0; font-size: 14px; font-weight: 600; }
.submit-form { display: flex; flex-direction: column; gap: 8px; }
.submit-form input,
.submit-form textarea,
.submit-form .source-select {
  border: 1px solid #ddd; border-radius: 6px;
  padding: 8px 10px; font-size: 13px;
  font-family: inherit; outline: none;
  width: 100%; box-sizing: border-box;
  background: var(--surface, #fff); color: var(--text, #333);
}
.submit-form input:focus,
.submit-form textarea:focus,
.submit-form .source-select:focus { border-color: var(--primary, #409eff); }

.slide-enter-active, .slide-leave-active { transition: all .25s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateX(20px); }
</style>
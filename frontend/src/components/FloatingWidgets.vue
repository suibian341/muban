<template>
  <div v-if="visible" class="floating-widgets">
    <!-- WishList button (buyer only) -->
    <div v-if="showWishList" class="wishlist-toggle" @click="$emit('toggle-wishlist')">
      <span class="badge" v-if="wishlistCount">{{ wishlistCount }}</span>
      <svg viewBox="0 0 24 24" width="22" height="22" fill="white">
        <path d="M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49A1.003 1.003 0 0020 4H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z"/>
      </svg>
    </div>

    <!-- WhatsApp -->
    <a v-if="showWhatsApp" :href="`https://wa.me/${whatsapp}`" target="_blank" class="widget-btn whatsapp" :title="t('floating.whatsapp')">
      <svg viewBox="0 0 24 24" width="22" height="22" fill="white">
        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
      </svg>
    </a>

    <!-- WeChat -->
    <button v-if="showWeChat" class="widget-btn wechat" @click="toggleWechat" title="WeChat">
      <svg viewBox="0 0 1024 1024" width="24" height="24" fill="white">
        <path d="M690.1 377.4c5.9 0 11.8.2 17.6.5-24.4-128.7-158.3-227.1-313.4-227.1C209 150.8 57.7 284.2 57.7 446.5c0 93.3 49.9 170.1 133 228.2l-33.2 99.9 115.8-58c41.5 8.3 75 16.6 116.5 16.6 5.5 0 11-.2 16.4-.5-3.4-12.2-5.4-24.9-5.4-38 0-168.6 149.2-317.3 289.3-317.3zM485.2 325.5c25 0 41.6 16.6 41.6 41.6 0 25-16.6 41.6-41.6 41.6-24.9 0-49.9-16.6-49.9-41.6 0-25 25-41.6 49.9-41.6zM285.4 408.7c-24.9 0-49.9-16.6-49.9-41.6 0-25 25-41.6 49.9-41.6 25 0 41.6 16.6 41.6 41.6 0 25-16.6 41.6-41.6 41.6z"/>
        <path d="M955.3 612.9c0-133-133-241.5-282.6-241.5-158.3 0-290.9 108.5-290.9 241.5S514.4 854.4 672.7 854.4c33.2 0 66.5-8.3 99.8-16.6l91.5 49.9-24.9-83.2c66.4-49.9 116.2-116.5 116.2-191.6zM602.8 570.5c-16.6 0-33.2-16.6-33.2-33.2 0-16.6 16.6-33.2 33.2-33.2 25 0 41.6 16.6 41.6 33.2 0 16.6-16.6 33.2-41.6 33.2zm149.8 0c-16.6 0-33.2-16.6-33.2-33.2 0-16.6 16.6-33.2 33.2-33.2 25 0 41.6 16.6 41.6 33.2 0 16.6-16.6 33.2-41.6 33.2z"/>
      </svg>
    </button>

    <!-- WeChat QR panel -->
    <transition name="slide">
      <div v-if="showWechat" class="wechat-panel">
        <div class="panel-header">
          <span>WeChat</span>
          <button class="panel-close" @click="showWechat = false">✕</button>
        </div>
        <div class="wechat-content">
          <img :src="wechatQr" alt="WeChat QR Code" class="qr-code" />
          <p>{{ t('floating.wechatTip') }}</p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../store/auth'

defineProps({ wishlistCount: { type: Number, default: 0 } })
defineEmits(['toggle-wishlist'])

const { t } = useI18n()
const { state: authState } = useAuth()
const role = computed(() => authState.user?.role)
const userCountry = computed(() => authState.user?.country)

// Entire widget: hidden when not logged in or admin
const visible = computed(() => !!authState.user && role.value !== 'admin')
// WishList: buyer only
const showWishList = computed(() => role.value === 'buyer')
// WhatsApp: non-CN users
const showWhatsApp = computed(() => userCountry.value !== 'CN')
// WeChat: CN users or no country set
const showWeChat = computed(() => !userCountry.value || userCountry.value === 'CN')

const whatsapp = import.meta.env.VITE_WHATSAPP || '8619876475649'
const wechatQr = import.meta.env.VITE_WECHAT_QR || '/wechat-qr.jpg'
const showWechat = ref(false)

function toggleWechat() {
  showWechat.value = !showWechat.value
  if (showWechat.value) {
    window.dispatchEvent(new CustomEvent('floating-panel-open', { detail: 'wechat' }))
  }
}

function onOtherPanelOpen(e) {
  if (e.detail !== 'wechat') {
    showWechat.value = false
  }
}

onMounted(() => window.addEventListener('floating-panel-open', onOtherPanelOpen))
onUnmounted(() => window.removeEventListener('floating-panel-open', onOtherPanelOpen))
</script>

<style scoped>
.floating-widgets {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 998;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: flex-end;
  gap: 12px;
}
[dir="rtl"] .floating-widgets { right: auto; left: 24px; align-items: flex-start; }

.widget-btn {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  transition: all var(--transition-base);
  box-shadow: 0 4px 16px rgba(0,0,0,.15);
}
.widget-btn:hover { transform: scale(1.12); box-shadow: 0 6px 24px rgba(0,0,0,.2); }
.whatsapp { background: linear-gradient(135deg, #25d366, #128c7e); }
.wechat { background: linear-gradient(135deg, #09b83e, #07a032); }

.wishlist-toggle {
  position: relative;
  width: 52px;
  height: 52px;
  background: var(--gradient-primary);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(37,99,235,.3);
  transition: all var(--transition-base);
}
.wishlist-toggle:hover { transform: scale(1.12); box-shadow: 0 6px 24px rgba(37,99,235,.4); }
.badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #ff4444;
  color: #fff;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: bold;
  padding: 0 4px;
}

.wechat-panel {
  position: absolute;
  bottom: 0;
  right: 60px;
  width: 260px;
  background: var(--surface, #fff);
  border: 1px solid var(--border, #ddd);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,.15);
  overflow: hidden;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #09b83e;
  color: #fff;
  font-weight: 700;
  font-size: 14px;
}
.panel-close {
  background: none;
  border: none;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  line-height: 1;
}
.wechat-content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}
.qr-code {
  width: 160px;
  height: 160px;
  border: 1px solid var(--border, #ddd);
  border-radius: 8px;
}
.wechat-content p {
  font-size: 13px;
  color: var(--text-secondary, #999);
  text-align: center;
  margin: 0;
}

.slide-enter-active, .slide-leave-active { transition: all .25s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateX(20px); }
</style>

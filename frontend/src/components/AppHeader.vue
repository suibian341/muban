<template>
  <nav class="header-nav">
    <div class="nav-container">
      <div class="nav-glass rounded-2xl">
        <!-- Top gradient line -->
        <div class="nav-top-line"></div>

        <!-- Left: Logo -->
        <router-link to="/" class="logo">
          <span v-if="branding.brand_logo" class="logo-image-box">
            <img :src="branding.brand_logo" alt="Logo" class="logo-image" />
          </span>
          <span v-else class="logo-icon-box">
            <span class="logo-icon-inner">C</span>
          </span>
          <span class="logo-brand-col">
            <span class="future-gradient brand-name">{{ brandName }}</span>
            <span class="micro-tag">{{ brandDesc }}</span>
          </span>
        </router-link>

        <!-- Center: Nav links (desktop) -->
        <div class="nav-center">
          <router-link to="/" class="nav-link" exact>{{ t('nav.home') }}</router-link>
          <router-link to="/products" class="nav-link" exact>{{ t('nav.products') }}</router-link>
          <div
            v-for="cat in categories" :key="cat.id"
            class="nav-dropdown"
            @mouseenter="openCat = cat.id"
            @mouseleave="openCat = null"
          >
            <router-link
              :to="`/products?category_id=${cat.id}`"
              class="nav-link nav-dropdown-trigger"
              :class="{ active: isCatActive(cat) }"
            >
              {{ cat.icon }} {{ localCatName(cat) }}
              <span v-if="cat.children && cat.children.length" class="arrow">&#9662;</span>
            </router-link>
            <transition name="dropdown">
              <div v-if="openCat === cat.id && cat.children && cat.children.length" class="dropdown-menu">
                <router-link
                  v-for="child in cat.children" :key="child.id"
                  :to="`/products?category_id=${child.id}`"
                  class="dropdown-item"
                  :class="{ active: activeCatId === child.id }"
                  @click="openCat = null"
                >{{ localCatName(child) }}</router-link>
              </div>
            </transition>
          </div>
          <router-link v-if="clearanceEnabled" to="/clearance" class="nav-link clearance-link">{{ t('nav.clearance') }}</router-link>
        </div>

        <!-- Right: Actions -->
        <div class="header-actions">
          <LanguageSwitcher class="lang-btn" />
          <template v-if="authState.user">
            <router-link :to="dashboardPath" class="btn-dash">
              {{ t('nav.dashboard') }}
              <span v-if="unreadCount > 0" class="unread-dot">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
            </router-link>
            <el-button text style="color:#64748b" @click="logout">{{ t('nav.logout') }}</el-button>
            <span class="user-name">{{ authState.user.username }}</span>
          </template>
          <template v-else>
            <router-link to="/login" class="btn-gradient btn-cta">{{ t('nav.signIn') }}</router-link>
          </template>
        </div>

        <!-- Hamburger (mobile) -->
        <button class="hamburger" @click="mobileOpen = !mobileOpen" aria-label="Menu">
          <span></span><span></span><span></span>
        </button>
      </div>
    </div>
  </nav>

  <!-- Spacer -->
  <div class="header-spacer"></div>

  <!-- Mobile overlay -->
  <div class="nav-backdrop" v-if="mobileOpen" @click="mobileOpen = false"></div>
  <div class="mobile-nav" :class="{ open: mobileOpen }">
    <nav class="mobile-nav-inner">
      <router-link to="/" class="nav-link" exact @click="mobileOpen = false">{{ t('nav.home') }}</router-link>
      <router-link to="/products" class="nav-link" exact @click="mobileOpen = false">{{ t('nav.products') }}</router-link>
      <div
        v-for="cat in categories" :key="cat.id"
        class="nav-dropdown"
      >
        <router-link
          :to="`/products?category_id=${cat.id}`"
          class="nav-link nav-dropdown-trigger"
          :class="{ active: isCatActive(cat) }"
          @click="openCat = openCat === cat.id ? null : cat.id"
        >
          {{ cat.icon }} {{ localCatName(cat) }}
          <span v-if="cat.children && cat.children.length" class="arrow">&#9662;</span>
        </router-link>
        <div v-if="openCat === cat.id && cat.children && cat.children.length" class="mobile-dropdown-items">
          <router-link
            v-for="child in cat.children" :key="child.id"
            :to="`/products?category_id=${child.id}`"
            class="dropdown-item"
            :class="{ active: activeCatId === child.id }"
            @click="openCat = null; mobileOpen = false"
          >{{ localCatName(child) }}</router-link>
        </div>
      </div>
      <router-link v-if="clearanceEnabled" to="/clearance" class="nav-link clearance-link" @click="mobileOpen = false">{{ t('nav.clearance') }}</router-link>
    </nav>
    <div class="mobile-actions">
      <LanguageSwitcher />
      <template v-if="authState.user">
        <router-link :to="dashboardPath" class="btn-dash" @click="mobileOpen = false">
          {{ t('nav.dashboard') }}
          <span v-if="unreadCount > 0" class="unread-dot">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </router-link>
        <el-button text style="color:#64748b" @click="logout; mobileOpen = false">{{ t('nav.logout') }}</el-button>
      </template>
      <template v-else>
        <router-link to="/login" class="btn-gradient btn-cta" @click="mobileOpen = false">{{ t('nav.signIn') }}</router-link>
      </template>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useDisplay } from '../utils/display'
import { useAuth } from '../store/auth'
import { useSiteMode } from '../composables/useSiteMode'
import { useClearance } from '../composables/useClearance'
import { ElNotification } from 'element-plus'
import LanguageSwitcher from './LanguageSwitcher.vue'
import api from '../api'

const { t, locale } = useI18n()
const { localCatName } = useDisplay()
const router = useRouter()
const route = useRoute()
const { state: authState, logout: doLogout } = useAuth()
const { isB2B, loadSiteMode } = useSiteMode()
const { clearanceEnabled, loadClearanceStatus } = useClearance()
const categories = ref([])
const openCat = ref(null)
const unreadCount = ref(0)
const mobileOpen = ref(false)
const branding = ref({
  brand_logo: '',
  brand_name_zh: '', brand_name_en: '', brand_name_es: '', brand_name_ar: '', brand_name_ru: '',
  brand_desc_zh: '', brand_desc_en: '', brand_desc_es: '', brand_desc_ar: '', brand_desc_ru: ''
})
let pollTimer = null
let prevUnread = -1

const brandName = computed(() => {
  const key = `brand_name_${locale.value}`
  return branding.value[key] || branding.value.brand_name_zh || t('brand')
})

const brandDesc = computed(() => {
  const key = `brand_desc_${locale.value}`
  return branding.value[key] || branding.value.brand_desc_zh || 'PREMIUM SOURCING HUB'
})

watch(() => route.path, () => { mobileOpen.value = false })

const dashboardPath = computed(() => {
  const role = authState.user?.role
  if (role === 'dev') return '/dev'
  if (role === 'admin') return '/admin'
  if (role === 'buyer') return '/buyer'
  return '/factory'
})

const activeCatId = computed(() => {
  if (route.path === '/products' && route.query.category_id) {
    return Number(route.query.category_id)
  }
  return null
})

function isCatActive(cat) {
  if (!activeCatId.value) return false
  if (cat.id === activeCatId.value) return true
  if (cat.children) return cat.children.some(c => c.id === activeCatId.value)
  return false
}
async function loadCategories() {
  try {
    const { data } = await api.get('/categories')
    categories.value = data
  } catch (e) { console.error(e) }
  await loadClearanceStatus()
}

async function loadBranding() {
  try {
    const { data } = await api.get('/site-settings')
    for (const key of Object.keys(branding.value)) {
      if (data[key]) branding.value[key] = data[key]
    }
  } catch (e) {
    console.error('Failed to load branding:', e)
  }
}

function onCategoriesUpdated() { loadCategories() }

function onSiteModeChanged() {
  loadSiteMode()
}

function onBrandingUpdated() {
  loadBranding()
}

onMounted(async () => {
  await loadSiteMode()
  await loadCategories()
  await loadBranding()
  startPolling()
  window.addEventListener('categories-updated', onCategoriesUpdated)
  window.addEventListener('site-mode-changed', onSiteModeChanged)
  window.addEventListener('branding-updated', onBrandingUpdated)
})

onUnmounted(() => {
  stopPolling()
  window.removeEventListener('categories-updated', onCategoriesUpdated)
  window.removeEventListener('site-mode-changed', onSiteModeChanged)
  window.removeEventListener('branding-updated', onBrandingUpdated)
})

watch(() => authState.user, () => {
  stopPolling()
  unreadCount.value = 0
  prevUnread = -1
  startPolling()
})

function startPolling() {
  const role = authState.user?.role
  if (!role || role === 'factory') return
  fetchUnread(false)
  pollTimer = setInterval(() => fetchUnread(true), 8000)
}

function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}
async function fetchUnread(notify) {
  const role = authState.user?.role
  if (!role) return
  try {
    let endpoint = ''
    if (role === 'admin') endpoint = '/inquiries/admin/unread-count'
    else if (role === 'buyer') endpoint = '/buyer/unread-count'
    else return
    const { data } = await api.get(endpoint)
    const count = data.count || 0
    if (notify && count > prevUnread && prevUnread >= 0) {
      const target = role === 'admin' ? '/admin/inquiries' : '/buyer'
      ElNotification({
        title: t('inquiry.newMessage'),
        message: t('inquiry.newMessageDesc'),
        type: 'info',
        duration: 5000,
        onClick() { router.push(target) }
      })
    }
    prevUnread = count
    unreadCount.value = count
  } catch (e) { /* ignore */ }
}

function logout() {
  stopPolling()
  doLogout()
  router.push('/')
}
</script>
<style scoped>
/* ---- Header nav container ---- */
.header-nav {
  position: fixed;
  top: 0;
  width: 100%;
  z-index: 100;
  padding-top: 24px;
  pointer-events: none;
}
.nav-container {
  pointer-events: auto;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  overflow: visible;
}

/* ---- Glass pill ---- */
.nav-glass {
  position: relative;
  background: rgba(255, 255, 255, .85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 0.5px solid rgba(15, 23, 42, .08);
  box-shadow: 0 4px 20px -5px rgba(0, 71, 171, .05), inset 0 1px 0 0 rgba(255, 255, 255, .8);
  border-radius: 16px;
  padding: 14px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  overflow: visible;
}
.nav-top-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 0.5px;
  background: linear-gradient(90deg, transparent, rgba(0, 210, 255, .2), transparent);
  border-radius: 16px 16px 0 0;
}

/* ---- Spacer ---- */
.header-spacer {
  height: 96px;
}

/* ---- Logo ---- */
.logo {
  display: flex;
  align-items: center;
  gap: 14px;
  text-decoration: none;
  flex-shrink: 0;
}

.logo-image-box {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.logo-icon-box {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #00d2ff, #7000ff);
  border-radius: 12px;
  transform: rotate(45deg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.logo-icon-inner {
  transform: rotate(-45deg);
  color: #fff;
  font-size: 15px;
  font-weight: 900;
  line-height: 1;
}
.logo-brand-col {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.brand-name {
  font-size: 1.5rem;
  font-weight: 800;
  line-height: 1.1;
}
.micro-tag {
  font-size: 6px;
  text-transform: uppercase;
  letter-spacing: 0.3em;
  font-weight: 700;
  color: #94a3b8;
}

/* ---- Center nav links ---- */
.nav-center {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
  justify-content: center;
  min-width: 0;
}
.nav-link {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
  color: #64748b;
  padding: 8px 10px;
  border-radius: 9999px;
  transition: color 0.2s, background 0.2s;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 4px;
  text-decoration: none;
  flex-shrink: 0;
}

.nav-link:hover {
  color: #0F172A;
  background: rgba(15, 23, 42, .04);
}
.nav-link.active,
.nav-link.router-link-exact-active {
  color: #1d4ed8;
}
.nav-dropdown-trigger.router-link-active:not(.active),
.nav-dropdown-trigger.router-link-exact-active:not(.active) {
  background: none;
  color: #64748b;
  font-weight: 700;
}

/* ---- Dropdown ---- */
.nav-dropdown {
  position: relative;
}
.nav-dropdown-trigger {
  cursor: pointer;
}
.arrow {
  font-size: 10px;
  transition: transform 0.2s;
}
.nav-dropdown:hover .arrow {
  transform: rotate(180deg);
}
.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  min-width: 200px;
  background: rgba(255, 255, 255, .95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 20px;
  padding: 8px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, .08);
  border: 0.5px solid rgba(15, 23, 42, .05);
  z-index: 200;
}
/* Bridge the 8px gap so mouse doesn't leave */
.dropdown-menu::before {
  content: '';
  position: absolute;
  top: -8px;
  left: 0;
  right: 0;
  height: 8px;
}
.dropdown-item {
  display: block;
  padding: 9px 16px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #64748b;
  border-radius: 12px;
  transition: all 0.15s;
  white-space: nowrap;
  text-decoration: none;
}

.dropdown-item:hover,
.dropdown-item.active {
  background: rgba(29, 78, 216, .08);
  color: #1d4ed8;
}
.dropdown-enter-active { transition: all 0.2s ease; }
.dropdown-leave-active { transition: all 0.15s ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateX(-50%) translateY(-6px); }
.dropdown-enter-to, .dropdown-leave-from { opacity: 1; transform: translateX(-50%) translateY(0); }

/* ---- Header actions (right side) ---- */
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}
.lang-btn {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-weight: 700;
  color: #64748b;
}
.user-name {
  font-size: 10px;
  font-weight: 700;
  color: #0f172a;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.btn-dash {
  position: relative;
  padding: 8px 16px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #0f172a;
  border: 0.5px solid rgba(15, 23, 42, .12);
  transition: all 0.2s;
  text-decoration: none;
}
.btn-dash:hover {
  border-color: #1d4ed8;
  color: #1d4ed8;
}

.unread-dot {
  position: absolute;
  top: -6px;
  right: -8px;
  background: linear-gradient(135deg, #f97316, #ef4444);
  color: #fff;
  font-size: 9px;
  font-weight: 800;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  line-height: 1;
}

/* ---- CTA / Sign-in button ---- */
.btn-gradient.btn-cta {
  background: linear-gradient(90deg, #00d2ff, #7000ff);
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.15em;
  color: #fff;
  text-transform: uppercase;
  text-decoration: none;
  transition: all 0.2s;
  box-shadow: 0 8px 20px rgba(0, 71, 171, .1);
  white-space: nowrap;
  display: inline-block;
}
.btn-gradient.btn-cta:hover {
  box-shadow: 0 10px 28px rgba(0, 71, 171, .18);
  transform: translateY(-1px);
}

/* ---- Clearance link ---- */
.clearance-link {
  color: #ef4444 !important;
}
.clearance-link:hover {
  color: #dc2626 !important;
  background: rgba(239, 68, 68, .06);
}

/* ---- Hamburger ---- */
.hamburger {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  width: 36px;
  height: 36px;
  padding: 6px;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  border-radius: 10px;
  transition: background 0.2s;
  flex-shrink: 0;
}

.hamburger:hover {
  background: rgba(0, 0, 0, .04);
}
.hamburger span {
  display: block;
  width: 20px;
  height: 2px;
  background: #374151;
  border-radius: 2px;
  transition: transform 0.3s, opacity 0.3s;
}

/* ---- Mobile nav backdrop ---- */
.nav-backdrop {
  display: none;
}

/* ---- Mobile nav panel ---- */
.mobile-nav {
  display: none;
}

/* ---- Mobile responsive (max-width: 1200px) ---- */
@media (max-width: 1200px) {
  .nav-container {
    padding: 0 12px;
  }
  .nav-glass {
    padding: 12px 20px;
  }
  .hamburger {
    display: flex;
  }
  .nav-center,
  .header-actions {
    display: none;
  }
  .nav-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 199;
    background: rgba(0, 0, 0, .35);
    backdrop-filter: blur(2px);
  }
  .mobile-nav {
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    width: 300px;
    background: rgba(255, 255, 255, .95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    z-index: 200;
    padding: 28px 20px;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    overflow-y: auto;
    box-shadow: -4px 0 32px rgba(0, 0, 0, .1);
    border-left: 0.5px solid rgba(15, 23, 42, .06);
  }

  .mobile-nav.open {
    transform: translateX(0);
  }
  .mobile-nav-inner {
    display: flex;
    flex-direction: column;
    gap: 2px;
    border-bottom: 0.5px solid rgba(15, 23, 42, .08);
    padding-bottom: 20px;
    margin-bottom: 20px;
  }
  .mobile-nav .nav-link {
    padding: 14px 16px;
    border-radius: 12px;
    font-size: 10px;
    letter-spacing: 0.25em;
    justify-content: flex-start;
  }
  .mobile-nav .nav-dropdown {
    position: static;
  }
  .mobile-dropdown-items {
    padding: 0 0 0 16px;
  }
  .mobile-dropdown-items .dropdown-item {
    padding: 12px 16px;
    font-size: 10px;
  }
  .mobile-actions {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  .mobile-actions .btn-gradient.btn-cta {
    text-align: center;
    display: block;
  }
  .mobile-actions .btn-dash {
    text-align: center;
    display: block;
  }
}
</style>
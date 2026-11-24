<template>
  <footer class="site-footer">
    <!-- Industrial Grid Overlay -->
    <div class="grid-overlay"></div>

    <!-- Main Footer -->
    <div class="footer-main">
      <div class="container footer-grid">
        <!-- Col 1-2: Brand (spans 2 columns) -->
        <div class="footer-brand">
          <div class="brand-logo">
            <template v-if="branding.brand_logo">
              <div class="brand-image-box">
                <img :src="branding.brand_logo" alt="Logo" />
              </div>
            </template>
            <template v-else>
              <div class="brand-icon">
                <div class="brand-icon-inner"></div>
              </div>
            </template>
            <div class="brand-text">
              <span class="brand-name">{{ brandName }}</span>
              <span class="brand-tag">{{ brandDesc }}</span>
            </div>
          </div>
          <p class="footer-desc">{{ brandDesc }}</p>
        </div>

        <!-- Col 3: Categories (from category management) -->
        <div class="footer-links">
          <h4 class="footer-heading">CORE MODULES</h4>
          <router-link
            v-for="cat in categories"
            :key="cat.id"
            :to="`/products?category_id=${cat.id}`"
          >{{ localCatName(cat) }}</router-link>
        </div>

        <!-- Col 4: Operations -->
        <div class="footer-links">
          <h4 class="footer-heading">OPERATIONS</h4>
          <router-link to="/faq">{{ t('footer.faq') }}</router-link>
          <router-link to="/shipping">{{ t('footer.shipping') }}</router-link>
          <router-link to="/terms">{{ t('footer.terms') }}</router-link>
        </div>

        <!-- Col 5: Company -->
        <div class="footer-links">
          <h4 class="footer-heading">COMPANY</h4>
          <router-link to="/about">{{ t('footer.aboutUs') }}</router-link>
          <router-link v-if="isB2B" to="/register">{{ t('footer.factoryReg') }}</router-link>
        </div>
      </div>
    </div>

    <!-- Bottom Bar -->
    <div class="footer-bottom">
      <div class="container bottom-inner">
        <span>{{ footerConfig.copyright || t('footer.copyright') }}</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDisplay } from '../utils/display'
import { useSiteMode } from '../composables/useSiteMode'
import api from '../api'

const { t, locale } = useI18n()
const { localCatName } = useDisplay()
const { isB2B, loadSiteMode } = useSiteMode()

const categories = ref([])
const branding = ref({
  brand_logo: '',
  brand_name_zh: '', brand_name_en: '', brand_name_es: '', brand_name_ar: '', brand_name_ru: '',
  brand_desc_zh: '', brand_desc_en: '', brand_desc_es: '', brand_desc_ar: '', brand_desc_ru: ''
})

const footerData = ref({
  faq_zh: '', faq_en: '', faq_es: '', faq_ar: '', faq_ru: '',
  shipping_zh: '', shipping_en: '', shipping_es: '', shipping_ar: '', shipping_ru: '',
  terms_zh: '', terms_en: '', terms_es: '', terms_ar: '', terms_ru: '',
  about_zh: '', about_en: '', about_es: '', about_ar: '', about_ru: ''
})

const footerConfig = ref({
  company_name: '',
  company_info: '',
  links: [],
  copyright: ''
})

const brandName = computed(() => {
  const key = `brand_name_${locale.value}`
  return branding.value[key] || branding.value.brand_name_zh || t('brand')
})

const brandDesc = computed(() => {
  const key = `brand_desc_${locale.value}`
  return branding.value[key] || branding.value.brand_desc_zh || 'PREMIUM SOURCING HUB'
})

async function loadCategories() {
  try {
    const { data } = await api.get('/categories')
    categories.value = data
  } catch (e) {
    console.error('Failed to load categories:', e)
  }
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

async function loadFooterData() {
  try {
    const { data } = await api.get('/site-settings')
    for (const key of Object.keys(footerData.value)) {
      if (data[key]) footerData.value[key] = data[key]
    }
  } catch (e) {
    console.error('Failed to load footer data:', e)
  }
}

function onFooterUpdated() { loadFooterData() }
function onBrandingUpdated() { loadBranding() }
function onCategoriesUpdated() { loadCategories() }

onMounted(async () => {
  await loadSiteMode()
  await Promise.all([loadCategories(), loadBranding(), loadFooterData()])
  try {
    const { data } = await api.get('/site-settings')
    if (data.footer_copyright) {
      footerConfig.value.copyright = data.footer_copyright
    }
  } catch (e) {
    console.error('Failed to load footer config:', e)
  }

  window.addEventListener('footer-updated', onFooterUpdated)
  window.addEventListener('branding-updated', onBrandingUpdated)
  window.addEventListener('categories-updated', onCategoriesUpdated)
})

onUnmounted(() => {
  window.removeEventListener('footer-updated', onFooterUpdated)
  window.removeEventListener('branding-updated', onBrandingUpdated)
  window.removeEventListener('categories-updated', onCategoriesUpdated)
})
</script>

<style scoped>
.site-footer {
  background: #0D1B2A;
  color: #ffffff;
  padding: 128px 0 64px;
  position: relative;
  overflow: hidden;
}

/* Industrial Grid Overlay */
.grid-overlay {
  position: absolute;
  inset: 0;
  opacity: 0.05;
  background-image:
    linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
}
/* Container */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Footer Main Grid */
.footer-main {
  position: relative;
  z-index: 1;
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 64px;
}

/* Brand Column */
.footer-brand {
  display: flex;
  flex-direction: column;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.brand-image-box {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-image-box img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.brand-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #00d2ff, #7000ff);
  border-radius: 8px;
  transform: rotate(45deg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-icon-inner {
  width: 16px;
  height: 16px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-name {
  font-size: 1.875rem;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.1;
}

.brand-tag {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: #94a3b8;
}
.footer-desc {
  font-size: 14px;
  color: #94a3b8;
  line-height: 1.7;
  margin: 0 0 28px;
}

/* Social Icons */
.social-icons {
  display: flex;
  gap: 12px;
}

.social-square {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  border: 1px solid rgba(100, 116, 139, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  text-decoration: none;
  transition: all 0.3s ease;
}

.social-square .material-symbols-outlined {
  font-size: 20px;
}

.social-square:hover {
  background: #ffffff;
  color: #0D1B2A;
  border-color: #ffffff;
}

/* Link Columns */
.footer-links {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.footer-heading {
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.5em;
  color: #1d4ed8;
  margin: 0 0 40px;
}
.footer-links a {
  font-size: 14px;
  font-weight: 500;
  color: #94a3b8;
  text-decoration: none;
  transition: all 0.6s;
}

.footer-links a:hover {
  color: #ffffff;
}

/* Bottom Bar */
.footer-bottom {
  border-top: 1px solid rgba(100, 116, 139, 0.3);
  padding-top: 32px;
  margin-top: 96px;
  position: relative;
  z-index: 1;
}

.bottom-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.bottom-inner span,
.bottom-links a {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: #64748b;
}

.bottom-links {
  display: flex;
  gap: 24px;
}

.bottom-links a {
  text-decoration: none;
  transition: all 0.6s;
}

.bottom-links a:hover {
  color: #ffffff;
}

/* Responsive: 1024px - 2 columns */
@media (max-width: 1024px) {
  .footer-grid {
    grid-template-columns: 1fr 1fr;
    gap: 48px;
  }

  .footer-brand {
    grid-column: span 2;
  }

  .site-footer {
    padding: 80px 0 48px;
  }
}

/* Responsive: 768px - 1 column */
@media (max-width: 768px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 40px;
  }

  .footer-brand {
    grid-column: span 1;
  }

  .site-footer {
    padding: 64px 0 32px;
  }

  .footer-heading {
    margin-bottom: 24px;
  }

  .footer-bottom {
    margin-top: 48px;
  }

  .bottom-inner {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .bottom-links {
    justify-content: center;
  }
}
</style>

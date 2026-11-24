<template>
  <div class="detail-page" v-if="product">
    <div class="container">
      <el-breadcrumb separator="/" class="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">{{ t('nav.home') }}</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/products' }">{{ t('nav.products') }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ localTitle(product) }}</el-breadcrumb-item>
      </el-breadcrumb>

      <div class="detail-layout fade-up">
        <div class="gallery">
          <div class="main-image" @mouseenter="pauseGallery" @mouseleave="resumeGallery"><img :src="currentImage" :alt="localTitle(product)" /></div>
          <div class="thumbs" v-if="product.images.length > 1">
            <div v-for="(img, i) in product.images" :key="i"
              class="thumb" :class="{ active: i === activeImg }" @click="activeImg = i; resetGalleryTimer()">
              <img :src="img" />
            </div>
          </div>
          <div v-if="product.video_url" class="video-link">
            <el-icon><VideoPlay /></el-icon>
            <a :href="product.video_url" target="_blank">{{ t('product.detail.watchVideo') }}</a>
          </div>
        </div>
        <div class="info">
          <div class="tags-row" v-if="product.is_featured || product.is_new || product.is_clearance">
            <span v-if="product.is_featured" class="tag tag-featured">★ {{ t('product.detail.tagFeatured') }}</span>
            <span v-if="product.is_new" class="tag tag-new">{{ t('product.detail.tagNew') }}</span>
            <span v-if="product.is_clearance" class="tag tag-clearance">{{ t('product.detail.tagClearance') }}</span>
          </div>
          <h1>{{ localTitle(product) }}</h1>

          <div class="meta-row">
            <div class="meta-box">
              <span class="meta-label">{{ t('product.moq') }}</span>
              <span class="meta-value">{{ product.moq }} {{ t('product.pcs') }}</span>
            </div>
            <div class="meta-box" v-if="product.lead_time">
              <span class="meta-label">{{ t('product.leadTime') }}</span>
              <span class="meta-value">{{ product.lead_time }}</span>
            </div>
            <div class="meta-box" v-if="localCatName(product)">
              <span class="meta-label">{{ t('product.category') }}</span>
              <span class="meta-value">{{ localCatName(product) }}</span>
            </div>
          </div>

          <div class="info-grid">
            <div class="info-item" v-if="product.certification">
              <span class="info-label">{{ t('product.detail.certification') }}</span>
              <span class="info-val">{{ product.certification }}</span>
            </div>
            <div class="info-item" v-if="product.stock_quantity != null">
              <span class="info-label">{{ t('product.detail.stock') }}</span>
              <span class="info-val">{{ product.stock_quantity }} {{ t('product.pcs') }}</span>
            </div>
            <div class="info-item" v-if="product.created_at">
              <span class="info-label">{{ t('product.detail.published') }}</span>
              <span class="info-val">{{ formatDate(product.created_at) }}</span>
            </div>
          </div>

          <div class="price-hint" v-if="isB2B">
            <el-icon><ChatDotSquare /></el-icon>
            <span>{{ t('product.detail.contactPrice') }}</span>
          </div>
          <div class="price-display" v-else-if="isB2C && product.base_price">
            <div class="price-label">{{ t('product.price') }}</div>
            <div class="price-value">{{ product.price_unit || 'USD' }} {{ product.base_price }}</div>
          </div>

          <div class="section-block" v-if="localDesc(product)">
            <h3>{{ t('product.detail.desc') }}</h3>
            <p class="desc-text">{{ localDesc(product) }}</p>
          </div>
          <div class="section-block" v-if="Object.keys(product.specs).length">
            <h3>{{ t('product.detail.specs') }}</h3>
            <table class="specs-table">
              <tr v-for="(v, k) in product.specs" :key="k">
                <td class="spec-key">{{ k }}</td><td>{{ v }}</td>
              </tr>
            </table>
          </div>
          <div class="section-block" v-if="localPackaging(product)">
            <h3>{{ t('product.detail.packaging') }}</h3>
            <p>{{ localPackaging(product) }}</p>
          </div>
          <div class="section-block" v-if="localCustomization(product)">
            <h3>{{ t('product.detail.customization') }}</h3>
            <p>{{ localCustomization(product) }}</p>
          </div>
        </div>
      </div>

      <!-- Poster Images -->
      <div v-if="product.poster_images && product.poster_images.length" class="poster-section fade-up fade-up-d1">
        <img v-for="(img, i) in product.poster_images" :key="i" :src="img" class="poster-img" />
      </div>

      <div v-if="!hideActions" class="inquiry-section fade-up fade-up-d2">
        <div class="inquiry-card">
          <h2>{{ t('product.inquire.title') }}</h2>
          <p class="inquiry-sub">{{ t('product.inquire.sub') }}</p>
          <form class="inquiry-form" @submit.prevent="submitInquiry">
            <div class="form-row">
              <input v-model="form.contact_name" :placeholder="t('product.inquire.name')" required />
              <input v-model="form.email" :placeholder="t('product.inquire.email')" type="email" required />
            </div>
            <div class="form-row">
              <input v-model="form.company_name" :placeholder="t('product.inquire.company')" />
              <input v-model="form.phone" :placeholder="t('product.inquire.phone')" />
            </div>
            <input v-model.number="form.quantity" :placeholder="t('product.inquire.qty')" type="number" min="1" />
            <el-select v-model="form.source" :placeholder="t('home.howFind')" clearable style="width:100%">
              <el-option value="tiktok" label="TikTok" />
              <el-option value="facebook" label="Facebook" />
              <el-option value="google" label="Google" />
              <el-option value="instagram" label="Instagram" />
              <el-option value="referral" :label="t('home.referralLabel')" />
              <el-option value="other" :label="t('home.otherLabel')" />
            </el-select>
            <textarea v-model="form.message" :placeholder="t('product.inquire.msg')" rows="4" required></textarea>
            <el-button type="primary" native-type="submit" :loading="sending" size="large" style="width:100%;font-weight:700">
              {{ sending ? t('product.inquire.sending') : t('product.inquire.send') }}
            </el-button>
          </form>
          <p v-if="inquirySent" class="success-msg">{{ t('product.inquire.success') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useDisplay } from '../utils/display'
import { useAuth } from '../store/auth'
import { useSiteMode } from '../composables/useSiteMode'
import { ElMessage } from 'element-plus'
import api from '../api'

const { t } = useI18n()
const isZh = localStorage.getItem('lang') === 'zh' || !localStorage.getItem('lang')
const { localTitle, localDesc, localPackaging, localCustomization, localCatName } = useDisplay()
const { state: authState } = useAuth()
const { isB2C, isB2B, loadSiteMode } = useSiteMode()
const hideActions = computed(() => {
  const role = authState.user?.role
  return role !== 'buyer'
})
const route = useRoute()
const product = ref(null)
const activeImg = ref(0)
let galleryTimer = null
const sending = ref(false)
const inquirySent = ref(false)
const u = authState.user
const form = reactive({
  contact_name: u?.username || '',
  email: u?.email || '',
  company_name: u?.company_name || '',
  phone: u?.phone || '',
  quantity: null,
  message: '',
  source: u?.source || ''
})

const currentImage = computed(() => {
  if (!product.value?.images?.length) return ''
  return product.value.images[activeImg.value] || product.value.images[0]
})

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString()
}

onMounted(async () => {
  await loadSiteMode()
  const { data } = await api.get(`/products/${route.params.id}`)
  product.value = data
  // Auto-carousel for multiple images
  if (data.images && data.images.length > 1) {
    galleryTimer = setInterval(() => {
      activeImg.value = (activeImg.value + 1) % data.images.length
    }, 3000)
  }
})

onUnmounted(() => { if (galleryTimer) clearInterval(galleryTimer) })

function resetGalleryTimer() {
  if (galleryTimer) clearInterval(galleryTimer)
  if (product.value?.images?.length > 1) {
    galleryTimer = setInterval(() => {
      activeImg.value = (activeImg.value + 1) % product.value.images.length
    }, 3000)
  }
}
function pauseGallery() {
  if (galleryTimer) { clearInterval(galleryTimer); galleryTimer = null }
}
function resumeGallery() {
  if (product.value?.images?.length > 1) {
    galleryTimer = setInterval(() => {
      activeImg.value = (activeImg.value + 1) % product.value.images.length
    }, 3000)
  }
}

async function submitInquiry() {
  sending.value = true
  try {
    await api.post('/inquiries', { ...form, product_id: product.value.id })
    inquirySent.value = true
    ElMessage.success(t('product.inquire.success'))
    Object.assign(form, { contact_name: '', email: '', company_name: '', phone: '', quantity: null, message: '' })
  } catch (e) { ElMessage.error('Failed') } finally { sending.value = false }
}

</script>

<style scoped>
.breadcrumb { padding: 28px 0; font-family: 'Manrope', sans-serif; }
.detail-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 56px; margin-bottom: 56px; }
.main-image {
  aspect-ratio: 3/4; border-radius: 32px; overflow: hidden;
  background: #f8fafc; border: 0.5px solid rgba(15,23,42,.05);
  box-shadow: 0 10px 25px -5px rgba(0,0,0,.02);
}
.main-image img { width: 100%; height: 100%; object-fit: cover; transition: all .7s cubic-bezier(.4,0,.2,1); }
.main-image:hover img { transform: scale(1.06); }
.thumbs { display: flex; gap: 10px; margin-top: 14px; }
.thumb {
  width: 68px; height: 68px; border-radius: 16px; overflow: hidden;
  border: 0.5px solid rgba(15,23,42,.05); cursor: pointer; transition: all .7s cubic-bezier(.4,0,.2,1);
}
.thumb.active, .thumb:hover { border-color: #1d4ed8; box-shadow: 0 0 0 2px rgba(29,78,216,.2); }
.thumb img { width: 100%; height: 100%; object-fit: cover; }
.video-link { margin-top: 14px; display: flex; align-items: center; gap: 6px; font-size: 14px; font-family: 'Manrope', sans-serif; }
.video-link a { color: #1d4ed8; font-weight: 600; transition: all .7s cubic-bezier(.4,0,.2,1); }

.tags-row { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }
.tag { font-size: 9px; font-weight: 900; font-family: 'Space Grotesk', sans-serif; padding: 5px 14px; border-radius: 10px; color: #fff; letter-spacing: 0.1em; text-transform: uppercase; }
.tag-featured { background: #f59e0b; }
.tag-new { background: #16a34a; }
.tag-clearance { background: #dc2626; }

.info h1 { font-size: 28px; font-weight: 800; margin-bottom: 22px; line-height: 1.3; color: #0F172A; font-family: 'Space Grotesk', sans-serif; }
.meta-row { display: flex; gap: 16px; margin-bottom: 22px; flex-wrap: wrap; }
.meta-box { background: #f8fafc; border: 0.5px solid rgba(15,23,42,.05); border-radius: 20px; padding: 16px 20px; }
.meta-label { display: block; font-size: 9px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.14em; font-weight: 900; font-family: 'Space Grotesk', sans-serif; }
.meta-value { font-size: 16px; font-weight: 700; margin-top: 4px; color: #0F172A; font-family: 'Manrope', sans-serif; }
.price-value { color: #10b981; }

.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 22px; }
.info-item { display: flex; justify-content: space-between; padding: 12px 16px; background: #f8fafc; border-radius: 16px; font-size: 14px; font-family: 'Manrope', sans-serif; border: 0.5px solid rgba(15,23,42,.05); }
.info-label { color: #94a3b8; }
.info-val { font-weight: 600; color: #0F172A; }

.price-hint {
  display: flex; align-items: center; gap: 8px;
  background: rgba(29,78,216,.04); border: 0.5px solid rgba(29,78,216,.12);
  border-radius: 16px; padding: 16px 20px;
  color: #1d4ed8; font-weight: 700; font-size: 14px; margin-bottom: 28px;
  font-family: 'Manrope', sans-serif;
}
.price-display {
  background: linear-gradient(135deg, rgba(16,185,129,.08) 0%, rgba(5,150,105,.08) 100%);
  border: 0.5px solid rgba(16,185,129,.2);
  border-radius: 16px; padding: 16px 20px;
  margin-bottom: 28px;
}
.price-label {
  font-size: 11px; color: #059669; text-transform: uppercase;
  letter-spacing: 0.1em; font-weight: 900; margin-bottom: 6px;
  font-family: 'Space Grotesk', sans-serif;
}
.price-value {
  font-size: 28px; font-weight: 800; color: #10b981;
  font-family: 'Space Grotesk', sans-serif;
}
.section-block { margin-bottom: 22px; }
.section-block h3 { font-size: 15px; font-weight: 700; margin-bottom: 10px; color: #0F172A; font-family: 'Space Grotesk', sans-serif; }
.section-block p { font-size: 14px; line-height: 1.7; color: #64748b; font-family: 'Manrope', sans-serif; }
.desc-text { white-space: pre-line; }
.specs-table { width: 100%; border-collapse: collapse; }
.specs-table tr:nth-child(even) { background: #f8fafc; }
.specs-table td { padding: 12px 16px; border: none; font-size: 14px; font-family: 'Manrope', sans-serif; }
.spec-key { color: #94a3b8; width: 40%; }
.poster-section { margin-bottom: 48px; display: flex; flex-direction: column; gap: 0; }
.poster-img { width: 100%; display: block; }
.inquiry-section { max-width: 720px; margin: 0 auto; }
.inquiry-card { background: #fff; border: 0.5px solid rgba(15,23,42,.05); border-radius: 32px; padding: 48px; box-shadow: 0 10px 25px -5px rgba(0,0,0,.02); }
.inquiry-card h2 { font-size: 24px; font-weight: 800; margin-bottom: 8px; font-family: 'Space Grotesk', sans-serif; background: linear-gradient(90deg, #00d2ff, #7000ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.inquiry-sub { color: #64748b; font-size: 14px; margin-bottom: 28px; font-family: 'Manrope', sans-serif; }
.inquiry-form { display: flex; flex-direction: column; gap: 14px; }
.form-row { display: flex; gap: 14px; }
.inquiry-form input, .inquiry-form textarea, .inquiry-form .source-select {
  flex: 1; background: #f8fafc; border: 0.5px solid rgba(15,23,42,.05);
  border-radius: 12px; padding: 14px 16px;
  color: #0F172A; font-size: 14px; font-family: 'Manrope', sans-serif;
  outline: none; transition: all .7s cubic-bezier(.4,0,.2,1); resize: none;
}
.inquiry-form input:focus, .inquiry-form textarea:focus, .inquiry-form .source-select:focus { border-color: #1d4ed8; box-shadow: 0 0 0 2px rgba(29,78,216,.2); }
.success-msg { color: #10b981; font-weight: 600; margin-top: 16px; font-size: 14px; font-family: 'Manrope', sans-serif; }

@media (max-width: 768px) {
  .detail-layout { grid-template-columns: 1fr; gap: 32px; }
  .main-image { aspect-ratio: 1 / 1; }
  .meta-row { flex-direction: column; }
  .info-grid { grid-template-columns: 1fr; }
  .form-row { flex-direction: column; }
  .inquiry-card { padding: 28px 18px; border-radius: 24px; }
}
</style>

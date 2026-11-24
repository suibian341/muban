<template>
  <div class="home">
    <!-- 1. Hero — Full-screen industrial split -->
    <section class="hero-section">
      <div class="hero-bg-photo">
        <div class="hero-bg-overlay"></div>
        <img :src="heroBgImage" alt="" class="hero-bg-img" />
      </div>
      <div class="hero-bg-image"></div>
      <div class="gl-container hero-grid">
        <div class="hero-left">
          <div class="glass-badge anim-slide-up">
            <span class="pulse-dot"></span>
            <span class="micro-tag">{{ t('home.heroBadge') }}</span>
          </div>
          <h1 class="hero-title anim-slide-up anim-d1">
            <template v-for="(part, i) in siteTitles.hero" :key="i"><span v-if="part.gradient" class="future-gradient">{{ part.text }}</span><template v-else>{{ part.text }}</template><br v-if="i < siteTitles.hero.length - 1" /></template>
          </h1>
          <p class="hero-desc anim-slide-up anim-d2">{{ siteTitles.heroDesc.map(p => p.text).join('') }}</p>
          <div class="hero-actions anim-slide-up anim-d3">
            <router-link to="/products" class="btn-gradient-primary">{{ t('home.heroExplore') }}</router-link>
            <router-link v-if="isB2B" to="/register" class="btn-glass-secondary">{{ t('home.heroQuote') }}</router-link>
          </div>
        </div>
        <div class="hero-right anim-slide-up anim-d3">
          <div v-if="bannerProducts.length" class="hero-card-wrap">
            <el-carousel height="480px" :interval="4000" arrow="hover">
              <el-carousel-item v-for="p in bannerProducts" :key="p.id">
                <router-link :to="`/products/${p.id}`" class="banner-slide">
                  <img :src="p.images?.[0]" :alt="localTitle(p)" class="banner-img" />
                  <div class="banner-overlay">
                    <div class="banner-tags">
                      <span v-if="p.is_featured" class="banner-tag hot-tag">{{ t('product.hotTag') }}</span>
                      <span v-if="p.is_new" class="banner-tag new-tag">{{ t('product.newTag') }}</span>
                      <span v-if="p.is_clearance && clearanceEnabled" class="banner-tag clearance-tag">{{ t('clearance.title') }}</span>
                    </div>
                    <h3>{{ localTitle(p) }}</h3>
                    <p>MOQ: {{ p.moq }} {{ t('product.pcs') }}</p>
                  </div>
                </router-link>
              </el-carousel-item>
            </el-carousel>
            <div class="hero-stat-overlay">
              <span class="micro-tag">{{ t('home.heroQualityLabel') }}</span>
              <span class="stat-bold">{{ t('home.heroQuality') }}</span>
              <div class="industrial-line"></div>
              <span class="micro-tag" style="color:#00d2ff">ISO 9001</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 2. Categories — Industrial grid -->
    <section class="section-categories">
      <div class="industrial-grid-overlay"></div>
      <div class="gl-container">
        <div class="section-header-row">
          <div>
            <p class="eyebrow-cyan">{{ siteEyebrows.cat }}</p>
            <h2 class="section-title-xl"><template v-for="(p,i) in siteTitles.cat" :key="i">{{ i?' ':'' }}<span v-if="p.gradient" class="future-gradient">{{ p.text }}</span><template v-else>{{ p.text }}</template></template></h2>
          </div>
          <p class="mono-stat">{{ categories.length }} {{ t('home.catModules') }}</p>
        </div>
        <div class="cat-grid">
          <router-link v-for="(cat, idx) in categories.slice(0, 6)" :key="cat.id" :to="`/products?category_id=${cat.id}`" class="cat-card">
            <div class="cat-image-area">
              <div class="cat-icon-placeholder" :class="['color-' + (idx % 3)]">{{ cat.icon || '📦' }}</div>
              <span class="cat-tag micro-tag">{{ t('home.catEyebrow') }}</span>
            </div>
            <h3 class="cat-card-title">{{ localCatName(cat) }}</h3>
            <p class="cat-card-desc">{{ t('home.catDesc') }}</p>
            <div class="industrial-line"></div>
            <span class="cat-tech-link micro-tag">{{ t('home.catLink') }} →</span>
          </router-link>
        </div>
      </div>
    </section>

    <!-- 3. Featured Products -->
    <section class="section-products section-with-accent" v-if="featured.length">
      <div class="section-accent-orb accent-cyan"></div>
      <div class="gl-container">
        <div class="section-header-center">
          <p class="eyebrow-cyan">{{ siteEyebrows.feat }}</p>
          <h2 class="section-title-xl"><template v-for="(p,i) in siteTitles.feat" :key="i">{{ i?' ':'' }}<span v-if="p.gradient" class="future-gradient">{{ p.text }}</span><template v-else>{{ p.text }}</template></template></h2>
          <p class="section-sub">{{ t('home.featSub') }}</p>
        </div>
        <div class="staggered-grid">
          <div v-for="p in featured" :key="p.id">
            <ProductCard :product="p" :hide-actions="hideActions" @inquire="openInquiry" />
          </div>
        </div>
        <div class="section-footer">
          <router-link to="/products?tab=featured" class="btn-glass-secondary">{{ t('home.viewAll') }}</router-link>
        </div>
      </div>
    </section>

    <!-- 4. New Products -->
    <section class="section-products section-alt" v-if="newProducts.length">
      <div class="gl-container">
        <div class="section-header-center">
          <p class="eyebrow-cyan">{{ siteEyebrows.new }}</p>
          <h2 class="section-title-xl"><template v-for="(p,i) in siteTitles.new" :key="i">{{ i?' ':'' }}<span v-if="p.gradient" class="future-gradient">{{ p.text }}</span><template v-else>{{ p.text }}</template></template></h2>
        </div>
        <div class="staggered-grid">
          <div v-for="p in newProducts" :key="p.id">
            <ProductCard :product="p" :hide-actions="hideActions" @inquire="openInquiry" />
          </div>
        </div>
        <div class="section-footer">
          <router-link to="/products?tab=new" class="btn-glass-secondary">{{ t('home.viewAll') }}</router-link>
        </div>
      </div>
    </section>

    <!-- 5-6-7. Toy Showcase + Clearance + Factory (连续区域) -->
    <section class="section-combined" v-if="toyCategories.length || (clearanceEnabled && clearanceProducts.length)">
      <div class="section-accent-orb accent-purple"></div>
      <div class="section-accent-orb accent-cyan" style="top:auto;bottom:-300px;left:50%;"></div>
      <div class="gl-container">

        <!-- 5. Toy Showcase -->
        <div v-if="toyCategories.length" class="combined-block">
          <div class="section-header-row">
            <div>
              <p class="eyebrow-cyan">{{ siteEyebrows.toys }}</p>
              <h2 class="section-title-xl"><template v-for="(p,i) in siteTitles.toys" :key="i">{{ i?' ':'' }}<span v-if="p.gradient" class="future-gradient">{{ p.text }}</span><template v-else>{{ p.text }}</template></template></h2>
            </div>
          </div>
          <div class="toy-showcase">
            <div v-for="tc in toyCategories" :key="tc.id" class="toy-block glass-card">
              <div class="toy-block-header">
                <h3>{{ localCatName(tc) }}</h3>
                <router-link :to="`/products?category_id=${tc.id}`" class="see-all-link">{{ t('home.viewAll') }} →</router-link>
              </div>
              <div class="toy-block-grid">
                <router-link v-for="p in (toyProducts[tc.id] || []).slice(0, 4)" :key="p.id" :to="`/products/${p.id}`" class="toy-item">
                  <img :src="p.images?.[0]" :alt="localTitle(p)" />
                  <span>{{ localTitle(p) }}</span>
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- 6. Clearance -->
        <div v-if="clearanceEnabled && clearanceProducts.length" class="combined-block clearance-block">
          <div class="clearance-banner">
            <div class="clearance-info">
              <p class="clearance-eyebrow">{{ t('home.clearanceEyebrow') }}</p>
              <h2>{{ t('clearance.title') }}</h2>
              <p class="clearance-sub">{{ t('clearance.subtitle') }}</p>
              <router-link to="/clearance" class="clearance-view-btn">{{ t('home.viewAll') }} →</router-link>
            </div>
            <div class="clearance-preview">
              <router-link v-for="p in clearanceProducts.slice(0, 4)" :key="p.id" :to="`/products/${p.id}`" class="clearance-thumb">
                <img :src="p.images?.[0]" :alt="localTitle(p)" />
              </router-link>
            </div>
          </div>
        </div>

        <!-- 7. Factory -->
        <div v-if="isB2B" class="combined-block">
          <div class="factory-grid">
            <div class="factory-image-wrap">
              <img :src="factoryImage" alt="Factory" class="factory-img" />
              <div class="factory-badge-overlay">
                <span class="micro-tag" style="color:#fff">GMPC</span>
              </div>
            </div>
            <div class="factory-info">
              <p class="eyebrow-cyan">{{ siteEyebrows.factory }}</p>
              <h2 class="section-title-xxl"><template v-for="(p,i) in siteTitles.factory" :key="i">{{ i?' ':'' }}<span v-if="p.gradient" class="future-gradient">{{ p.text }}</span><template v-else>{{ p.text }}</template></template></h2>
              <p class="factory-desc">{{ factoryDesc }}</p>
              <div class="stat-grid-2x2">
                <div v-for="(s, i) in factoryStatsData" :key="i" class="stat-card">
                  <span class="stat-number">{{ s.number }}</span>
                  <span class="stat-label">{{ s.label }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </section>

    <!-- 8. Process -->
    <section class="section-process">
      <div class="gl-container">
        <div class="section-header-center">
          <p class="eyebrow-cyan">{{ siteEyebrows.work }}</p>
          <h2 class="section-title-xl"><template v-for="(p,i) in siteTitles.work" :key="i">{{ i?' ':'' }}<span v-if="p.gradient" class="future-gradient">{{ p.text }}</span><template v-else>{{ p.text }}</template></template></h2>
        </div>
        <div class="process-grid">
          <div v-for="(step, idx) in processStepsData" :key="idx" class="process-step">
            <span class="process-bg-num">{{ String(idx + 1).padStart(2, '0') }}</span>
            <div class="process-image-area"><img v-if="step.icon && step.icon.startsWith('/')" :src="step.icon" class="process-icon-img" /><div v-else class="process-icon">{{ step.icon }}</div></div>
            <h3>{{ step.title }}</h3>
            <p>{{ step.desc }}</p>
            <div class="process-underline"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 11. Inquiry Dialog -->
    <el-dialog v-if="!hideActions" v-model="showInquiry" :title="t('product.inquire.title')" width="520px">
      <p class="inq-sub">{{ t('product.inquire.sub') }}</p>
      <p v-if="inquiryProduct" class="inq-product">{{ localTitle(inquiryProduct) }}</p>
      <form class="inq-form" @submit.prevent="submitInquiry">
        <input v-model="inquiryForm.contact_name" :placeholder="t('product.inquire.name')" required />
        <input v-model="inquiryForm.email" :placeholder="t('product.inquire.email')" type="email" required />
        <input v-model="inquiryForm.company_name" :placeholder="t('product.inquire.company')" />
        <input v-model="inquiryForm.phone" :placeholder="t('product.inquire.phone')" />
        <input v-model.number="inquiryForm.quantity" :placeholder="t('product.inquire.qty')" type="number" min="1" />
        <el-select v-model="inquiryForm.source" :placeholder="t('home.howFind')" clearable style="width:100%">
          <el-option value="tiktok" label="TikTok" />
          <el-option value="facebook" label="Facebook" />
          <el-option value="google" label="Google" />
          <el-option value="instagram" label="Instagram" />
          <el-option value="referral" :label="t('home.referralLabel')" />
          <el-option value="other" :label="t('home.otherLabel')" />
        </el-select>
        <textarea v-model="inquiryForm.message" :placeholder="t('product.inquire.msg')" rows="3" required></textarea>
        <el-button type="primary" native-type="submit" :loading="sending" style="width:100%;font-weight:700">
          {{ sending ? t('product.inquire.sending') : t('product.inquire.send') }}
        </el-button>
      </form>
      <p v-if="inquirySent" class="inq-success">{{ t('product.inquire.success') }}</p>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDisplay } from '../utils/display'
import { useAuth } from '../store/auth'
import { useSiteMode } from '../composables/useSiteMode'
import { useClearance } from '../composables/useClearance'
import { ElMessage } from 'element-plus'
import api from '../api'
import ProductCard from '../components/ProductCard.vue'

const { t, locale } = useI18n()
const { localCatName, localTitle, isZh } = useDisplay()
const { state: authState } = useAuth()
const { isB2B, isB2C, loadSiteMode } = useSiteMode()
const { clearanceEnabled, loadClearanceStatus } = useClearance()

const heroBgImage = ref('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=1600&q=80')
const factoryImage = ref('https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&q=80')
const factoryDesc = ref('')
const factoryStatsData = ref([])
const processStepsData = ref([])
const siteEyebrows = reactive({})
const rawSiteSettings = ref(null)

// Dynamic title parts from site settings: [{text, gradient}]
const siteTitles = reactive({
  hero: [], heroDesc: [], cat: [], feat: [], new: [], toys: [], factory: [], work: []
})

function parseSiteSettings(settings, lang) {
  if (!settings) return
  const l = lang || locale.value || 'zh'
  const sections = ['hero','heroDesc','cat','feat','new','toys','factory','work']
  for (const sec of sections) {
    const raw = settings[`${sec}.${l}`]
    siteTitles[sec] = raw ? (JSON.parse(raw) || []) : []
  }
  // Eyebrows
  const eyebrowKeys = ['cat','feat','new','toys','factory','work']
  for (const key of eyebrowKeys) {
    siteEyebrows[key] = settings[`eyebrow_${key}.${l}`] || ''
  }
  // Factory
  if (settings.factory_image) factoryImage.value = settings.factory_image
  factoryDesc.value = settings[`factory_desc.${l}`] || ''
  if (settings.factory_stats) {
    try {
      const stats = JSON.parse(settings.factory_stats)
      factoryStatsData.value = stats.map(s => ({ number: s.number, label: s['label_' + l] || s.label_en || '' }))
    } catch {}
  }
  // Process steps
  if (settings.process_steps) {
    try {
      const steps = JSON.parse(settings.process_steps)
      processStepsData.value = steps.map(s => ({ icon: s.icon, title: s['title_' + l] || s.title_en || '', desc: s['desc_' + l] || s.desc_en || '' }))
    } catch {}
  }
}

// Re-parse when language changes
watch(locale, (newLang) => {
  if (rawSiteSettings.value) parseSiteSettings(rawSiteSettings.value, newLang)
})
const hideActions = computed(() => {
  const role = authState.user?.role
  return role !== 'buyer'
})
const categories = ref([])
const featured = ref([])
const newProducts = ref([])
const clearanceProducts = ref([])
const bannerProducts = ref([])
const toyCategories = ref([])
const toyProducts = ref({})

const showInquiry = ref(false)
const inquiryProduct = ref(null)
const sending = ref(false)
const inquirySent = ref(false)
const inquiryForm = reactive({ contact_name: '', email: '', company_name: '', phone: '', quantity: null, message: '', source: '' })

function openInquiry(product) {
  inquiryProduct.value = product
  inquirySent.value = false
  const u = authState.user
  Object.assign(inquiryForm, {
    contact_name: u?.username || '',
    email: u?.email || '',
    company_name: u?.company_name || '',
    phone: u?.phone || '',
    quantity: null,
    message: '',
    source: u?.source || ''
  })
  showInquiry.value = true
}

async function submitInquiry() {
  sending.value = true
  try {
    await api.post('/inquiries', { ...inquiryForm, product_id: inquiryProduct.value.id })
    inquirySent.value = true
    ElMessage.success(t('product.inquire.success'))
    setTimeout(() => { showInquiry.value = false }, 2000)
  } catch { ElMessage.error('Failed') } finally { sending.value = false }
}

onMounted(async () => {
  await loadSiteMode()
  // Load site settings and override i18n
  try {
    const { data: settings } = await api.get('/site-settings')
    if (settings.hero_bg_image) heroBgImage.value = settings.hero_bg_image
    rawSiteSettings.value = settings
    parseSiteSettings(settings)
  } catch (e) { /* use defaults */ }

  try {
    const [cats, feat, news, cl, bannerRes] = await Promise.all([
      api.get('/categories'), api.get('/featured-products'), api.get('/new-products'),
      api.get('/clearance-products', { params: { per_page: 8 } }),
      api.get('/banner-products'),
    ])
    categories.value = cats.data
    featured.value = feat.data
    newProducts.value = news.data
    clearanceProducts.value = cl.data.items || cl.data || []
    await loadClearanceStatus()
    bannerProducts.value = (bannerRes.data || []).filter(p => p.images?.length).slice(0, 6)

    // Toy categories: find the Toys parent and its children
    const toysParent = cats.data.find(c => c.name_en === 'Toys' || c.name === '玩具全品类')
    if (toysParent && toysParent.children?.length) {
      const subCats = toysParent.children.slice(0, 4)
      toyCategories.value = subCats
      // Load products for each toy subcategory
      const toyLoads = subCats.map(sc => api.get('/products', { params: { category_id: sc.id, per_page: 4 } }))
      const toyResults = await Promise.all(toyLoads)
      const map = {}
      subCats.forEach((sc, i) => { map[sc.id] = toyResults[i].data.items || [] })
      toyProducts.value = map
    }
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
/* ── Industrial Design System — HomePage ── */

/* ── Animations ── */
@keyframes heroSlideUp {
  from { opacity: 0; transform: translateY(40px); filter: blur(4px); }
  to { opacity: 1; transform: translateY(0); filter: blur(0); }
}
@keyframes pulse-glow {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(0, 210, 255, 0.4); }
  50% { opacity: .7; box-shadow: 0 0 0 6px rgba(0, 210, 255, 0); }
}
.anim-slide-up { animation: heroSlideUp .8s cubic-bezier(.16,1,.3,1) both; }
.anim-d1 { animation-delay: .15s; }
.anim-d2 { animation-delay: .3s; }
.anim-d3 { animation-delay: .45s; }

/* ── Base ── */
.home {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  color: #0F172A;
}
.gl-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 48px;
}
.future-gradient {
  background: linear-gradient(135deg, #00d2ff 0%, #7000ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.industrial-line {
  height: 0.5px;
  width: 100%;
  background: #e2e8f0;
}
.micro-tag {
  font-size: 9px;
  font-weight: 900;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: #94a3b8;
}

/* ── Shared Section Utilities ── */
.eyebrow-cyan {
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.5em;
  text-transform: uppercase;
  color: #00d2ff;
  margin-bottom: 12px;
}
.section-title-xl {
  font-size: clamp(36px, 5vw, 56px);
  font-weight: 800;
  color: #0F172A;
  letter-spacing: -1.5px;
  line-height: 1.1;
  margin-bottom: 16px;
}
.section-title-xxl {
  font-size: clamp(42px, 6vw, 68px);
  font-weight: 800;
  color: #0F172A;
  letter-spacing: -2px;
  line-height: 1.05;
  margin-bottom: 20px;
}
.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 48px;
}
.section-header-center {
  text-align: center;
  margin-bottom: 56px;
}
.section-sub {
  font-size: 16px;
  color: #94a3b8;
  margin-top: 8px;
}
.section-footer {
  text-align: center;
  margin-top: 48px;
}
.mono-stat {
  font-family: 'JetBrains Mono', 'SF Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.15em;
  color: #94a3b8;
}

/* ── 1. Hero Section ── */
.hero-section {
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding: 120px 0 80px;
  margin-top: -96px;
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.4);
  overflow: hidden;
}
.hero-bg-photo {
  position: absolute;
  inset: 0;
  z-index: 0;
}
.hero-bg-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.18;
  transform: scale(1.05);
}
.hero-bg-overlay {
  position: absolute;
  inset: 0;
  z-index: 1;
  background: linear-gradient(to bottom, rgba(255,255,255,.15) 0%, rgba(255,255,255,.4) 50%, rgba(255,255,255,.6) 100%);
}
.hero-bg-image {
  position: absolute;
  inset: 0;
  z-index: 1;
  background:
    radial-gradient(ellipse 80% 60% at 20% 40%, rgba(0,210,255,.04) 0%, transparent 70%),
    radial-gradient(ellipse 60% 50% at 80% 30%, rgba(112,0,255,.04) 0%, transparent 70%);
  opacity: 0.6;
  pointer-events: none;
}
.hero-grid {
  display: grid;
  grid-template-columns: 1fr 480px;
  gap: 48px;
  align-items: start;
  position: relative;
  z-index: 2;
}
.hero-left {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding-top: 40px;
  min-width: 0;
  overflow-wrap: break-word;
  word-break: break-word;
}
.glass-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  width: fit-content;
  padding: 10px 24px;
  border-radius: 100px;
  background: rgba(255,255,255,.7);
  backdrop-filter: blur(12px);
  border: 0.5px solid rgba(15,23,42,.05);
  margin-bottom: 32px;
}
.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00d2ff;
  animation: pulse-glow 2s ease-in-out infinite;
}
.hero-title {
  font-size: clamp(36px, 5vw, 72px);
  font-weight: 800;
  line-height: 1.08;
  color: #0F172A;
  letter-spacing: -2px;
  overflow-wrap: break-word;
  word-break: break-word;
  margin-bottom: 28px;
}
.hero-desc {
  font-size: 20px;
  color: #64748b;
  line-height: 1.8;
  margin-bottom: 40px;
  max-width: 560px;
  padding-left: 32px;
  border-left: 0.5px solid rgba(112,0,255,.3);
}
.hero-actions {
  display: flex;
  gap: 16px;
}

/* Buttons */
.btn-gradient-primary {
  display: inline-flex;
  align-items: center;
  padding: 24px 48px;
  font-weight: 700;
  font-size: 14px;
  border-radius: 20px;
  background: linear-gradient(135deg, #00d2ff 0%, #7000ff 100%);
  color: #fff;
  transition: all .7s cubic-bezier(.4,0,.2,1);
  box-shadow: 0 4px 24px rgba(112,0,255,.2);
  letter-spacing: 0.02em;
}
.btn-gradient-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(112,0,255,.3);
}
.btn-glass-secondary {
  display: inline-flex;
  align-items: center;
  padding: 24px 48px;
  font-weight: 700;
  font-size: 14px;
  border-radius: 20px;
  background: rgba(255,255,255,.6);
  backdrop-filter: blur(12px);
  border: 0.5px solid rgba(15,23,42,.05);
  color: #0F172A;
  transition: all .7s cubic-bezier(.4,0,.2,1);
}
.btn-glass-secondary:hover {
  background: rgba(255,255,255,.9);
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,.06);
}

/* Hero Right */
.hero-right {
  display: flex;
  justify-content: center;
  position: relative;
  width: 480px;
  height: 540px;
  flex-shrink: 0;
}
.hero-card-wrap {
  width: 480px;
  height: 540px;
  padding: 16px;
  position: relative;
  background: rgba(255,255,255,.5);
  backdrop-filter: blur(16px);
  border: 0.5px solid rgba(15,23,42,.05);
  border-radius: 48px;
  box-shadow: 0 20px 50px -10px rgba(15,23,42,.06), 0 8px 20px -4px rgba(0,0,0,.02);
  transition: all .7s cubic-bezier(.4,0,.2,1);
}
.hero-card-wrap:hover {
  box-shadow: 0 30px 60px -12px rgba(15,23,42,.08);
}
.hero-card-wrap :deep(.el-carousel) { border-radius: 36px; overflow: hidden; }
.hero-card-wrap :deep(.el-carousel__container) { border-radius: 36px; overflow: hidden; }
.hero-card-wrap :deep(.el-carousel__indicators) {
  position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%);
}
.hero-card-wrap :deep(.el-carousel__indicator .el-carousel__button) {
  width: 20px; height: 3px; border-radius: 2px; background: #cbd5e1;
}
.hero-card-wrap :deep(.el-carousel__indicator.is-active .el-carousel__button) {
  background: #7000ff; width: 28px;
}

/* Hero stat overlay */
.hero-stat-overlay {
  position: absolute;
  bottom: -16px;
  right: -16px;
  padding: 18px 28px;
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  z-index: 10;
  background: rgba(255,255,255,.85);
  backdrop-filter: blur(20px);
  border: 0.5px solid rgba(15,23,42,.05);
  box-shadow: 0 8px 32px rgba(0,0,0,.08);
}
.stat-bold {
  font-size: 28px;
  font-weight: 800;
  color: #0F172A;
}

/* Banner slides */
.banner-slide {
  display: block;
  position: relative;
  height: 480px;
  overflow: hidden;
  border-radius: 36px;
}
.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(0.2);
  transition: all .7s cubic-bezier(.4,0,.2,1);
}
.banner-slide:hover .banner-img {
  filter: grayscale(0);
  transform: scale(1.03);
}
.banner-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 28px 32px;
  background: linear-gradient(transparent, rgba(0,0,0,.55));
  color: #fff;
  border-radius: 0 0 36px 36px;
}
.banner-overlay h3 { font-size: 18px; font-weight: 700; margin-bottom: 4px; color: #fff !important; }
.banner-overlay p { font-size: 13px; opacity: .8; }
.banner-tag {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 100px;
  font-size: 10px;
  font-weight: 800;
  margin-bottom: 8px;
  color: #fff;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.banner-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
.clearance-tag { background: #dc2626; }
.hot-tag { background: #f59e0b; }
.new-tag { background: #16a34a; }

/* ── 2. Categories ── */
.section-categories {
  padding: 120px 0;
  background: linear-gradient(180deg, rgba(248,250,252,.5) 0%, rgba(241,245,249,.3) 100%);
  position: relative;
}
.industrial-grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(rgba(15,23,42,.02) 1px, transparent 1px),
    linear-gradient(to right, rgba(15,23,42,.005) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(15,23,42,.005) 1px, transparent 1px);
  background-size: 60px 60px, 180px 180px, 180px 180px;
  pointer-events: none;
}
.cat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  position: relative;
  z-index: 1;
}
.cat-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 36px 32px;
  border-radius: 40px;
  background: #fff;
  border: 0.5px solid rgba(15,23,42,.05);
  box-shadow: 0 10px 25px -5px rgba(0,0,0,.02), 0 4px 10px -2px rgba(0,0,0,.01);
  transition: all .7s cubic-bezier(.4,0,.2,1);
}
.cat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 30px 60px -12px rgba(15,23,42,.08), 0 18px 36px -18px rgba(15,23,42,.05);
  border-color: rgba(29,78,216,.2);
}
.cat-image-area {
  height: 256px;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}
.cat-image-area.color-0, .cat-icon-placeholder.color-0 { background: rgba(0,210,255,.06); }
.cat-image-area.color-1, .cat-icon-placeholder.color-1 { background: rgba(112,0,255,.06); }
.cat-image-area.color-2, .cat-icon-placeholder.color-2 { background: rgba(15,23,42,.04); }
.cat-icon-placeholder {
  width: 100%;
  height: 256px;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
  transition: all .7s cubic-bezier(.4,0,.2,1);
}
.cat-card:hover .cat-icon-placeholder {
  transform: scale(1.05);
}
.cat-tag {
  position: absolute;
  top: 16px;
  left: 16px;
  padding: 4px 12px;
  background: rgba(255,255,255,.9);
  backdrop-filter: blur(8px);
  border-radius: 100px;
  color: #94a3b8;
}
.cat-card-title {
  font-size: 18px;
  font-weight: 700;
  color: #0F172A;
}
.cat-card-desc {
  font-size: 14px;
  color: #64748b;
  line-height: 1.7;
}
.cat-tech-link {
  color: #1d4ed8;
  margin-top: auto;
  transition: letter-spacing .7s cubic-bezier(.4,0,.2,1);
}
.cat-card:hover .cat-tech-link {
  letter-spacing: 0.4em;
}

/* ── 3 & 4. Products Sections ── */
.section-products {
  padding: 120px 0;
  background: #fff;
  position: relative;
  overflow: hidden;
}
.section-products.section-alt {
  background: linear-gradient(180deg, rgba(248,250,252,.5) 0%, rgba(241,245,249,.3) 100%);
}
.section-with-accent {
  overflow: hidden;
}
.section-accent-orb {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  filter: blur(140px);
  pointer-events: none;
  z-index: 0;
}
.section-accent-orb.accent-cyan {
  background: rgba(0,210,255,.04);
  top: -200px;
  right: -100px;
}
.section-accent-orb.accent-purple {
  background: rgba(112,0,255,.04);
  bottom: -200px;
  left: -100px;
}
.staggered-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 40px;
}
.staggered-grid > div:nth-child(even) {
  transform: translateY(40px);
}

/* ── 5. Toy Showcase ── */
.toy-showcase {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}
.toy-block {
  padding: 28px;
  border-radius: 32px;
  transition: all .7s cubic-bezier(.4,0,.2,1);
}
.toy-block:hover {
  box-shadow: 0 30px 60px -12px rgba(15,23,42,.08);
}
.toy-block-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.toy-block-header h3 { font-size: 17px; font-weight: 700; color: #0F172A; }
.see-all-link {
  font-size: 12px;
  font-weight: 700;
  color: #1d4ed8;
  letter-spacing: 0.05em;
  transition: letter-spacing .7s cubic-bezier(.4,0,.2,1);
}
.see-all-link:hover { letter-spacing: 0.15em; }
.toy-block-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.toy-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
  transition: transform .7s cubic-bezier(.4,0,.2,1);
}
.toy-item:hover { transform: translateY(-4px); }
.toy-item img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 16px;
  border: 0.5px solid rgba(15,23,42,.05);
  filter: grayscale(0.2);
  transition: all .7s cubic-bezier(.4,0,.2,1);
}
.toy-item:hover img {
  filter: grayscale(0);
}
.toy-item span {
  font-size: 11px;
  color: #64748b;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ── 5-6-7. Combined Section (Toys + Clearance + Factory) ── */
.section-combined {
  padding: 120px 0;
  background: #fff;
  position: relative;
  overflow: hidden;
}
.combined-block {
  margin-bottom: 120px;
}
.combined-block.clearance-block {
  margin-top: 240px;
  margin-bottom: 240px;
}
.combined-block:last-child {
  margin-bottom: 0;
}

/* ── 6. Clearance ── */
@keyframes flowRed {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.clearance-banner {
  display: flex;
  align-items: center;
  gap: 48px;
  background: linear-gradient(270deg, #dc2626, #f97316, #ef4444, #b91c1c, #f97316);
  background-size: 300% 300%;
  animation: flowRed 6s ease infinite;
  border-radius: 40px;
  padding: 56px 64px;
  color: #fff;
  position: relative;
  overflow: hidden;
}
.clearance-banner::before {
  content: '';
  position: absolute;
  width: 400px; height: 400px;
  border-radius: 50%;
  background: rgba(255,255,255,.08);
  filter: blur(80px);
  top: -30%; right: -5%;
}
.clearance-info { flex: 1; position: relative; z-index: 1; color: #fff; }
.clearance-eyebrow {
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: rgba(255,255,255,.85);
  margin-bottom: 8px;
}
.clearance-info h2 { font-size: 32px; font-weight: 800; margin-bottom: 8px; color: #fff !important; -webkit-text-fill-color: #fff; }
.clearance-sub { font-size: 15px; color: rgba(255,255,255,.9); margin-bottom: 24px; }
.clearance-view-btn {
  display: inline-block;
  padding: 12px 32px;
  background: #fff;
  color: #dc2626;
  font-weight: 700;
  border-radius: 16px;
  font-size: 14px;
  transition: all .7s cubic-bezier(.4,0,.2,1);
}
.clearance-view-btn:hover {
  background: rgba(255,255,255,.9);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(255,255,255,.3);
}
.clearance-preview {
  display: flex;
  gap: 16px;
  position: relative;
  z-index: 1;
}
.clearance-thumb {
  width: 110px; height: 110px;
  border-radius: 24px;
  overflow: hidden;
  border: 2px solid rgba(255,255,255,.3);
  transition: all .7s cubic-bezier(.4,0,.2,1);
}
.clearance-thumb:hover { border-color: #fff; transform: scale(1.08); }
.clearance-thumb img { width: 100%; height: 100%; object-fit: cover; }

/* ── 7. Factory / Why Choose Us ── */
.factory-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
  align-items: center;
}
.factory-image-wrap {
  position: relative;
  border-radius: 64px;
  overflow: hidden;
}
.factory-img {
  width: 100%;
  height: 520px;
  object-fit: cover;
  border-radius: 64px;
  filter: grayscale(0.2);
  transition: all .7s cubic-bezier(.4,0,.2,1);
}
.factory-image-wrap:hover .factory-img {
  filter: grayscale(0);
}
.factory-badge-overlay {
  position: absolute;
  top: 24px;
  left: 24px;
  padding: 10px 20px;
  background: rgba(0,0,0,.4);
  backdrop-filter: blur(12px);
  border-radius: 100px;
  border: 0.5px solid rgba(255,255,255,.2);
}
.factory-info {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.factory-desc {
  font-size: 16px;
  color: #64748b;
  line-height: 1.8;
  margin-bottom: 32px;
}
.stat-grid-2x2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px 24px;
  border-radius: 32px;
  background: #fff;
  border: 0.5px solid rgba(15,23,42,.05);
  box-shadow: 0 10px 25px -5px rgba(0,0,0,.02);
  transition: all .7s cubic-bezier(.4,0,.2,1);
}
.stat-card:hover {
  border-color: rgba(29,78,216,.3);
  box-shadow: 0 30px 60px -12px rgba(15,23,42,.08);
  transform: translateY(-4px);
}
.stat-card:hover .stat-number {
  color: #1d4ed8;
}
.stat-number {
  font-size: 32px;
  font-weight: 800;
  color: #0F172A;
  transition: color .7s cubic-bezier(.4,0,.2,1);
}
.stat-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 600;
  text-align: center;
}

/* ── 8. Process ── */
.section-process {
  padding: 120px 0;
  background: #fff;
  position: relative;
}
.process-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32px;
}
.process-step {
  position: relative;
  padding: 40px 28px 36px;
  overflow: hidden;
}
.process-bg-num {
  position: absolute;
  top: -10px;
  left: 0;
  font-size: 120px;
  font-weight: 900;
  color: rgba(248,250,252,.8);
  line-height: 1;
  pointer-events: none;
  z-index: 0;
}
.process-image-area {
  height: 176px;
  border-radius: 24px;
  border: 0.5px solid rgba(15,23,42,.05);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
  background: rgba(248,250,252,.5);
  transition: all .7s cubic-bezier(.4,0,.2,1);
}
.process-step:hover .process-image-area {
  border-color: rgba(29,78,216,.2);
}
.process-icon {
  font-size: 48px;
}
.process-icon-img {
  width: 64px;
  height: 64px;
  object-fit: contain;
  border-radius: 12px;
}
.process-step h3 {
  font-size: 18px;
  font-weight: 700;
  color: #0F172A;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}
.process-step p {
  font-size: 14px;
  color: #64748b;
  line-height: 1.7;
  position: relative;
  z-index: 1;
  margin-bottom: 16px;
}
.process-underline {
  height: 1.5px;
  width: 48px;
  background: linear-gradient(90deg, #00d2ff, #7000ff);
  border-radius: 1px;
  transition: width .7s cubic-bezier(.4,0,.2,1);
  position: relative;
  z-index: 1;
}
.process-step:hover .process-underline {
  width: 100%;
}

/* ── 9. Certifications ── */
.section-certs {
  padding: 96px 0;
  background: #fff;
}
.cert-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 48px;
  flex-wrap: wrap;
  margin-top: 32px;
}
.cert-item {
  font-size: clamp(24px, 3vw, 36px);
  font-weight: 800;
  color: #0F172A;
  opacity: 0.3;
  filter: grayscale(1);
  transition: all .7s cubic-bezier(.4,0,.2,1);
  cursor: default;
}
.cert-item:hover {
  opacity: 1;
  color: #1d4ed8;
  filter: grayscale(0);
}

/* ── 10. CTA Section ── */
.section-cta {
  padding: 120px 0;
  background: #fff;
}
.cta-glass-panel {
  background: rgba(255,255,255,.7);
  backdrop-filter: blur(20px);
  border: 0.5px solid rgba(15,23,42,.05);
  border-radius: 64px;
  padding: 80px;
  box-shadow: 0 10px 25px -5px rgba(0,0,0,.02);
}
.cta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
  align-items: center;
}
.cta-left { display: flex; flex-direction: column; gap: 0; }
.cta-desc {
  font-size: 16px;
  color: #64748b;
  margin-bottom: 32px;
  line-height: 1.7;
}
.cta-checklist {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.cta-checklist li {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 15px;
  color: #334155;
  font-weight: 500;
}
.check-icon {
  width: 28px; height: 28px;
  border-radius: 8px;
  background: rgba(29,78,216,.1);
  color: #1d4ed8;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 800; flex-shrink: 0;
}
.cta-right {
  padding: 40px;
  border-radius: 32px;
}
.form-title {
  font-size: 20px;
  font-weight: 700;
  color: #0F172A;
  margin-bottom: 24px;
}
.submit-btn {
  width: 100%;
  font-weight: 700;
  border-radius: 16px !important;
  height: 48px;
}

/* ── Inquiry Dialog & Forms ── */
.inq-sub { color: #64748b; font-size: 14px; margin-bottom: 8px; }
.inq-product { font-weight: 700; margin-bottom: 16px; color: #0F172A; }
.inq-form { display: flex; flex-direction: column; gap: 12px; }
.inq-form input, .inq-form textarea {
  background: rgba(248,250,252,.8);
  border: 0.5px solid rgba(15,23,42,.05);
  border-radius: 16px;
  padding: 12px 18px;
  color: #0F172A;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: all .4s cubic-bezier(.4,0,.2,1);
}
.inq-form input:focus, .inq-form textarea:focus {
  border-color: #1d4ed8;
  box-shadow: 0 0 0 3px rgba(29,78,216,.1);
}
.source-select {
  background: rgba(248,250,252,.8);
  border: 0.5px solid rgba(15,23,42,.05);
  border-radius: 16px;
  padding: 12px 18px;
  color: #0F172A;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: all .4s cubic-bezier(.4,0,.2,1);
  width: 100%;
}
.source-select:focus {
  border-color: #1d4ed8;
  box-shadow: 0 0 0 3px rgba(29,78,216,.1);
}
.inq-success { color: #059669; font-weight: 600; margin-top: 12px; }

/* ── Responsive: Wide Tablet (max-width: 1200px) ── */
@media (max-width: 1200px) {
  .hero-grid { grid-template-columns: 1fr; gap: 32px; }
  .hero-left { padding-top: 0; text-align: center; align-items: center; }
  .hero-right { width: 100%; height: auto; margin: 0 auto; }
  .hero-card-wrap { width: 100%; max-width: 520px; height: auto; margin: 0 auto; }
  .hero-desc { max-width: 100%; border-left: none; padding-left: 0; text-align: center; }
  .hero-actions { justify-content: center; }
}

/* ── Responsive: Tablet (max-width: 1024px) ── */
@media (max-width: 1024px) {
  .gl-container { padding: 0 32px; }
  .section-categories,
  .section-products,
  .section-combined,
  .section-process,
  .section-cta { padding: 72px 0; }
  .section-certs { padding: 48px 0; }
  .hero-section { min-height: auto; padding: 32px 0 40px; margin-top: 0; }
  .hero-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }
  .hero-left { order: 1; text-align: center; align-items: center; padding-top: 0; }
  .hero-right { order: 2; width: 100%; height: auto; margin: 0 auto; }
  .hero-title { font-size: 44px; letter-spacing: -1px; }
  .hero-desc { max-width: 100%; border-left: none; padding-left: 0; text-align: center; }
  .hero-actions { justify-content: center; }
  .hero-card-wrap { max-width: 100%; width: 100%; height: auto; }
  .hero-card-wrap :deep(.el-carousel__container) { height: 360px !important; }
  .banner-slide { height: 360px; }
  .banner-overlay { padding: 20px 24px; }
  .banner-overlay h3 { font-size: 16px; }
  .hero-stat-overlay { right: 8px; bottom: -8px; }
  .cat-grid { grid-template-columns: repeat(2, 1fr); }
  .staggered-grid { grid-template-columns: repeat(3, 1fr); }
  .staggered-grid > div:nth-child(even) { transform: none; }
  .factory-grid { grid-template-columns: 1fr; gap: 48px; }
  .factory-img { height: 360px; }
  .factory-image-wrap { border-radius: 40px; }
  .process-grid { grid-template-columns: repeat(2, 1fr); gap: 24px; }
  .process-bg-num { font-size: 80px; }
  .cta-glass-panel { padding: 48px; border-radius: 40px; }
  .cta-grid { grid-template-columns: 1fr; gap: 40px; }
  .clearance-banner { flex-direction: column; text-align: center; padding: 40px 32px; }
  .clearance-preview { justify-content: center; }
  .toy-showcase { grid-template-columns: 1fr; }
  .section-header-row { flex-direction: column; align-items: flex-start; gap: 16px; }
  .stat-grid-2x2 { gap: 12px; }
  .cert-row { gap: 32px; }
}

/* ── Responsive: Mobile (max-width: 640px) ── */
@media (max-width: 640px) {
  .gl-container { padding: 0 20px; }
  .section-categories,
  .section-products,
  .section-combined,
  .section-process,
  .section-cta { padding: 48px 0; }
  .section-certs { padding: 32px 0; }
  .hero-section { padding: 24px 0 32px; margin-top: 0; }
  .hero-grid { grid-template-columns: 1fr; gap: 24px; }
  .hero-right { width: 100%; height: auto; }
  .hero-title { font-size: 32px; letter-spacing: -0.5px; }
  .glass-badge { padding: 6px 14px; }
  .hero-desc { font-size: 16px; }
  .hero-actions {
    flex-direction: column;
    align-items: center;
    gap: 12px;
    width: 100%;
  }
  .btn-gradient-primary, .btn-glass-secondary {
    width: 100%;
    max-width: 280px;
    justify-content: center;
    padding: 16px 32px;
  }
  .hero-card-wrap { max-width: 100%; width: 100%; height: auto; border-radius: 24px; padding: 10px; }
  .hero-card-wrap :deep(.el-carousel) { border-radius: 20px; }
  .hero-card-wrap :deep(.el-carousel__container) { height: 240px !important; border-radius: 20px; }
  .banner-slide { height: 240px; border-radius: 20px; }
  .banner-overlay { padding: 14px 16px; border-radius: 0 0 20px 20px; }
  .banner-overlay h3 { font-size: 14px; margin-bottom: 2px; }
  .banner-overlay p { font-size: 11px; }
  .banner-tag { font-size: 8px; padding: 3px 8px; margin-bottom: 4px; }
  .banner-tags { gap: 4px; margin-bottom: 4px; }
  .hero-stat-overlay { display: none; }
  .cat-grid { grid-template-columns: 1fr; }
  .cat-card { padding: 28px 24px; border-radius: 32px; }
  .cat-icon-placeholder { height: 180px; font-size: 48px; }
  .staggered-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .staggered-grid > div:nth-child(even) { transform: none; }
  .factory-img { height: 260px; border-radius: 32px; }
  .factory-image-wrap { border-radius: 32px; }
  .stat-grid-2x2 { grid-template-columns: 1fr 1fr; gap: 10px; }
  .stat-card { padding: 20px 16px; border-radius: 24px; }
  .stat-number { font-size: 24px; }
  .process-grid { grid-template-columns: 1fr; }
  .process-bg-num { font-size: 64px; }
  .cta-glass-panel { padding: 32px 24px; border-radius: 32px; }
  .cta-grid { grid-template-columns: 1fr; gap: 32px; }
  .cta-right { padding: 28px 24px; border-radius: 24px; }
  .section-title-xl { font-size: 28px; letter-spacing: -0.5px; }
  .section-title-xxl { font-size: 32px; letter-spacing: -0.5px; }
  .eyebrow-cyan { font-size: 9px; letter-spacing: 0.3em; }
  .combined-block.clearance-block { margin-top: 80px; margin-bottom: 80px; }
  .clearance-banner { padding: 32px 24px; border-radius: 24px; }
  .clearance-thumb { width: 80px; height: 80px; border-radius: 14px; }
  .toy-block-grid { grid-template-columns: repeat(2, 1fr); }
  .toy-block { padding: 20px; border-radius: 24px; }
  .cert-row { gap: 20px; }
  .cert-item { font-size: 20px; }
}

/* ── Responsive: Small Mobile (max-width: 480px) ── */
@media (max-width: 480px) {
  .staggered-grid { grid-template-columns: 1fr; }
  .hero-title { font-size: 28px; }
  .stat-grid-2x2 { grid-template-columns: 1fr; }
  .hero-card-wrap :deep(.el-carousel__container) { height: 200px !important; }
  .banner-slide { height: 200px; }
  .banner-overlay { padding: 10px 12px; }
  .banner-overlay h3 { font-size: 13px; }
  .banner-tag { font-size: 7px; padding: 2px 6px; }
  .combined-block.clearance-block { margin-top: 120px; margin-bottom: 120px; }
}
</style>
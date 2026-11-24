<template>
  <div class="product-list-page">
    <div class="container">
      <div class="page-header fade-up">
        <h1>{{ t('product.all') }}</h1>
        <p>{{ total }} {{ t('product.found') }}</p>
      </div>
      <div class="list-layout">
        <aside class="sidebar fade-up fade-up-d1">
          <div class="filter-group">
            <h4>{{ t('product.category') }}</h4>
            <div class="cat-tree">
              <div class="cat-tree-item" :class="{ active: filters.category_id === null }" @click="selectCategory(null)">
                <span class="cat-tree-name">{{ t('product.allCat') }}</span>
              </div>
              <div v-for="parent in categories" :key="parent.id" class="cat-parent-group">
                <div class="cat-tree-item parent" :class="{ active: filters.category_id === parent.id }" @click="toggleOrSelect(parent)">
                  <span class="cat-tree-icon">{{ parent.icon || '📁' }}</span>
                  <span class="cat-tree-name">{{ localCatName(parent) }}</span>
                  <span class="cat-tree-arrow" v-if="parent.children && parent.children.length">
                    {{ expandedCat === parent.id ? '▾' : '▸' }}
                  </span>
                </div>
                <transition name="expand">
                  <div v-if="expandedCat === parent.id && parent.children && parent.children.length" class="cat-children">
                    <div v-for="child in parent.children" :key="child.id" class="cat-tree-item child"
                      :class="{ active: filters.category_id === child.id }" @click.stop="selectCategory(child.id)">
                      <span class="cat-tree-dot">·</span>
                      <span class="cat-tree-name">{{ localCatName(child) }}</span>
                    </div>
                  </div>
                </transition>
              </div>
              <!-- 营销专区 -->
              <div class="cat-divider"></div>
              <div class="cat-tree-item" :class="{ active: activeTab === 'featured' }" @click="selectTab('featured')">
                <span class="cat-tree-icon">🔥</span>
                <span class="cat-tree-name">{{ t('home.hot') }}</span>
              </div>
              <div class="cat-tree-item" :class="{ active: activeTab === 'new' }" @click="selectTab('new')">
                <span class="cat-tree-icon">✨</span>
                <span class="cat-tree-name">{{ t('home.new') }}</span>
              </div>
            </div>
          </div>
          <div class="filter-group">
            <h4>{{ t('product.maxMoq') }}</h4>
            <el-select v-model="filters.moq_max" @change="loadProducts" :placeholder="t('product.any')" clearable size="small" style="width:100%">
              <el-option label="≤ 10" :value="10" />
              <el-option label="≤ 50" :value="50" />
              <el-option label="≤ 100" :value="100" />
              <el-option label="≤ 500" :value="500" />
              <el-option label="≤ 1000" :value="1000" />
            </el-select>
          </div>
          <div class="filter-group">
            <h4>{{ t('product.leadTime') }}</h4>
            <el-select v-model="filters.lead_time" @change="loadProducts" :placeholder="t('product.any')" clearable size="small" style="width:100%">
              <el-option :label="t('filter.within7days')" :value="7" />
              <el-option :label="t('filter.within15days')" :value="15" />
              <el-option :label="t('filter.within30days')" :value="30" />
              <el-option :label="t('filter.within60days')" :value="60" />
            </el-select>
          </div>
          <div class="filter-group">
            <h4>{{ t('filter.certification') }}</h4>
            <el-select v-model="filters.certification" @change="loadProducts" :placeholder="t('product.any')" clearable size="small" style="width:100%">
              <el-option label="CE" value="CE" />
              <el-option label="FCC" value="FCC" />
              <el-option label="RoHS" value="RoHS" />
              <el-option label="ISO" value="ISO" />
              <el-option label="CCC" value="CCC" />
              <el-option label="UL" value="UL" />
            </el-select>
          </div>
          <div v-if="clearanceEnabled" class="filter-group">
            <el-checkbox v-model="filters.is_clearance" @change="loadProducts" :label="t('filter.clearanceOnly')" />
          </div>
          <div class="filter-group">
            <h4>{{ t('product.search') }}</h4>
            <el-input v-model="filters.q" :placeholder="t('product.search')" size="small" @keyup.enter="loadProducts" clearable>
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </div>
          <el-button @click="resetFilters" size="small" style="width:100%;margin-top:8px">{{ t('product.reset') }}</el-button>
        </aside>
        <div class="grid-area">
          <div class="product-grid fade-up fade-up-d2">
            <ProductCard v-for="p in products" :key="p.id" :product="p" :hide-actions="hideActions" @inquire="openInquiry" />
          </div>
          <div v-if="!products.length && !loading" class="empty-state"><p>{{ t('product.noResult') }}</p></div>
          <div class="pagination" v-if="pages > 1">
            <el-pagination background layout="prev, pager, next" :current-page="page" :page-size="12" :total="total" @current-change="handlePage" />
          </div>
        </div>
      </div>
    </div>

    <!-- 询盘弹窗 -->
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
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useDisplay } from '../utils/display'
import { useAuth } from '../store/auth'
import { useClearance } from '../composables/useClearance'
import { ElMessage } from 'element-plus'
import api from '../api'
import ProductCard from '../components/ProductCard.vue'

const { t } = useI18n()
const { localCatName, localTitle, isZh } = useDisplay()
const { state: authState } = useAuth()
const { clearanceEnabled } = useClearance()
const hideActions = computed(() => {
  const role = authState.user?.role
  return role !== 'buyer'
})
const route = useRoute()
const router = useRouter()
const products = ref([])
const categories = ref([])
const total = ref(0)
const pages = ref(0)
const page = ref(1)
const loading = ref(false)
const expandedCat = ref(null)
const activeTab = ref('all')
const filters = reactive({ category_id: null, moq_max: null, q: '', lead_time: null, certification: null, is_clearance: false })

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

function toggleOrSelect(parent) {
  if (parent.children && parent.children.length) {
    expandedCat.value = expandedCat.value === parent.id ? null : parent.id
  }
  selectCategory(parent.id)
}

function selectCategory(catId) {
  const query = { ...route.query }
  if (catId) {
    query.category_id = catId
  } else {
    delete query.category_id
  }
  router.push({ path: '/products', query })
}

function selectTab(tab) {
  const next = activeTab.value === tab ? 'all' : tab
  activeTab.value = next
  page.value = 1
  const query = { ...route.query }
  if (next === 'all') {
    delete query.tab
  } else {
    query.tab = next
  }
  router.push({ path: '/products', query })
  loadProducts()
}

async function loadCategories() {
  const { data } = await api.get('/categories')
  categories.value = data
}

async function loadProducts() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: 12 }
    if (filters.category_id) params.category_id = filters.category_id
    if (filters.moq_max) params.moq_max = filters.moq_max
    if (filters.q) params.q = filters.q
    if (filters.lead_time) params.lead_time_max = filters.lead_time
    if (filters.certification) params.certification = filters.certification
    if (filters.is_clearance) params.is_clearance = true
    if (activeTab.value === 'featured') params.is_featured = true
    if (activeTab.value === 'new') params.is_new = true
    const { data } = await api.get('/products', { params })
    products.value = data.items; total.value = data.total; pages.value = data.pages
  } finally { loading.value = false }
}

function handlePage(p) { page.value = p; loadProducts() }
function resetFilters() { Object.assign(filters, { category_id: null, moq_max: null, q: '', lead_time: null, certification: null, is_clearance: false }); expandedCat.value = null; activeTab.value = 'all'; page.value = 1; router.push({ path: '/products' }); loadProducts() }

onMounted(async () => {
  await loadCategories()
  if (route.query.category_id) {
    const catId = Number(route.query.category_id)
    filters.category_id = catId
    for (const p of categories.value) {
      if (p.id === catId && p.children?.length) { expandedCat.value = p.id; break }
      if (p.children?.some(c => c.id === catId)) { expandedCat.value = p.id; break }
    }
  }
  if (route.query.tab === 'featured' || route.query.tab === 'new') {
    activeTab.value = route.query.tab
  }
  loadProducts()
})

watch(() => route.query, (q) => {
  const catId = q.category_id ? Number(q.category_id) : null
  const tab = q.tab || 'all'
  let changed = false
  if (catId !== filters.category_id) {
    filters.category_id = catId
    changed = true
    if (catId !== null) {
      for (const p of categories.value) {
        if (p.id === catId && p.children?.length) { expandedCat.value = p.id; break }
        if (p.children?.some(c => c.id === catId)) { expandedCat.value = p.id; break }
      }
    } else {
      expandedCat.value = null
    }
  }
  if (tab !== activeTab.value) {
    activeTab.value = tab
    changed = true
  }
  if (changed) {
    page.value = 1
    loadProducts()
  }
})
</script>

<style scoped>
.page-header { padding: 48px 0 28px; }
.page-header h1 { font-size: 32px; font-weight: 800; font-family: 'Space Grotesk', sans-serif; color: #1d4ed8; }
.page-header p { color: #64748b; font-size: 14px; margin-top: 4px; font-family: 'Manrope', sans-serif; }
.cat-divider { height: 0.5px; background: rgba(15,23,42,.05); margin: 10px 0; }
.list-layout { display: grid; grid-template-columns: 260px 1fr; gap: 32px; }
.sidebar { background: #fff; border: 0.5px solid rgba(15,23,42,.05); border-radius: 24px; padding: 24px; height: fit-content; position: sticky; top: 92px; box-shadow: 0 10px 25px -5px rgba(0,0,0,.02); }
.filter-group { margin-bottom: 22px; }
.filter-group h4 { font-size: 9px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.14em; color: #94a3b8; margin-bottom: 12px; font-family: 'Space Grotesk', sans-serif; }
.cat-tree { display: flex; flex-direction: column; gap: 2px; }
.cat-tree-item { display: flex; align-items: center; gap: 8px; padding: 9px 14px; border-radius: 9999px; cursor: pointer; font-size: 14px; font-family: 'Manrope', sans-serif; color: #64748b; transition: all .7s cubic-bezier(.4,0,.2,1); user-select: none; }
.cat-tree-item:hover { background: rgba(29,78,216,.04); color: #0F172A; }
.cat-tree-item.active { background: rgba(29,78,216,.08); color: #1d4ed8; font-weight: 600; }
.cat-tree-item.parent { font-weight: 600; color: #0F172A; }
.cat-tree-item.child { padding-inline-start: 36px; font-size: 13px; font-weight: 400; }
.cat-tree-item.child.active { font-weight: 600; }
.cat-tree-icon { font-size: 16px; }
.cat-tree-name { flex: 1; }
.cat-tree-arrow { font-size: 12px; color: #94a3b8; }
.cat-tree-dot { color: rgba(15,23,42,.08); font-size: 18px; font-weight: 700; line-height: 1; }
.cat-children { display: flex; flex-direction: column; gap: 1px; padding: 2px 0; }
.expand-enter-active, .expand-leave-active { transition: all .7s cubic-bezier(.4,0,.2,1); overflow: hidden; }
.expand-enter-from, .expand-leave-to { opacity: 0; max-height: 0; }
.expand-enter-to, .expand-leave-from { opacity: 1; max-height: 400px; }
.product-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; }
.empty-state { text-align: center; padding: 80px 0; color: #94a3b8; font-family: 'Manrope', sans-serif; }
.pagination { display: flex; justify-content: center; margin-top: 40px; }
.inq-sub { color: #64748b; font-size: 14px; margin-bottom: 8px; font-family: 'Manrope', sans-serif; }
.inq-product { font-weight: 700; margin-bottom: 16px; color: #0F172A; font-family: 'Space Grotesk', sans-serif; }
.inq-form { display: flex; flex-direction: column; gap: 10px; }
.inq-form input, .inq-form textarea, .inq-form .source-select { background: #f8fafc; border: 0.5px solid rgba(15,23,42,.05); border-radius: 12px; padding: 12px 16px; color: #0F172A; font-size: 14px; font-family: 'Manrope', sans-serif; outline: none; transition: all .7s cubic-bezier(.4,0,.2,1); width: 100%; }
.inq-form input:focus, .inq-form textarea:focus, .inq-form .source-select:focus { border-color: #1d4ed8; box-shadow: 0 0 0 2px rgba(29,78,216,.2); }
.inq-success { color: #10b981; font-weight: 600; margin-top: 12px; }

@media (max-width: 1024px) {
  .product-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .list-layout { grid-template-columns: 1fr; }
  .sidebar { position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 100; border-radius: 0; overflow-y: auto; display: none; }
  .product-grid { grid-template-columns: repeat(2, 1fr); gap: 20px; }
}
@media (max-width: 480px) {
  .product-grid { grid-template-columns: 1fr; }
}
</style>

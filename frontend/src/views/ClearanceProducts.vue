<template>
  <div class="clearance-page">
    <div class="container">
      <div class="clearance-header fade-up">
        <div class="header-content">
          <h1>{{ t('clearance.title') }}</h1>
          <p>{{ t('clearance.subtitle') }}</p>
        </div>
      </div>

      <div class="clearance-tabs fade-up">
        <button v-for="tab in tabs" :key="tab.value" class="cl-tab" :class="{ active: activeType === tab.value }" @click="switchType(tab.value)">
          {{ tab.icon }} {{ tab.label }}
        </button>
      </div>

      <div class="clearance-grid fade-up fade-up-d1">
        <ProductCard v-for="p in products" :key="p.id" :product="p" :hide-actions="hideActions" @inquire="openInquiry" />
      </div>

      <div v-if="!products.length && !loading" class="empty-state">
        <p>{{ t('product.noResult') }}</p>
      </div>

      <div class="pagination" v-if="pages > 1">
        <el-pagination background layout="prev, pager, next" :current-page="page" :page-size="12" :total="total" @current-change="handlePage" />
      </div>
    </div>

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
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDisplay } from '../utils/display'
import { useAuth } from '../store/auth'
import { ElMessage } from 'element-plus'
import api from '../api'
import ProductCard from '../components/ProductCard.vue'

const { t, locale } = useI18n()
const { localTitle } = useDisplay()
const { state: authState } = useAuth()
const hideActions = computed(() => {
  const role = authState.user?.role
  return role !== 'buyer'
})
const products = ref([])
const total = ref(0)
const pages = ref(0)
const page = ref(1)
const loading = ref(false)
const activeType = ref('')
const clearanceCategories = ref([])

const tabs = computed(() => {
  const allTab = { value: '', icon: '📦', label: locale.value === 'zh' ? '全部' : 'All' }
  const catTabs = clearanceCategories.value.map(c => ({
    value: c.name_en?.toLowerCase().replace(/\s+/g, '_') || c.id.toString(),
    icon: c.icon || '📦',
    label: locale.value === 'zh' ? c.name : c.name_en || c.name,
  }))
  return [allTab, ...catTabs]
})

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
    contact_name: u?.username || '', email: u?.email || '',
    company_name: u?.company_name || '', phone: u?.phone || '',
    quantity: null, message: '', source: u?.source || ''
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

async function loadProducts() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: 12 }
    if (activeType.value) params.clearance_type = activeType.value
    const { data } = await api.get('/clearance-products', { params })
    products.value = data.items
    total.value = data.total
    pages.value = data.pages
  } finally { loading.value = false }
}

function switchType(type) {
  activeType.value = type
  page.value = 1
  loadProducts()
}

function handlePage(p) { page.value = p; loadProducts() }

onMounted(async () => {
  try {
    const { data } = await api.get('/clearance-categories')
    clearanceCategories.value = data.categories || []
  } catch (e) { console.error(e) }
  loadProducts()
})
</script>

<style scoped>
@keyframes flowRed {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.clearance-page { padding: 48px 0; }
.clearance-header {
  background: linear-gradient(270deg, #dc2626, #f97316, #ef4444, #b91c1c, #f97316);
  background-size: 300% 300%;
  animation: flowRed 6s ease infinite;
  color: white; padding: 80px 0; margin-bottom: 40px; border-radius: 40px;
  position: relative; overflow: hidden;
}
.clearance-header::before {
  content: ''; position: absolute; width: 360px; height: 360px; border-radius: 50%;
  background: rgba(255,255,255,.08); filter: blur(80px);
  top: -20%; right: -5%; animation: orbFloat 8s ease-in-out infinite;
}
.header-content { text-align: center; position: relative; z-index: 1; color: #fff; }
.clearance-header h1 { font-size: 48px; font-weight: 800; margin-bottom: 16px; font-family: 'Space Grotesk', sans-serif; color: #fff; }
.clearance-header p { font-size: 18px; color: rgba(255,255,255,.85); font-family: 'Manrope', sans-serif; }
.clearance-tabs { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 32px; }
.cl-tab {
  padding: 10px 24px; border-radius: 9999px; border: 0.5px solid rgba(15,23,42,.05); background: #fff;
  font-size: 14px; font-weight: 700; font-family: 'Manrope', sans-serif; color: #64748b; cursor: pointer;
  transition: all .7s cubic-bezier(.4,0,.2,1);
  box-shadow: 0 10px 25px -5px rgba(0,0,0,.02);
}
.cl-tab:hover { border-color: rgba(239,68,68,.2); color: #ef4444; }
.cl-tab.active { background: linear-gradient(90deg, #dc2626, #f97316); color: #fff; border-color: transparent; box-shadow: 0 10px 30px -5px rgba(220,38,38,.2); }
.clearance-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 32px; margin-bottom: 40px; }
.empty-state { text-align: center; padding: 80px 0; color: #94a3b8; font-family: 'Manrope', sans-serif; }
.pagination { display: flex; justify-content: center; margin-top: 40px; }
.inq-sub { color: #64748b; font-size: 14px; margin-bottom: 8px; font-family: 'Manrope', sans-serif; }
.inq-product { font-weight: 700; margin-bottom: 16px; color: #0F172A; font-family: 'Space Grotesk', sans-serif; }
.inq-form { display: flex; flex-direction: column; gap: 10px; }
.inq-form input, .inq-form textarea, .inq-form .source-select { background: #f8fafc; border: 0.5px solid rgba(15,23,42,.05); border-radius: 12px; padding: 12px 16px; color: #0F172A; font-size: 14px; font-family: 'Manrope', sans-serif; outline: none; transition: all .7s cubic-bezier(.4,0,.2,1); }
.inq-form input:focus, .inq-form textarea:focus, .inq-form .source-select:focus { border-color: #1d4ed8; box-shadow: 0 0 0 2px rgba(29,78,216,.2); }
.inq-success { color: #10b981; font-weight: 600; margin-top: 12px; }

@media (max-width: 1024px) {
  .clearance-grid { grid-template-columns: repeat(3, 1fr); gap: 24px; }
}
@media (max-width: 768px) {
  .clearance-grid { grid-template-columns: repeat(2, 1fr); gap: 20px; }
  .clearance-header h1 { font-size: 32px; }
  .clearance-header { padding: 48px 0; border-radius: 28px; }
}
@media (max-width: 480px) {
  .clearance-grid { grid-template-columns: 1fr; }
}
</style>

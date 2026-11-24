<template>
  <div class="dashboard">
    <div class="container">
      <div class="dash-header fade-up">
        <h1>{{ t('factory.title') }}</h1>
        <div class="status-badge" :class="factory?.status">
          {{ factory?.status === 'approved' ? '✓ ' + t('factory.approved') : factory?.status === 'pending' ? '⏳ ' + t('factory.pending') : factory?.status === 'disabled' ? '⛔ ' + (isZh ? '已禁用' : 'Disabled') : '✗ ' + t('factory.rejected') }}
        </div>
      </div>
      <div v-if="factory?.status === 'disabled'" class="disabled-notice fade-up fade-up-d1">
        <el-icon><Warning /></el-icon>
        <span>{{ isZh ? '您的工厂已被平台禁用，所有产品已下架。如有疑问请联系平台客服。' : 'Your factory has been disabled by the platform. All products have been taken offline. Please contact support for assistance.' }}</span>
        <p v-if="factory?.description" style="margin-top:6px;font-weight:600">{{ factory.description }}</p>
      </div>
      <div v-else-if="factory?.status !== 'approved'" class="pending-notice fade-up fade-up-d1">
        <el-icon><Warning /></el-icon>
        <span>{{ t('factory.pendingNotice') }}</span>
      </div>

      <div class="stats-row fade-up fade-up-d1">
        <div class="stat-card"><span class="stat-num">{{ products.length }}</span><span>{{ t('factory.totalProducts') }}</span></div>
        <div class="stat-card"><span class="stat-num ok">{{ countByStatus('active') }}</span><span>{{ t('factory.sActive') }}</span></div>
        <div class="stat-card"><span class="stat-num blue">{{ countByStatus('pending') }}</span><span>{{ t('factory.sPending') }}</span></div>
        <div class="stat-card"><span class="stat-num warn">{{ countByStatus('draft') }}</span><span>{{ t('factory.sDraft') }}</span></div>
        <div class="stat-card"><span class="stat-num danger">{{ countByStatus('rejected') }}</span><span>{{ t('factory.sRejected') }}</span></div>
      </div>

      <div class="actions-bar fade-up fade-up-d2">
        <h2>{{ t('factory.myProducts') }}</h2>
        <div class="action-buttons">
          <router-link to="/factory/products/new">
            <el-button type="primary" :icon="Plus">{{ t('factory.addProduct') }}</el-button>
          </router-link>
          <el-button @click="showBulkUpload = true" :icon="Upload">{{ t('factory.bulkUpload') }}</el-button>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="fade-up fade-up-d3">
        <el-tab-pane :label="t('factory.products')" name="products">
          <div class="filter-bar">
            <el-radio-group v-model="productFilter" @change="loadData" size="small">
              <el-radio-button value="">{{ t('admin.all') }}</el-radio-button>
              <el-radio-button value="draft">{{ t('factory.sDraft') }}</el-radio-button>
              <el-radio-button value="pending">{{ t('factory.sPending') }}</el-radio-button>
              <el-radio-button value="active">{{ t('factory.sActive') }}</el-radio-button>
              <el-radio-button value="rejected">{{ t('factory.sRejected') }}</el-radio-button>
            </el-radio-group>
          </div>
          <el-table :data="filteredProducts" style="width:100%" v-loading="loading">
            <el-table-column :label="t('factory.addTitle')" min-width="200">
              <template #default="{ row }">
                <div class="prod-cell">
                  <img :src="getThumb(row)" class="prod-thumb" />
                  <div>
                    <div>{{ row.title }}</div>
                    <div v-if="row.title_en" style="font-size:12px;color:var(--text-secondary)">{{ row.title_en }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="moq" :label="t('product.moq')" width="80" />
            <el-table-column :label="t('factory.basePrice')" width="110">
              <template #default="{ row }"><span class="price-tag">${{ row.base_price }}</span></template>
            </el-table-column>
            <el-table-column :label="t('factory.status')" width="120">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('factory.actions')" min-width="280">
              <template #default="{ row }">
                <template v-if="row.status === 'draft'">
                  <el-button size="small" @click="$router.push(`/factory/products/${row.id}/edit`)">{{ t('factory.edit') }}</el-button>
                  <el-button size="small" type="primary" @click="submitReview(row.id)">{{ t('factory.submitReview') }}</el-button>
                </template>
                <template v-if="row.status === 'rejected'">
                  <el-button size="small" @click="$router.push(`/factory/products/${row.id}/edit`)">{{ t('factory.edit') }}</el-button>
                </template>
                <template v-if="row.status === 'pending'">
                  <el-button size="small" type="warning" @click="withdrawReview(row.id)">{{ t('factory.withdrawReview') }}</el-button>
                </template>
                <template v-if="row.status === 'active'">
                  <el-button size="small" type="warning" @click="takeOffline(row.id)">{{ t('factory.takeOffline') }}</el-button>
                </template>
                <el-popconfirm :title="t('factory.confirmDelete')" @confirm="deleteProduct(row.id)">
                  <template #reference><el-button size="small" type="danger">{{ t('factory.delete') }}</el-button></template>
                </el-popconfirm>
                <div v-if="(row.status === 'rejected' || row.status === 'draft') && row.review_note" class="reject-reason-cell">
                  <el-icon><Warning /></el-icon> {{ row.review_note }}
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane :label="t('factory.analytics')" name="analytics">
          <div class="analytics-grid">
            <div class="analytics-card">
              <div class="card-label">{{ t('factory.totalViews') }}</div>
              <div class="card-value">{{ inquiryStats?.total_views || 0 }}</div>
            </div>
            <div class="analytics-card">
              <div class="card-label">{{ t('factory.totalInquiries') }}</div>
              <div class="card-value">{{ inquiryStats?.total_inquiries || 0 }}</div>
            </div>
            <div class="analytics-card">
              <div class="card-label">{{ t('factory.conversionRate') }}</div>
              <div class="card-value">{{ conversionRate }}%</div>
            </div>
            <div class="analytics-card">
              <div class="card-label">{{ t('factory.avgResponseTime') }}</div>
              <div class="card-value">{{ inquiryStats?.avg_response_time || '-' }}</div>
            </div>
          </div>

          <div class="analytics-section">
            <h3>{{ t('factory.topProducts') }}</h3>
            <el-table :data="topProducts" style="width:100%">
              <el-table-column prop="title" :label="t('factory.product')" min-width="200" />
              <el-table-column prop="view_count" :label="t('factory.views')" width="100" />
              <el-table-column prop="inquiry_count" :label="t('factory.inquiries')" width="100" />
              <el-table-column :label="t('factory.conversionRate')" width="120">
                <template #default="{ row }">
                  {{ row.view_count > 0 ? Math.round((row.inquiry_count / row.view_count) * 100) : 0 }}%
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>

      <el-dialog v-model="showBulkUpload" :title="t('factory.bulkUpload')" width="600px">
        <div class="bulk-upload-form">
          <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
            <el-icon><Upload /></el-icon>
            <p>{{ t('factory.dragDropCsv') }}</p>
            <el-button type="primary" @click="$refs.fileInput.click()">{{ t('factory.selectFile') }}</el-button>
            <input ref="fileInput" type="file" accept=".csv" style="display:none" @change="handleFileSelect" />
          </div>
          <div v-if="uploadPreview.length" class="preview-section">
            <h4>{{ t('factory.preview') }} ({{ uploadPreview.length }})</h4>
            <el-table :data="uploadPreview" style="width:100%" max-height="300px">
              <el-table-column prop="title" :label="t('factory.addTitle')" min-width="150" />
              <el-table-column prop="moq" :label="t('product.moq')" width="80" />
              <el-table-column prop="base_price" :label="t('factory.basePrice')" width="100" />
            </el-table>
          </div>
        </div>
        <template #footer>
          <el-button @click="showBulkUpload = false">{{ t('admin.cancel') }}</el-button>
          <el-button type="primary" @click="submitBulkUpload" :loading="uploading">{{ t('factory.upload') }}</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDisplay } from '../../utils/display'
import { Plus, Warning, Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const { t } = useI18n()
const { isZh } = useDisplay()
const factory = ref(null)
const products = ref([])
const loading = ref(false)
const activeTab = ref('products')
const productFilter = ref('')
const showBulkUpload = ref(false)
const inquiryStats = ref(null)
const topProducts = ref([])
const uploadPreview = ref([])
const uploading = ref(false)

const filteredProducts = computed(() => {
  if (!productFilter.value) return products.value
  return products.value.filter(p => p.status === productFilter.value)
})

const conversionRate = computed(() => {
  if (!inquiryStats.value || inquiryStats.value.total_views === 0) return 0
  return Math.round((inquiryStats.value.total_inquiries / inquiryStats.value.total_views) * 100)
})

function statusType(s) {
  return { active: 'success', pending: 'warning', draft: 'info', rejected: 'danger' }[s] || 'info'
}

function statusLabel(s) {
  const map = { draft: 'factory.sDraft', pending: 'factory.sPending', active: 'factory.sActive', rejected: 'factory.sRejected' }
  return t(map[s]) || s
}

function countByStatus(s) {
  return products.value.filter(p => p.status === s).length
}

function getThumb(row) {
  return row.images?.length ? row.images[0] : ''
}

async function loadData() {
  loading.value = true
  try {
    const [prof, prods, stats, top] = await Promise.all([
      api.get('/factories/profile'),
      api.get('/products/factory/my'),
      api.get('/factories/analytics').catch(() => ({ data: null })),
      api.get('/factories/top-products').catch(() => ({ data: [] }))
    ])
    factory.value = prof.data
    products.value = prods.data
    inquiryStats.value = stats.data
    topProducts.value = top.data
  } finally {
    loading.value = false
  }
}

async function submitReview(id) {
  try {
    await api.post(`/products/factory/${id}/submit`)
    ElMessage.success(t('factory.submitReview') + ' ✓')
    loadData()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || 'Failed')
  }
}

async function withdrawReview(id) {
  try {
    await api.post(`/products/factory/${id}/withdraw`)
    ElMessage.success(t('factory.withdrawReview') + ' ✓')
    loadData()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || 'Failed')
  }
}

async function deleteProduct(id) {
  try {
    await api.delete(`/products/factory/${id}`)
    ElMessage.success(t('factory.delete') + ' ✓')
    loadData()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || 'Failed')
  }
}

async function takeOffline(id) {
  try {
    await api.post(`/products/factory/${id}/offline`)
    ElMessage.success(t('factory.takeOffline') + ' ✓')
    loadData()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || 'Failed')
  }
}

function handleFileSelect(e) {
  const file = e.target.files[0]
  if (file) parseCsv(file)
}

function handleDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file && file.type === 'text/csv') parseCsv(file)
}

function parseCsv(file) {
  const reader = new FileReader()
  reader.onload = (e) => {
    const csv = e.target.result
    const lines = csv.split('\n').filter(l => l.trim())
    const headers = lines[0].split(',').map(h => h.trim().toLowerCase())
    const data = []
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim())
      const row = {}
      headers.forEach((h, idx) => {
        row[h] = values[idx]
      })
      if (row.title) data.push(row)
    }
    uploadPreview.value = data
  }
  reader.readAsText(file)
}

async function submitBulkUpload() {
  if (!uploadPreview.value.length) return
  uploading.value = true
  try {
    const products = uploadPreview.value.map(p => ({
      title: p.title,
      title_en: p.title_en || '',
      description: p.description || '',
      moq: parseInt(p.moq) || 1,
      lead_time: p.lead_time || '',
      base_price: parseFloat(p.base_price) || 0,
      category_id: parseInt(p.category_id) || null,
      is_clearance: p.is_clearance === 'true' || p.is_clearance === '1',
      stock_quantity: parseInt(p.stock_quantity) || 0
    }))
    await api.post('/products/factory/bulk-create', { products })
    ElMessage.success(t('factory.bulkUpload') + ' ✓')
    uploadPreview.value = []
    showBulkUpload.value = false
    loadData()
  } catch (e) {
    ElMessage.error(e.response?.data?.error || 'Upload failed')
  } finally {
    uploading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.dashboard { padding: 32px 0; min-height: 100vh; margin-top: -96px; padding-top: 120px; }
.dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; }
.dash-header h1 { font-size: 28px; font-weight: 800; }
.status-badge { padding: 6px 16px; border-radius: 8px; font-size: 13px; font-weight: 700; }
.status-badge.approved { background: rgba(16,185,129,.1); color: var(--success); }
.status-badge.pending { background: rgba(245,158,11,.1); color: var(--warning); }
.status-badge.rejected { background: rgba(239,68,68,.1); color: var(--danger); }
.status-badge.disabled { background: rgba(156,163,175,.1); color: #6b7280; }
.pending-notice { display: flex; align-items: center; gap: 10px; background: rgba(245,158,11,.06); border: 1px solid rgba(245,158,11,.15); border-radius: 12px; padding: 16px 20px; color: var(--warning); font-size: 14px; margin-bottom: 24px; }
.disabled-notice { display: flex; flex-direction: column; gap: 4px; background: rgba(239,68,68,.04); border: 1px solid rgba(239,68,68,.12); border-radius: 12px; padding: 18px 22px; color: var(--danger); font-size: 14px; margin-bottom: 24px; }

/* Stats */
.stats-row { display: flex; gap: 14px; margin-bottom: 28px; flex-wrap: wrap; }
.stat-card {
  flex: 1; min-width: 120px; background: #fff; border: 1px solid #e5e7eb;
  border-radius: 14px; padding: 22px; text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,.04); transition: all .2s;
}
.stat-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,.07); transform: translateY(-2px); }
.stat-num { display: block; font-size: 30px; font-weight: 800; }
.stat-num.ok { color: var(--success); }
.stat-num.blue { color: var(--primary); }
.stat-num.warn { color: var(--warning); }
.stat-num.danger { color: var(--danger); }
.stat-card span:last-child { font-size: 13px; color: #9ca3af; margin-top: 4px; }

/* Tabs card */
:deep(.el-tabs) {
  background: #fff; border: 1px solid #e5e7eb; border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,.04); overflow: hidden;
}
:deep(.el-tabs__header) { margin-bottom: 0; padding: 6px 24px 0; }
:deep(.el-tabs__content) { padding: 24px; }

.actions-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.actions-bar h2 { font-size: 18px; font-weight: 700; }
.action-buttons { display: flex; gap: 8px; }
.filter-bar { margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
.prod-cell { display: flex; align-items: center; gap: 10px; }
.prod-thumb { width: 40px; height: 40px; border-radius: 8px; object-fit: cover; background: #f9fafb; }
.price-tag { font-weight: 700; color: var(--success); }
.reject-reason-cell { display: flex; align-items: center; gap: 4px; margin-top: 4px; font-size: 12px; color: var(--danger); }

/* Analytics */
.analytics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 28px; }
.analytics-card {
  background: #fff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 20px; text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.card-label { font-size: 13px; color: #9ca3af; margin-bottom: 8px; }
.card-value { font-size: 32px; font-weight: 800; color: var(--primary); }
.analytics-section { margin-bottom: 24px; }
.analytics-section h3 { font-size: 16px; font-weight: 700; margin-bottom: 16px; }

/* Bulk upload */
.bulk-upload-form { padding: 20px; }
.upload-area { border: 2px dashed #e5e7eb; border-radius: 14px; padding: 40px 20px; text-align: center; cursor: pointer; transition: all .2s; }
.upload-area:hover { border-color: var(--primary); background: rgba(37,99,235,.03); }
.upload-area svg { font-size: 48px; color: var(--primary); margin-bottom: 12px; }
.upload-area p { margin: 12px 0; color: #9ca3af; }
.preview-section { margin-top: 20px; }
.preview-section h4 { margin-bottom: 12px; font-weight: 700; }
</style>

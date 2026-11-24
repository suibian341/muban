<template>
  <div class="inquiries-page">
    <div class="container">
      <div class="dash-header fade-up">
        <h1>{{ t('admin.title') }}</h1>
        <nav class="nav-links">
          <router-link to="/admin">{{ t('admin.overview') }}</router-link>
          <router-link to="/admin/inquiries" class="nav-active">
            {{ t('admin.inquiries') }}
            <span v-if="totalUnread > 0" class="nav-badge">{{ totalUnread }}</span>
          </router-link>
        </nav>
      </div>
      <div class="filter-bar fade-up fade-up-d1">
        <el-radio-group v-model="statusFilter" @change="loadInquiries" size="small">
          <el-radio-button value="">{{ t('admin.all') }}</el-radio-button>
          <el-radio-button value="new">{{ t('admin.sNew') }}</el-radio-button>
          <el-radio-button value="contacted">{{ t('admin.sContacted') }}</el-radio-button>
          <el-radio-button value="quoted">{{ t('admin.sQuoted') }}</el-radio-button>
          <el-radio-button value="closed">{{ t('admin.sClosed') }}</el-radio-button>
        </el-radio-group>
      </div>
      <div class="table-card fade-up fade-up-d2">
        <el-table :data="inquiries" style="width:100%" v-loading="loading" class="clickable-table" @row-click="openDetail">
        <el-table-column prop="created_at" :label="t('admin.date')" width="110">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="contact_name" :label="t('admin.contactName')" width="100" />
        <el-table-column prop="company_name" :label="t('admin.companyN')" width="120" />
        <el-table-column prop="email" :label="t('admin.emailE')" width="160" show-overflow-tooltip />
        <el-table-column prop="product_title" :label="t('admin.productN')" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.is_wishlist && row.wishlist_products && row.wishlist_products.length">
              {{ row.wishlist_products.map(p => p.title).join('、') }}
              <el-tag size="small" type="warning" style="margin-left:4px">{{ t('wishlist.title') }}</el-tag>
            </span>
            <span v-else>
              {{ row.product_title || 'N/A' }}
              <el-tag v-if="row.quantity" size="small" type="info" style="margin-left:4px">{{ t('admin.quantity') }}: {{ row.quantity }}</el-tag>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="source" :label="t('admin.source')" width="90">
          <template #default="{ row }">
            <el-tag v-if="row.source" size="small" type="info">{{ row.source }}</el-tag>
            <span v-else style="color:var(--text-secondary);font-size:12px">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="t('factory.status')" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('admin.basePrice')" width="80">
          <template #default="{ row }">
            <span v-if="row.base_price" class="price-base">${{ row.base_price }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('inquiry.quoteLabel')" width="80">
          <template #default="{ row }">
            <span v-if="row.quote_price" class="price-quote">${{ row.quote_price }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('buyer.messages')" width="70" align="center">
          <template #default="{ row }">
            <div class="msg-cell" @click.stop="openDetail(row)">
              <el-badge v-if="row.unread_count" :value="row.unread_count" class="unread-badge" />
              <span v-else class="msg-icon">💬</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
      </div>
      <el-dialog v-model="showDetail" :title="t('admin.inqTitle')" width="680px" top="5vh" @close="onDetailClose">
        <div v-if="selected" class="inquiry-detail">
          <div class="detail-row"><strong>{{ t('admin.contactName') }}:</strong> {{ selected.contact_name }}</div>
          <div class="detail-row"><strong>{{ t('admin.companyN') }}:</strong> {{ selected.company_name || 'N/A' }}</div>
          <div class="detail-row"><strong>{{ t('admin.emailE') }}:</strong> {{ selected.email }}</div>
          <div class="detail-row"><strong>{{ t('admin.phone') }}:</strong> {{ selected.phone || 'N/A' }}</div>
          <!-- DETAIL_PRODUCT_PLACEHOLDER -->
          <div class="detail-row"><strong>{{ t('admin.productN') }}:</strong>
            <span v-if="!selected.wishlist_products">{{ selected.product_title || 'N/A' }}</span>
          </div>
          <div v-if="selected.wishlist_products && selected.wishlist_products.length" class="wishlist-products-box">
            <strong>{{ t('wishlist.title') }} ({{ selected.wishlist_products.length }})</strong>
            <table class="wl-table">
              <thead><tr><th style="width:50px"></th><th>{{ t('admin.productN') }}</th><th style="width:80px">{{ t('admin.quantity') }}</th></tr></thead>
              <tbody>
                <tr v-for="wp in selected.wishlist_products" :key="wp.product_id">
                  <td><img v-if="wp.image" :src="wp.image" class="wl-thumb" /></td>
                  <td>{{ wp.title }}<span v-if="wp.title_en" class="wl-en"> / {{ wp.title_en }}</span></td>
                  <td>{{ wp.quantity }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else-if="selected.quantity" class="detail-row"><strong>{{ t('admin.quantity') }}:</strong> <el-tag size="small" type="info">{{ selected.quantity }}</el-tag></div>
          <div class="detail-row message-box"><strong>{{ t('admin.message') }}:</strong><p>{{ selected.message }}</p></div>
          <div class="detail-row"><strong>{{ t('factory.status') }}:</strong> <el-tag :type="statusType(selected.status)" size="small">{{ statusLabel(selected.status) }}</el-tag></div>

          <el-divider />
          <h4 style="margin-bottom:12px;font-weight:700">{{ t('buyer.chatWithAdmin') }}</h4>
          <MessageThread
            :inquiry-id="selected.id"
            :api-prefix="'/inquiries/admin'"
            :current-user-id="currentUserId"
            viewer-role="admin"
            :is-closed="selected.status === 'closed' || selected.status === 'quoted'"
            :closed-status="selected.status"
          />

          <!-- Send quote form -->
          <div v-if="selected.status !== 'closed' && selected.status !== 'quoted'" class="quote-form-section">
            <el-divider />
            <h4 style="font-weight:700;margin-bottom:12px">{{ t('inquiry.sendQuote') }}</h4>
            <div class="quote-form">
              <el-input-number v-model="quotePrice" :min="0.01" :precision="2" :placeholder="t('inquiry.quotePrice')" size="default" style="width:180px" />
              <el-input v-model="quoteNote" :placeholder="t('inquiry.quoteNote')" size="default" style="flex:1" />
              <el-button type="warning" @click="sendQuote" :loading="quoteSending" :disabled="!quotePrice">{{ t('inquiry.sendQuote') }}</el-button>
            </div>
          </div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../../store/auth'
import { ElMessage } from 'element-plus'
import api from '../../api'
import MessageThread from '../../components/MessageThread.vue'

const { t } = useI18n()
const isZh = localStorage.getItem('lang') === 'zh' || !localStorage.getItem('lang')
const { state: authState } = useAuth()
const currentUserId = computed(() => authState.user?.id)
const inquiries = ref([])
const loading = ref(false)
const statusFilter = ref('')

const totalUnread = computed(() => inquiries.value.reduce((s, i) => s + (i.unread_count || 0), 0))
const showDetail = ref(false)
const selected = ref(null)
const quotePrice = ref(null)
const quoteNote = ref('')
const quoteSending = ref(false)

function statusType(s) { return { new: 'danger', contacted: 'warning', quoted: 'success', closed: 'info' }[s] || '' }
function statusLabel(s) {
  const map = { new: 'admin.sNew', contacted: 'admin.sContacted', quoted: 'admin.sQuoted', closed: 'admin.sClosed' }
  return t(map[s]) || s
}
function formatDate(d) {
  if (!d) return ''
  const dt = new Date(d.replace(' ', 'T') + 'Z')
  if (isNaN(dt.getTime())) return d
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`
}

async function loadInquiries() {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    const { data } = await api.get('/inquiries/admin', { params })
    inquiries.value = data.items
  } finally { loading.value = false }
}

function openDetail(row) {
  selected.value = { ...row }
  quotePrice.value = null
  quoteNote.value = ''
  showDetail.value = true
}

function onDetailClose() { loadInquiries() }

async function sendQuote() {
  if (!quotePrice.value) return
  quoteSending.value = true
  try {
    await api.post(`/inquiries/admin/${selected.value.id}/send-quote`, { price: quotePrice.value, note: quoteNote.value })
    ElMessage.success(t('inquiry.sendQuote') + ' ✓')
    quotePrice.value = null
    quoteNote.value = ''
    // Refresh status
    const { data } = await api.get('/inquiries/admin', { params: { status: '' } })
    const updated = data.items.find(i => i.id === selected.value.id)
    if (updated) selected.value = { ...updated }
  } catch (e) {
    ElMessage.error(e.response?.data?.error || 'Failed')
  } finally { quoteSending.value = false }
}

let refreshTimer = null

onMounted(() => {
  loadInquiries()
  refreshTimer = setInterval(loadInquiries, 10000)
})
onUnmounted(() => { if (refreshTimer) clearInterval(refreshTimer) })
</script>

<style scoped>
.inquiries-page .container { max-width: 1280px; }
.inquiries-page { padding: 32px 0; min-height: 100vh; margin-top: -96px; padding-top: 120px; }
.dash-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 28px; }
.dash-header h1 { font-size: 28px; font-weight: 800; }
.nav-links { display: flex; gap: 8px; }
.nav-links a {
  color: #6b7280; font-weight: 600; font-size: 14px; padding: 8px 18px;
  border-radius: 9999px; transition: all .2s;
}
.nav-links a:hover { background: #f3f4f6; color: #111827; }
.nav-links .nav-active { background: var(--primary); color: #fff; }
.nav-links .nav-active:hover { background: var(--primary-hover); }
.nav-badge {
  display: inline-flex; align-items: center; justify-content: center;
  background: #fff; color: var(--primary); font-size: 10px; font-weight: 700;
  min-width: 18px; height: 18px; border-radius: 9px; padding: 0 4px;
  margin-left: 6px; vertical-align: middle;
}
.filter-bar { margin-bottom: 20px; }
.table-card {
  background: #fff; border: 1px solid #e5e7eb; border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,.04); overflow: hidden; padding: 4px 0;
}
.inquiry-detail .detail-row { margin-bottom: 14px; font-size: 14px; }
.inquiry-detail .detail-row strong { color: #9ca3af; margin-inline-end: 8px; }
.message-box p { margin-top: 6px; padding: 14px; background: #f9fafb; border-radius: 12px; line-height: 1.7; white-space: pre-wrap; }
.wishlist-products-box { margin-bottom: 12px; }
.wishlist-products-box > strong { display: block; color: #9ca3af; font-size: 13px; margin-bottom: 8px; }
.wl-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.wl-table th { text-align: left; padding: 8px 10px; color: #9ca3af; font-weight: 600; font-size: 12px; border: none; }
.wl-table td { padding: 10px; border: none; vertical-align: middle; }
.wl-thumb { width: 40px; height: 40px; object-fit: cover; border-radius: 8px; }
.wl-en { color: #9ca3af; font-size: 12px; }
.quote-form-section { margin-top: 12px; }
.quote-form { display: flex; gap: 12px; align-items: center; }
.price-base { color: #9ca3af; font-size: 13px; }
.price-quote { color: var(--success); font-weight: 700; font-size: 13px; }
.clickable-table :deep(tr) { cursor: pointer; }
.msg-cell { display: inline-flex; align-items: center; cursor: pointer; }
.msg-icon { font-size: 18px; opacity: 0.4; transition: opacity .2s; }
.msg-cell:hover .msg-icon { opacity: 0.8; }
.unread-badge { cursor: pointer; }
</style>
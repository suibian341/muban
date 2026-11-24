<template>
  <div class="buyer-dashboard">
    <div class="container">
      <div class="page-header fade-up">
        <h1>{{ t('buyer.title') }}</h1>
      </div>

      <div class="filter-bar fade-up">
        <el-radio-group v-model="statusFilter" @change="loadInquiries" size="small">
          <el-radio-button value="">{{ t('admin.all') }}</el-radio-button>
          <el-radio-button value="new">{{ t('admin.sNew') }}</el-radio-button>
          <el-radio-button value="contacted">{{ t('admin.sContacted') }}</el-radio-button>
          <el-radio-button value="quoted">{{ t('admin.sQuoted') }}</el-radio-button>
          <el-radio-button value="closed">{{ t('admin.sClosed') }}</el-radio-button>
        </el-radio-group>
      </div>

      <div class="dash-content fade-up">
        <el-table :data="inquiries" style="width:100%" @row-click="openDetail" class="clickable-table" v-loading="loading" :table-layout="'auto'">
          <el-table-column :label="t('admin.date')" min-width="160">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column :label="t('buyer.product')" min-width="300">
            <template #default="{ row }">
              <div v-if="row.is_wishlist && row.wishlist_products && row.wishlist_products.length">
                <span class="product-link">{{ row.wishlist_products.map(p => p.title).join('、') }}</span>
                <el-tag size="small" type="warning" style="margin-left:4px">{{ t('wishlist.title') }}</el-tag>
              </div>
              <span v-else class="product-link">
                {{ localTitle(row) || '-' }}
                <el-tag v-if="row.quantity" size="small" type="info" style="margin-left:4px">{{ t('buyer.quantity') }}: {{ row.quantity }}</el-tag>
              </span>
            </template>
          </el-table-column>
          <el-table-column :label="t('buyer.status')" min-width="110">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="t('inquiry.quoteLabel')" min-width="100">
            <template #default="{ row }">
              <span v-if="row.quote_price" class="price-quote">${{ row.quote_price }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column :label="t('buyer.messages')" min-width="90" align="center">
            <template #default="{ row }">
              <el-badge v-if="row.unread_count" :value="row.unread_count" class="unread-badge" />
              <span v-else class="msg-icon">💬</span>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="!inquiries.length && !loading" class="empty-state">
          <p>{{ t('buyer.noInquiries') }}</p>
        </div>
        <div class="pagination" v-if="pages > 1">
          <el-pagination background layout="prev, pager, next" :current-page="page" :page-size="50" :total="total" @current-change="handlePage" />
        </div>
      </div>
    </div>

    <!-- Detail dialog -->
    <el-dialog v-model="showDetail" :title="t('buyer.chatWithAdmin')" width="680px" @close="onDetailClose">
      <div v-if="activeInquiry" class="inquiry-detail">
        <div v-if="activeInquiry.wishlist_products && activeInquiry.wishlist_products.length" class="wishlist-products-box">
          <strong>{{ t('wishlist.title') }} ({{ activeInquiry.wishlist_products.length }})</strong>
          <table class="wl-table">
            <thead><tr><th style="width:50px"></th><th>{{ t('buyer.product') }}</th><th style="width:80px">{{ t('buyer.quantity') }}</th></tr></thead>
            <tbody>
              <tr v-for="wp in activeInquiry.wishlist_products" :key="wp.product_id">
                <td><img v-if="wp.image" :src="wp.image" class="wl-thumb" /></td>
                <td>{{ wp.title }}<span v-if="wp.title_en" class="wl-en"> / {{ wp.title_en }}</span></td>
                <td>{{ wp.quantity }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="detail-row">
          <strong>{{ t('buyer.product') }}:</strong> {{ localTitle(activeInquiry) || '-' }}
          <el-tag v-if="activeInquiry.quantity" size="small" type="info" style="margin-left:8px">{{ t('buyer.quantity') }}: {{ activeInquiry.quantity }}</el-tag>
        </div>
        <div v-if="activeInquiry.message" class="detail-row message-box">
          <strong>{{ t('buyer.originalMessage') }}:</strong><p>{{ activeInquiry.message }}</p>
        </div>
        <div class="detail-row"><strong>{{ t('buyer.status') }}:</strong> <el-tag :type="statusType(activeInquiry.status)" size="small">{{ statusLabel(activeInquiry.status) }}</el-tag></div>

        <el-divider />
        <MessageThread
          :inquiry-id="activeInquiry.id"
          :api-prefix="'/buyer/inquiries'"
          :current-user-id="currentUserId"
          viewer-role="buyer"
          :is-closed="activeInquiry.status === 'closed' || activeInquiry.status === 'quoted'"
          :closed-status="activeInquiry.status"
          @status-changed="onStatusChanged"
        />

        <div v-if="activeInquiry.status !== 'closed' && activeInquiry.status !== 'quoted'" class="close-section">
          <el-popconfirm :title="t('inquiry.confirmClose')" @confirm="closeInquiry">
            <template #reference><el-button type="info" size="small">{{ t('inquiry.closeInquiry') }}</el-button></template>
          </el-popconfirm>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuth } from '../../store/auth'
import { ElMessage } from 'element-plus'
import api from '../../api'
import MessageThread from '../../components/MessageThread.vue'

const { t } = useI18n()
const { state: authState } = useAuth()
const currentUserId = computed(() => authState.user?.id)

const inquiries = ref([])
const total = ref(0)
const pages = ref(0)
const page = ref(1)
const loading = ref(false)
const statusFilter = ref('')
const showDetail = ref(false)
const activeInquiry = ref(null)

function statusType(s) { return { new: 'danger', contacted: 'warning', quoted: 'success', closed: 'info' }[s] || '' }
function statusLabel(s) {
  const map = { new: 'admin.sNew', contacted: 'admin.sContacted', quoted: 'admin.sQuoted', closed: 'admin.sClosed' }
  return t(map[s]) || s
}
function formatDate(d) { return d ? new Date(d).toLocaleString() : '' }
function localTitle(inq) {
  const lang = localStorage.getItem('lang') || 'zh'
  if (lang !== 'zh' && inq.product_title_en) return inq.product_title_en
  return inq.product_title || inq.product_title_en || ''
}

async function loadInquiries() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: 50 }
    if (statusFilter.value) params.status = statusFilter.value
    const { data } = await api.get('/buyer/inquiries', { params })
    inquiries.value = data.items
    total.value = data.total
    pages.value = data.pages
  } catch (e) { console.error(e) } finally { loading.value = false }
}

function handlePage(p) { page.value = p; loadInquiries() }
function openDetail(row) { activeInquiry.value = { ...row }; showDetail.value = true }
function onDetailClose() { loadInquiries() }

function onStatusChanged(newStatus) {
  if (activeInquiry.value) activeInquiry.value.status = newStatus
}

async function closeInquiry() {
  try {
    await api.post(`/buyer/inquiries/${activeInquiry.value.id}/close`)
    ElMessage.success(t('inquiry.inquiryClosed'))
    activeInquiry.value.status = 'closed'
    loadInquiries()
  } catch (e) { ElMessage.error(e.response?.data?.error || 'Failed') }
}

onMounted(() => {
  loadInquiries()
})
</script>

<style scoped>
.buyer-dashboard { padding: 32px 0; min-height: 100vh; margin-top: -96px; padding-top: 120px; }
.buyer-dashboard .container { max-width: 1280px; }
.page-header { padding: 32px 0 20px; }
.page-header h1 { font-size: 28px; font-weight: 800; }
.filter-bar { margin-bottom: 20px; }
.dash-content {
  background: #fff; border: 1px solid #e5e7eb;
  border-radius: 16px; padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,.04);
}
.clickable-table :deep(tr) { cursor: pointer; }
.product-link { color: var(--primary); font-weight: 600; }
.empty-state { text-align: center; padding: 60px 0; color: #9ca3af; }
.pagination { display: flex; justify-content: center; margin-top: 24px; }
.unread-badge { cursor: pointer; }
.msg-icon { font-size: 18px; opacity: 0.4; transition: opacity .2s; }
.clickable-table :deep(tr:hover) .msg-icon { opacity: 0.8; }
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
.close-section { margin-top: 14px; text-align: right; }
.price-quote { color: var(--success); font-weight: 700; font-size: 13px; }
</style>
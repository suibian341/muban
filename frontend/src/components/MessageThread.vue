<template>
  <div class="msg-thread">
    <div class="msg-list" ref="listRef">
      <div v-if="!messages.length" class="msg-empty">{{ t('buyer.noMessages') }}</div>
      <template v-for="m in messages" :key="m.id">
        <!-- System message -->
        <div v-if="m.msg_type === 'system'" class="msg-system">
          {{ systemText(m.content) }}
        </div>
        <!-- Quote message -->
        <div v-else-if="m.msg_type === 'quote'" class="quote-card" :class="m.sender_id === currentUserId ? 'mine' : 'theirs'">
          <div class="quote-header">
            <span class="quote-label">{{ t('inquiry.quoteLabel') }}</span>
            <span class="quote-status" :class="m.quote_status">
              {{ m.quote_status === 'pending' ? t('inquiry.quotePending') : m.quote_status === 'accepted' ? t('inquiry.quoteAccepted') : t('inquiry.quoteRejected') }}
            </span>
          </div>
          <div class="quote-price">${{ m.quote_price }}</div>
          <div v-if="m.content && m.content !== `$${m.quote_price}`" class="quote-note">{{ m.content }}</div>
          <div class="msg-meta">
            <span class="msg-sender">{{ m.sender_name }}</span>
            <span class="msg-time">{{ formatTime(m.created_at) }}</span>
          </div>
          <div v-if="m.quote_status === 'pending' && viewerRole === 'buyer'" class="quote-actions">
            <el-popconfirm :title="t('inquiry.confirmAccept')" @confirm="acceptQuote">
              <template #reference><el-button type="success" size="small">{{ t('inquiry.acceptQuote') }}</el-button></template>
            </el-popconfirm>
            <el-popconfirm :title="t('inquiry.confirmReject')" @confirm="rejectQuote">
              <template #reference><el-button type="danger" size="small" plain>{{ t('inquiry.rejectQuote') }}</el-button></template>
            </el-popconfirm>
          </div>
        </div>
        <!-- Normal text message -->
        <div v-else class="msg-bubble" :class="m.sender_id === currentUserId ? 'mine' : 'theirs'">
          <div class="msg-meta">
            <span class="msg-sender">{{ m.sender_name }}</span>
            <span class="msg-time">{{ formatTime(m.created_at) }}</span>
          </div>
          <div class="msg-content">{{ m.content }}</div>
        </div>
      </template>
    </div>
    <!-- Closed notice -->
    <div v-if="isClosed" class="msg-closed">
      {{ closedStatus === 'quoted' ? t('inquiry.inquiryQuoted') : t('inquiry.inquiryClosed') }}
    </div>
    <!-- Input -->
    <div v-else class="msg-input">
      <el-input ref="inputRef" v-model="newMsg" :placeholder="t('buyer.typeMessage')" @keyup.enter="send" :disabled="sending" />
      <el-button type="primary" @click="send" :loading="sending" :disabled="!newMsg.trim()">{{ t('buyer.send') }}</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import api from '../api'

const props = defineProps({
  inquiryId: { type: Number, required: true },
  apiPrefix: { type: String, required: true },
  currentUserId: { type: Number, required: true },
  viewerRole: { type: String, default: 'buyer' },
  isClosed: { type: Boolean, default: false },
  closedStatus: { type: String, default: '' },
})

const emit = defineEmits(['messagesLoaded', 'statusChanged'])
const { t } = useI18n()
const messages = ref([])
const newMsg = ref('')
const sending = ref(false)
const listRef = ref(null)
const inputRef = ref(null)
let pollTimer = null

const systemTextMap = {
  buyer_accepted: () => t('inquiry.buyerAccepted'),
  buyer_rejected: () => t('inquiry.buyerRejected'),
  buyer_closed: () => t('inquiry.buyerClosed'),
}
function systemText(content) {
  return systemTextMap[content] ? systemTextMap[content]() : content
}

function formatTime(iso) {
  if (!iso) return ''
  // Server stores UTC, append Z to parse as UTC then display as local
  const dt = new Date(iso.replace(' ', 'T') + 'Z')
  if (isNaN(dt.getTime())) return iso
  const y = dt.getFullYear()
  const mo = String(dt.getMonth() + 1).padStart(2, '0')
  const d = String(dt.getDate()).padStart(2, '0')
  const h = String(dt.getHours()).padStart(2, '0')
  const mi = String(dt.getMinutes()).padStart(2, '0')
  return `${y}-${mo}-${d} ${h}:${mi}`
}

async function loadMessages() {
  try {
    const { data } = await api.get(`${props.apiPrefix}/${props.inquiryId}/messages`)
    const hadNew = data.length > messages.value.length
    messages.value = data
    emit('messagesLoaded', data)
    if (hadNew) {
      await nextTick()
      scrollBottom()
      markRead()
    }
  } catch (e) { console.error(e) }
}

async function send() {
  const content = newMsg.value.trim()
  if (!content) return
  sending.value = true
  try {
    await api.post(`${props.apiPrefix}/${props.inquiryId}/messages`, { content })
    newMsg.value = ''
    await loadMessages()
    // Quick re-polls to catch auto-reply
    setTimeout(loadMessages, 1500)
    setTimeout(loadMessages, 4000)
  } catch (e) {
    ElMessage.error(e.response?.data?.error || 'Failed')
  } finally {
    sending.value = false
    await nextTick()
    inputRef.value?.focus()
  }
}

async function acceptQuote() {
  try {
    await api.post(`/buyer/inquiries/${props.inquiryId}/accept-quote`)
    ElMessage.success(t('inquiry.quoteAccepted'))
    emit('statusChanged', 'quoted')
    await loadMessages()
  } catch (e) { ElMessage.error(e.response?.data?.error || 'Failed') }
}

async function rejectQuote() {
  try {
    await api.post(`/buyer/inquiries/${props.inquiryId}/reject-quote`)
    ElMessage.success(t('inquiry.quoteRejected'))
    await loadMessages()
  } catch (e) { ElMessage.error(e.response?.data?.error || 'Failed') }
}

async function markRead() {
  try {
    await api.post(`${props.apiPrefix}/${props.inquiryId}/messages/read`)
  } catch (e) { /* ignore */ }
}

function scrollBottom() {
  if (listRef.value) listRef.value.scrollTop = listRef.value.scrollHeight
}

onMounted(() => {
  loadMessages()
  pollTimer = setInterval(loadMessages, 3000)
})
onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })
watch(() => props.inquiryId, () => { messages.value = []; loadMessages() })
</script>

<style scoped>
.msg-thread { display: flex; flex-direction: column; height: 280px; }
.msg-list { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; background: var(--surface-2); border-radius: var(--radius-lg); }
.msg-empty { text-align: center; color: var(--text-secondary); padding: 48px 0; font-size: 14px; }
.msg-bubble {
  max-width: 75%; padding: 12px 16px; border-radius: var(--radius-lg); font-size: 14px; line-height: 1.6;
  animation: fadeUp .3s cubic-bezier(.16,1,.3,1) both;
}
.msg-bubble.mine { align-self: flex-end; background: #2563eb; color: #fff; border-bottom-right-radius: 4px; box-shadow: 0 2px 8px rgba(37,99,235,.15); }
.msg-bubble.theirs { align-self: flex-start; background: var(--surface); border: 1px solid var(--border); border-bottom-left-radius: 4px; box-shadow: var(--shadow); }
.msg-meta { display: flex; justify-content: space-between; gap: 12px; font-size: 11px; opacity: 0.7; margin-bottom: 4px; }
.msg-bubble.mine .msg-meta { color: rgba(255,255,255,0.8); }
.msg-bubble.theirs .msg-meta { color: var(--text-secondary); }
.msg-content { word-break: break-word; }
.msg-system { text-align: center; font-size: 12px; color: var(--text-secondary); padding: 6px 0; }
.quote-card {
  max-width: 80%; padding: 16px 20px; border-radius: var(--radius-lg);
  border: 2px solid #f59e0b; background: linear-gradient(135deg, #fffbeb, #fef3c7);
  box-shadow: 0 4px 16px rgba(245,158,11,.1);
  animation: fadeUp .3s cubic-bezier(.16,1,.3,1) both;
}
.quote-card.mine { align-self: flex-end; }
.quote-card.theirs { align-self: flex-start; }
.quote-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.quote-label { font-weight: 700; font-size: 13px; color: #b45309; }
.quote-status { font-size: 12px; font-weight: 600; padding: 2px 8px; border-radius: 10px; }
.quote-status.pending { background: #fef3c7; color: #b45309; }
.quote-status.accepted { background: #d1fae5; color: #065f46; }
.quote-status.rejected { background: #fee2e2; color: #991b1b; }
.quote-price { font-size: 24px; font-weight: 800; color: #b45309; margin-bottom: 4px; }
.quote-note { font-size: 13px; color: var(--text-secondary); margin-bottom: 6px; }
.quote-card .msg-meta { color: var(--text-secondary); }
.quote-actions { display: flex; gap: 8px; margin-top: 10px; }
.msg-input { display: flex; gap: 10px; margin-top: 10px; }
.msg-input .el-input { flex: 1; }
.msg-closed {
  text-align: center; padding: 16px; margin-top: 14px;
  background: var(--surface-2); border-radius: var(--radius);
  color: var(--text-secondary); font-size: 14px; font-weight: 600;
  border: 1px solid var(--border);
}

@media (max-width: 768px) {
  .msg-thread { height: 60vh; }
  .msg-bubble { max-width: 85%; font-size: 13px; padding: 10px 14px; }
  .msg-list { padding: 12px; gap: 10px; }
  .msg-input { flex-direction: column; gap: 8px; }
  .quote-card { max-width: 90%; padding: 14px 16px; }
  .quote-price { font-size: 20px; }
}
</style>
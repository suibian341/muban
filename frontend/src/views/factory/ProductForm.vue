<template>
  <div class="product-form-page">
    <div class="container">
      <h1 class="fade-up">{{ isEdit ? t('factory.editTitle') : t('factory.addTitle') }}</h1>

      <!-- 拒绝理由提示 -->
      <div v-if="isEdit && productData?.review_note && productData?.status === 'rejected'" class="reject-notice fade-up">
        <el-icon><Warning /></el-icon>
        <div>
          <strong>{{ t('factory.rejectReason') }}:</strong>
          <p>{{ productData.review_note }}</p>
        </div>
      </div>

      <!-- 不可编辑提示 -->
      <div v-if="isEdit && !isEditable" class="locked-notice fade-up">
        <el-icon><Lock /></el-icon>
        <span>{{ t('factory.cannotEdit') }}</span>
      </div>

      <el-form :model="form" label-position="top" class="form-card fade-up fade-up-d1" @submit.prevent="handleSubmit">
        <el-form-item label="产品标题（中文）*" required>
          <el-input v-model="form.title" placeholder="例如：1:10比例遥控赛车" size="large" :disabled="!isEditable" />
        </el-form-item>

        <el-form-item label="Product Title (English)">
          <el-input v-model="form.title_en" placeholder="e.g. RC Racing Car 1:10 Scale" size="large" :disabled="!isEditable" />
        </el-form-item>

        <div class="form-row">
          <el-form-item :label="t('factory.category')" style="flex:1">
            <el-cascader
              v-model="selectedCategoryPath"
              :options="cascaderOptions"
              :props="{ checkStrictly: true, emitPath: false }"
              :placeholder="t('factory.selectCat')"
              size="large" style="width:100%" clearable
              @change="onCategoryChange"
              :disabled="!isEditable"
            />
          </el-form-item>
          <el-form-item :label="t('factory.moqLabel')" style="flex:1">
            <el-input-number v-model="form.moq" :min="1" size="large" style="width:100%" :disabled="!isEditable" />
          </el-form-item>
        </div>

        <div class="form-row">
          <el-form-item :label="t('factory.priceLabel')" style="flex:1">
            <el-input-number v-model="form.base_price" :min="0" :precision="2" size="large" style="width:100%" :disabled="!isEditable" />
          </el-form-item>
          <el-form-item :label="t('factory.leadTimeLabel')" style="flex:1">
            <el-input-number v-model="form.lead_time_days" :min="1" size="large" style="width:100%" :disabled="!isEditable" />
            <div class="field-hint">{{ t('factory.leadTimeUnit') }}</div>
          </el-form-item>
        </div>

        <div class="form-row">
          <el-form-item label="认证 / Certification" style="flex:1">
            <el-select v-model="form.certification" placeholder="选择认证" size="large" style="width:100%" clearable multiple :disabled="!isEditable">
              <el-option label="CE" value="CE" />
              <el-option label="FCC" value="FCC" />
              <el-option label="RoHS" value="RoHS" />
              <el-option label="ISO" value="ISO" />
              <el-option label="CCC" value="CCC" />
              <el-option label="UL" value="UL" />
            </el-select>
          </el-form-item>
          <el-form-item label="库存数量 / Stock Quantity" style="flex:1">
            <el-input-number v-model="form.stock_quantity" :min="0" size="large" style="width:100%" :disabled="!isEditable" placeholder="0" />
          </el-form-item>
        </div>

        <el-form-item>
          <el-checkbox v-model="form.is_clearance" :disabled="!isEditable">
            清仓产品 / Clearance Product
          </el-checkbox>
          <div class="field-hint">勾选后该产品将出现在清仓专区</div>
        </el-form-item>

        <el-form-item v-if="form.is_clearance" label="清仓分类 / Clearance Type">
          <el-select v-model="form.clearance_type" placeholder="可选，不选则归入清仓总区" size="large" style="width:100%" clearable :disabled="!isEditable">
            <el-option v-for="ct in clearanceTypes" :key="ct.value" :label="ct.label" :value="ct.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="产品规格 / Specifications">
          <div class="specs-editor">
            <div v-for="(val, key, idx) in form.specs" :key="idx" class="spec-row">
              <el-input :model-value="key" placeholder="参数名" size="small" style="flex:1" :disabled="!isEditable"
                @update:model-value="updateSpecKey(key, $event)" />
              <el-input :model-value="val" placeholder="参数值" size="small" style="flex:1" :disabled="!isEditable"
                @update:model-value="form.specs[key] = $event" />
              <el-button v-if="isEditable" type="danger" size="small" @click="removeSpec(key)" :icon="Delete" circle />
            </div>
            <el-button v-if="isEditable" size="small" @click="addSpec" :icon="Plus">添加规格</el-button>
          </div>
        </el-form-item>

        <el-form-item label="产品描述（中文）">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="详细产品描述" :disabled="!isEditable" />
        </el-form-item>

        <el-form-item label="Description (English)">
          <el-input v-model="form.description_en" type="textarea" :rows="3" placeholder="Detailed product description" :disabled="!isEditable" />
        </el-form-item>

        <el-form-item :label="t('factory.images')">
          <div class="image-upload-area">
            <div v-for="(img, i) in form.images" :key="i" class="img-preview">
              <img :src="img" />
              <button v-if="isEditable" class="img-remove" @click="form.images.splice(i, 1)">×</button>
            </div>
            <div v-if="isEditable" class="img-add" @click="triggerUpload">
              <el-icon size="24"><Plus /></el-icon>
              <span>{{ t('factory.upload') }}</span>
            </div>
            <input ref="fileInput" type="file" accept="image/*" hidden @change="handleUpload" />
          </div>
        </el-form-item>

        <el-form-item :label="isZh ? '描述海报' : 'Description Posters'">
          <div class="image-upload-area">
            <div v-for="(img, i) in form.poster_images" :key="i" class="img-preview poster-preview">
              <img :src="img" />
              <button v-if="isEditable" class="img-remove" @click="form.poster_images.splice(i, 1)">×</button>
            </div>
            <div v-if="isEditable" class="img-add" @click="$refs.posterInput.click()">
              <el-icon size="24"><Plus /></el-icon>
              <span>{{ isZh ? '上传海报' : 'Upload Poster' }}</span>
            </div>
            <input ref="posterInput" type="file" accept="image/*" hidden @change="handlePosterUpload" />
          </div>
          <p class="poster-hint">{{ isZh ? '海报图片将在商品详情页全屏展示' : 'Poster images will be displayed full-width on the product detail page' }}</p>
        </el-form-item>

        <el-form-item :label="t('factory.videoUrl')">
          <el-input v-model="form.video_url" placeholder="URL" :disabled="!isEditable" />
        </el-form-item>

        <el-form-item label="包装信息（中文）">
          <el-input v-model="form.packaging_info" type="textarea" :rows="2" placeholder="箱规、重量等" :disabled="!isEditable" />
        </el-form-item>

        <el-form-item label="Packaging Info (English)">
          <el-input v-model="form.packaging_info_en" type="textarea" :rows="2" placeholder="Carton size, weight, etc." :disabled="!isEditable" />
        </el-form-item>

        <el-form-item label="定制说明（中文）">
          <el-input v-model="form.customization" type="textarea" :rows="2" placeholder="Logo印刷、颜色定制、OEM/ODM等" :disabled="!isEditable" />
        </el-form-item>

        <el-form-item label="Customization (English)">
          <el-input v-model="form.customization_en" type="textarea" :rows="2" placeholder="Logo printing, color options, OEM/ODM, etc." :disabled="!isEditable" />
        </el-form-item>

        <div class="form-actions">
          <el-button @click="$router.back()" size="large">{{ t('factory.cancel') }}</el-button>
          <el-button v-if="isEditable" type="primary" native-type="submit" :loading="submitting" size="large" style="font-weight:700">
            {{ isEdit ? t('factory.updateSubmit') : t('factory.addTitle') }}
          </el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Plus, Warning, Lock, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const { t } = useI18n()
const isZh = localStorage.getItem('lang') === 'zh' || !localStorage.getItem('lang')
const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const isAdmin = computed(() => route.path.startsWith('/admin'))
const submitting = ref(false)
const fileInput = ref(null)
const categories = ref([])
const selectedCategoryPath = ref(null)
const productData = ref(null)

const form = reactive({
  title: '', title_en: '',
  description: '', description_en: '',
  images: [], poster_images: [], video_url: '',
  moq: 1, lead_time_days: 1, base_price: 1, price_unit: 'USD',
  packaging_info: '', packaging_info_en: '',
  customization: '', customization_en: '',
  category_id: null,
  is_clearance: false,
  clearance_type: '',
  certification: '',
  stock_quantity: null,
  specs: {},
})

const clearanceTypes = [
  { value: 'clearance_toys', label: '🧸 库存玩具清仓 / Clearance Toys' },
  { value: 'clearance_rc', label: '🎮 遥控类库存 / Clearance RC' },
  { value: 'clearance_drones', label: '🚁 无人机库存 / Clearance Drones' },
  { value: 'clearance_bulk', label: '📦 大宗混装库存 / Clearance Bulk' },
  { value: 'closeout_stock', label: '🏷️ 整单尾货 / Closeout Stock' },
]

// ★ 管理员和开发者可编辑任何状态，工厂只能编辑 draft 和 rejected
const isEditable = computed(() => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (user?.role === 'admin' || user?.role === 'dev') return true
  if (!isEdit.value) return true
  if (!productData.value) return true
  return productData.value.status === 'draft' || productData.value.status === 'rejected'
})

const cascaderOptions = computed(() => {
  return categories.value.map(parent => ({
    value: parent.id,
    label: `${parent.icon || ''} ${parent.name} / ${parent.name_en || parent.name}`,
    children: parent.children && parent.children.length
      ? parent.children.map(child => ({
          value: child.id,
          label: `${child.name} / ${child.name_en || child.name}`,
        }))
      : undefined,
  }))
})

function onCategoryChange(val) { form.category_id = val }
function triggerUpload() { fileInput.value.click() }

function addSpec() {
  const key = `spec_${Object.keys(form.specs).length + 1}`
  form.specs[key] = ''
}

function removeSpec(key) {
  delete form.specs[key]
}

function updateSpecKey(oldKey, newKey) {
  if (oldKey === newKey) return
  const val = form.specs[oldKey]
  delete form.specs[oldKey]
  form.specs[newKey] = val
}

async function handleUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const { data } = await api.post('/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    form.images.push(data.url)
  } catch { ElMessage.error('Upload failed') }
  e.target.value = ''
}
async function handlePosterUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const { data } = await api.post('/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    form.poster_images.push(data.url)
  } catch { ElMessage.error('Upload failed') }
  e.target.value = ''
}

async function handleSubmit() {
  if (!isEditable.value) return
  submitting.value = true
  const payload = {
    ...form,
    lead_time: `${form.lead_time_days}天`,
    certification: Array.isArray(form.certification) ? form.certification.join(',') : form.certification,
    clearance_type: form.is_clearance ? form.clearance_type : '',
  }
  delete payload.lead_time_days
  try {
    if (isEdit.value) {
      if (isAdmin.value) {
        await api.put(`/admin/products/${route.params.id}`, payload)
      } else {
        await api.put(`/products/factory/${route.params.id}`, payload)
      }
    } else {
      await api.post('/products/factory', payload)
    }
    ElMessage.success(isEdit.value ? (isZh ? '保存成功' : 'Saved') : (isZh ? '添加成功' : 'Created'))
    router.push(isAdmin.value ? '/admin' : '/factory')
  } catch (e) {
    ElMessage.error(e.response?.data?.error || 'Failed')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const { data } = await api.get('/categories')
  categories.value = data

  if (isEdit.value) {
    // ★ 管理员用 admin 接口，工厂用 factory 接口
    const endpoint = isAdmin.value ? `/admin/products/${route.params.id}` : `/products/factory/${route.params.id}`
    const { data: prod } = await api.get(endpoint)
    productData.value = prod
    Object.assign(form, {
      title: prod.title || '',
      title_en: prod.title_en || '',
      description: prod.description || '',
      description_en: prod.description_en || '',
      images: prod.images || [],
      poster_images: prod.poster_images || [],
      video_url: prod.video_url || '',
      moq: prod.moq,
      lead_time_days: parseInt(prod.lead_time) || 1,
      base_price: prod.base_price,
      packaging_info: prod.packaging_info || '',
      packaging_info_en: prod.packaging_info_en || '',
      customization: prod.customization || '',
      customization_en: prod.customization_en || '',
      category_id: prod.category_id,
      is_clearance: prod.is_clearance || false,
      clearance_type: prod.clearance_type || '',
      certification: prod.certification ? prod.certification.split(',') : [],
      stock_quantity: prod.stock_quantity,
      specs: prod.specs || {},
    })
    selectedCategoryPath.value = prod.category_id
  }
})
</script>

<style scoped>
.product-form-page { padding: 32px 0; }
.product-form-page h1 { font-size: 28px; font-weight: 800; margin-bottom: 24px; }
.form-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-xl); padding: 40px; max-width: 800px;
  box-shadow: var(--shadow);
  transition: box-shadow var(--transition-base);
}
.form-card:hover { box-shadow: var(--shadow-lg); }
.form-row { display: flex; gap: 16px; }
.field-hint { font-size: 11px; color: var(--text-secondary); margin-top: 4px; }
.reject-notice {
  display: flex; align-items: flex-start; gap: 10px;
  background: rgba(220,38,38,.04); border: 1px solid rgba(220,38,38,.15);
  border-radius: var(--radius-lg); padding: 18px 22px; margin-bottom: 20px;
  color: var(--danger); font-size: 14px;
}
.reject-notice strong { display: block; margin-bottom: 4px; }
.reject-notice p { margin: 0; color: var(--text); }
.locked-notice {
  display: flex; align-items: center; gap: 8px;
  background: var(--surface-2); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 16px 22px; margin-bottom: 20px;
  color: var(--text-secondary); font-size: 14px;
}
.image-upload-area { display: flex; flex-wrap: wrap; gap: 12px; }
.img-preview {
  position: relative; width: 100px; height: 100px;
  border-radius: var(--radius); overflow: hidden; border: 1px solid var(--border);
  transition: all var(--transition-fast);
}
.img-preview:hover { box-shadow: var(--shadow); transform: scale(1.03); }
.img-preview img { width: 100%; height: 100%; object-fit: cover; }
.poster-preview { width: 160px; height: 200px; border-radius: 12px; }
.poster-hint { font-size: 12px; color: #94a3b8; margin-top: 8px; }
.img-remove {
  position: absolute; top: 4px; right: 4px; width: 22px; height: 22px; border-radius: 50%;
  background: var(--danger); color: #fff; border: none; cursor: pointer; font-size: 14px;
  line-height: 22px; text-align: center; opacity: 0; transition: opacity var(--transition-fast);
}
.img-preview:hover .img-remove { opacity: 1; }
.img-add {
  width: 100px; height: 100px; border: 2px dashed var(--border);
  border-radius: var(--radius); display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 4px; cursor: pointer;
  color: var(--text-secondary); font-size: 12px;
  transition: all var(--transition-base);
}
.img-add:hover { border-color: var(--primary); color: var(--primary); background: rgba(37,99,235,.03); }
.form-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 20px; }
.specs-editor { width: 100%; display: flex; flex-direction: column; gap: 8px; }
.spec-row { display: flex; gap: 8px; align-items: center; }
:deep(.el-cascader-panel) { background: var(--surface); border-color: var(--border); }
:deep(.el-cascader-node__label) { color: var(--text); }
:deep(.el-cascader-node:not(.is-disabled):hover) { background: var(--surface-2); }
:deep(.el-cascader-node.in-active-path) { color: var(--primary); }
</style>

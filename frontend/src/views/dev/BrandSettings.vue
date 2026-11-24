<template>
  <div class="brand-settings">
    <div class="page-header">
      <el-button @click="$router.back()" icon="el-icon-arrow-left">返回</el-button>
      <h1>🎨 品牌设置</h1>
    </div>

    <el-card>
      <el-form :model="form" label-width="120px">
        <!-- Logo上传（可选） -->
        <el-form-item label="品牌Logo">
          <div class="logo-upload">
            <el-input v-model="form.brand_logo" placeholder="输入Logo URL或上传图片（可选，不上传则使用默认图标）">
              <template #append>
                <el-upload
                  action="/api/upload"
                  :headers="uploadHeaders"
                  :show-file-list="false"
                  :on-success="(res) => handleUploadSuccess(res, 'brand_logo')"
                  accept="image/*"
                >
                  <el-button>上传</el-button>
                </el-upload>
              </template>
            </el-input>
            <div v-if="form.brand_logo" class="logo-preview">
              <img :src="form.brand_logo" alt="Brand Logo" />
            </div>
            <div v-else class="logo-preview default">
              <div class="default-icon">C</div>
            </div>
          </div>
          <div class="form-tip">建议尺寸：200x60px，格式：PNG/SVG。不上传则使用默认图标"C"</div>
        </el-form-item>

        <!-- 品牌名称（多语言） -->
        <el-form-item label="品牌名称">
          <div class="lang-inputs">
            <div v-for="lang in languages" :key="lang.code" class="lang-input-row">
              <span class="lang-label">{{ lang.name }}</span>
              <el-input v-model="form[`brand_name_${lang.code}`]" :placeholder="`输入${lang.name}品牌名称`" />
            </div>
          </div>
        </el-form-item>

        <!-- 品牌描述（多语言） -->
        <el-form-item label="品牌描述">
          <div class="lang-inputs">
            <div v-for="lang in languages" :key="lang.code" class="lang-input-row">
              <span class="lang-label">{{ lang.name }}</span>
              <el-input
                v-model="form[`brand_desc_${lang.code}`]"
                type="textarea"
                :rows="2"
                :placeholder="`输入${lang.name}品牌描述`"
              />
            </div>
          </div>
        </el-form-item>

        <!-- 预览 -->
        <el-form-item label="预览效果">
          <div class="preview-section">
            <div class="preview-header">
              <div class="preview-logo">
                <img v-if="form.brand_logo" :src="form.brand_logo" alt="Logo" />
                <div v-else class="preview-default-icon">C</div>
              </div>
              <div class="preview-text">
                <div class="preview-brand-name">{{ form.brand_name_zh || '品牌名称' }}</div>
                <div class="preview-brand-desc">{{ form.brand_desc_zh || '品牌描述' }}</div>
              </div>
            </div>
          </div>
        </el-form-item>

        <!-- 保存按钮 -->
        <el-form-item>
          <el-button type="primary" @click="save" :loading="saving">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const uploadHeaders = { Authorization: `Bearer ${localStorage.getItem('token')}` }

const languages = [
  { code: 'zh', name: '中文' },
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Español' },
  { code: 'ar', name: 'العربية' },
  { code: 'ru', name: 'Русский' }
]

const form = reactive({
  brand_logo: '',
  brand_name_zh: '',
  brand_name_en: '',
  brand_name_es: '',
  brand_name_ar: '',
  brand_name_ru: '',
  brand_desc_zh: '',
  brand_desc_en: '',
  brand_desc_es: '',
  brand_desc_ar: '',
  brand_desc_ru: ''
})

const saving = ref(false)

onMounted(async () => {
  try {
    const { data } = await api.get('/dev/branding')
    Object.assign(form, data)
  } catch (e) {
    console.error('Failed to load branding:', e)
  }
})

function handleUploadSuccess(res, field) {
  if (res.url) {
    form[field] = res.url
    ElMessage.success('上传成功')
  }
}

async function save() {
  saving.value = true
  try {
    await api.put('/dev/branding', form)
    ElMessage.success('保存成功')
    // 触发全局事件通知Header更新
    window.dispatchEvent(new CustomEvent('branding-updated'))
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.brand-settings {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.logo-upload {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.logo-preview {
  width: 200px;
  height: 80px;
  border: 2px dashed #ddd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
}

.logo-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.logo-preview.default,
.preview-default-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 32px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.default-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}

.lang-inputs {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.lang-input-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.lang-label {
  min-width: 80px;
  font-size: 14px;
  font-weight: 500;
  color: #666;
}

.preview-section {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
  background: #f9fafb;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.preview-logo {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-logo img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.preview-default-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  font-size: 24px;
}

.preview-text {
  flex: 1;
}

.preview-brand-name {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 4px;
}

.preview-brand-desc {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
}
</style>

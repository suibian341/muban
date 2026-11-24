<template>
  <div class="footer-editor">
    <div class="page-header">
      <el-button @click="$router.back()">返回</el-button>
      <h1>页脚内容编辑</h1>
    </div>

    <el-tabs v-model="activeSection" type="border-card">
      <el-tab-pane v-for="section in sections" :key="section.key" :label="section.label" :name="section.key">
        <el-tabs v-model="activeLang" type="card" class="lang-tabs">
          <el-tab-pane v-for="lang in languages" :key="lang.code" :label="lang.name" :name="lang.code">
            <div class="editor-wrapper">
              <QuillEditor
                :ref="el => setEditorRef(section.key, lang.code, el)"
                theme="snow"
                :content="form[`${section.key}_${lang.code}`]"
                content-type="html"
                :toolbar="toolbarOptions"
                @update:content="val => form[`${section.key}_${lang.code}`] = val"
                style="min-height: 250px;"
              />
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-tab-pane>
    </el-tabs>

    <!-- 预览 -->
    <el-card class="preview-card">
      <template #header>
        <span>预览（{{ currentSectionLabel }} - {{ currentLangName }}）</span>
      </template>
      <div class="preview-content" v-html="currentPreview"></div>
    </el-card>

    <!-- 保存按钮 -->
    <div class="save-bar">
      <el-button type="primary" size="large" @click="save" :loading="saving">保存所有设置</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import api from '../../api'

const activeSection = ref('faq')
const activeLang = ref('zh')

const sections = [
  { key: 'faq', label: '常见问题 FAQ' },
  { key: 'shipping', label: '物流说明 Shipping' },
  { key: 'terms', label: '服务条款 Terms' },
  { key: 'about', label: '关于我们 About Us' }
]

const languages = [
  { code: 'zh', name: '中文' },
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Español' },
  { code: 'ar', name: 'العربية' },
  { code: 'ru', name: 'Русский' }
]

const toolbarOptions = [
  [{ header: [1, 2, 3, false] }],
  ['bold', 'italic', 'underline', 'strike'],
  [{ color: [] }, { background: [] }],
  [{ list: 'ordered' }, { list: 'bullet' }],
  [{ align: [] }],
  ['link', 'image'],
  ['clean']
]

const form = reactive({
  faq_zh: '', faq_en: '', faq_es: '', faq_ar: '', faq_ru: '',
  shipping_zh: '', shipping_en: '', shipping_es: '', shipping_ar: '', shipping_ru: '',
  terms_zh: '', terms_en: '', terms_es: '', terms_ar: '', terms_ru: '',
  about_zh: '', about_en: '', about_es: '', about_ar: '', about_ru: ''
})

const editorRefs = {}
function setEditorRef(section, lang, el) {
  editorRefs[`${section}_${lang}`] = el
}

const saving = ref(false)

const currentSectionLabel = computed(() => {
  const s = sections.find(s => s.key === activeSection.value)
  return s ? s.label : ''
})

const currentLangName = computed(() => {
  const l = languages.find(l => l.code === activeLang.value)
  return l ? l.name : ''
})

const currentPreview = computed(() => {
  const key = `${activeSection.value}_${activeLang.value}`
  return form[key] || '<span style="color:#999">暂无内容</span>'
})

onMounted(async () => {
  try {
    const { data } = await api.get('/dev/footer')
    Object.assign(form, data)
  } catch (e) {
    console.error('Failed to load footer:', e)
  }
})

async function save() {
  saving.value = true
  try {
    await api.put('/dev/footer', form)
    ElMessage.success('保存成功')
    window.dispatchEvent(new CustomEvent('footer-updated'))
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.footer-editor {
  padding: 24px;
  max-width: 1100px;
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

.lang-tabs {
  margin-top: 8px;
}

.editor-wrapper {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.editor-wrapper :deep(.ql-toolbar) {
  border: none;
  border-bottom: 1px solid #dcdfe6;
  background: #fafafa;
}

.editor-wrapper :deep(.ql-container) {
  border: none;
  font-size: 14px;
}

.editor-wrapper :deep(.ql-editor) {
  min-height: 250px;
}

.preview-card {
  margin-top: 24px;
}

.preview-content {
  padding: 16px;
  font-size: 14px;
  line-height: 1.8;
  color: #333;
}

.preview-content :deep(h1) { font-size: 24px; font-weight: 700; margin: 16px 0 8px; }
.preview-content :deep(h2) { font-size: 20px; font-weight: 700; margin: 14px 0 8px; }
.preview-content :deep(h3) { font-size: 17px; font-weight: 600; margin: 12px 0 6px; }
.preview-content :deep(p) { margin: 8px 0; }
.preview-content :deep(ul), .preview-content :deep(ol) { padding-left: 20px; }
.preview-content :deep(li) { margin: 4px 0; }

.save-bar {
  margin-top: 24px;
  text-align: center;
}
</style>

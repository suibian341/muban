<template>
  <div class="static-page">
    <div class="container">
      <h1>{{ t('footer.aboutUs') }}</h1>
      <div class="content-text" v-html="aboutContent"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '../api'

const { t, locale } = useI18n()
const footerData = ref({
  about_zh: '', about_en: '', about_es: '', about_ar: '', about_ru: ''
})

const aboutContent = computed(() => {
  const key = `about_${locale.value}`
  return footerData.value[key] || footerData.value.about_zh || ''
})

onMounted(async () => {
  try {
    const { data } = await api.get('/site-settings')
    for (const key of Object.keys(footerData.value)) {
      if (data[key]) footerData.value[key] = data[key]
    }
  } catch (e) {
    console.error('Failed to load about:', e)
  }
})
</script>

<style scoped>
.static-page { padding: 48px 0; }
.static-page h1 { font-size: 32px; font-weight: 800; margin-bottom: 32px; }
.content-text { font-size: 15px; line-height: 1.8; color: var(--text-secondary); white-space: pre-wrap; }
</style>

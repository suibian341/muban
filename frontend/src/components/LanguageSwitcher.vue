<template>
  <el-dropdown trigger="click" @command="switchLang">
    <button class="lang-trigger">
      <span class="lang-flag">{{ current.flag }}</span>
      <span class="lang-name">{{ current.label }}</span>
    </button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item v-for="l in langs" :key="l.code" :command="l.code">
          {{ l.flag }} {{ l.label }}
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLanguage } from '../i18n'

const { locale } = useI18n({ useScope: 'global' })

const langs = [
  { code: 'zh', label: '中文', flag: '🇨🇳' },
  { code: 'en', label: 'English', flag: '🇺🇸' },
  { code: 'es', label: 'Español', flag: '🇪🇸' },
  { code: 'ar', label: 'العربية', flag: '🇸🇦' },
  { code: 'ru', label: 'Русский', flag: '🇷🇺' },
]

const current = computed(() => langs.find(l => l.code === locale.value) || langs[1])

function switchLang(code) {
  setLanguage(code)
}
</script>

<style scoped>
.lang-trigger {
  display: flex; align-items: center; gap: 6px;
  background: #fff; border: 0.5px solid rgba(15,23,42,.1);
  border-radius: 12px; padding: 8px 14px;
  color: #0F172A; cursor: pointer; font-size: 12px;
  font-weight: 700; font-family: 'Manrope', sans-serif;
  transition: all .3s;
}
.lang-trigger:hover { border-color: #1d4ed8; background: #fff; }
.lang-flag { font-size: 15px; }
.lang-name { font-weight: 700; letter-spacing: 0.02em; }
</style>

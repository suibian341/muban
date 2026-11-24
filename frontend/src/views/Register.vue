<template>
  <div class="auth-page">
    <div class="auth-bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
    </div>
    <div class="auth-card register-card fade-up">
      <h2>{{ t('auth.regTitle') }}</h2>
      <p class="auth-sub">{{ t('auth.regSub') }}</p>
      <div v-if="errorMsg" class="auth-error">
        <span class="error-icon">!</span>
        {{ errorMsg }}
      </div>
      <div v-if="successMsg" class="auth-success">
        {{ successMsg }}
      </div>
      <form @submit.prevent="handleRegister">
        <div class="form-grid">
          <el-input v-model="form.username" :placeholder="t('auth.loginUsername')" size="large" />
          <el-input v-model="form.password" :placeholder="t('auth.loginPassword')" type="password" size="large" show-password />
          <el-input v-model="form.company_name" :placeholder="t('auth.companyName')" size="large" />
          <el-input v-model="form.contact_person" :placeholder="t('auth.contactPerson')" size="large" />
          <el-input v-model="form.email" :placeholder="t('auth.email')" size="large" />
          <el-select v-model="form.country" :placeholder="t('auth.buyerCountry')" size="large" filterable style="width:100%">
            <el-option v-for="c in countries" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </div>
        <el-input v-model="form.phone" :placeholder="t('auth.phone')" size="large" />
        <el-input v-model="form.address" :placeholder="t('auth.address')" size="large" />
        <el-input v-model="form.description" type="textarea" :rows="3" :placeholder="t('auth.desc')" size="large" />
        <div class="cert-upload">
          <label class="cert-label">{{ isZh ? '认证资料（CE/ISO等）' : 'Certification Documents (CE/ISO etc.)' }}</label>
          <div class="cert-files">
            <div v-for="(f, i) in form.certification_files" :key="i" class="cert-file">
              <span>{{ f.split('/').pop() }}</span>
              <button type="button" class="cert-remove" @click="form.certification_files.splice(i, 1)">×</button>
            </div>
            <el-button size="small" @click="$refs.certInput.click()">{{ isZh ? '上传文件' : 'Upload File' }}</el-button>
            <input ref="certInput" type="file" accept=".pdf,.jpg,.jpeg,.png" hidden @change="uploadCert" />
          </div>
        </div>
        <el-button type="primary" native-type="submit" :loading="loading" size="large" style="width:100%;font-weight:700">
          {{ t('auth.submitReg') }}
        </el-button>
      </form>
      <p class="auth-footer">{{ t('auth.alreadyReg') }} <router-link to="/login">{{ t('auth.signIn') }}</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import api from '../api'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const form = reactive({ username: '', password: '', company_name: '', contact_person: '', email: '', country: '', phone: '', address: '', description: '', certification_files: [] })
const isZh = localStorage.getItem('lang') === 'zh' || !localStorage.getItem('lang')
const errorMsg = ref('')
const successMsg = ref('')

const countries = [
  { value: 'CN', label: '🇨🇳 中国 / China' },
  { value: 'US', label: '🇺🇸 United States' },
  { value: 'GB', label: '🇬🇧 United Kingdom' },
  { value: 'DE', label: '🇩🇪 Germany' },
  { value: 'FR', label: '🇫🇷 France' },
  { value: 'ES', label: '🇪🇸 Spain' },
  { value: 'IT', label: '🇮🇹 Italy' },
  { value: 'RU', label: '🇷🇺 Russia' },
  { value: 'JP', label: '🇯🇵 Japan' },
  { value: 'KR', label: '🇰🇷 South Korea' },
  { value: 'IN', label: '🇮🇳 India' },
  { value: 'BR', label: '🇧🇷 Brazil' },
  { value: 'MX', label: '🇲🇽 Mexico' },
  { value: 'AU', label: '🇦🇺 Australia' },
  { value: 'CA', label: '🇨🇦 Canada' },
  { value: 'SA', label: '🇸🇦 Saudi Arabia' },
  { value: 'AE', label: '🇦🇪 UAE' },
  { value: 'TR', label: '🇹🇷 Turkey' },
  { value: 'TH', label: '🇹🇭 Thailand' },
  { value: 'VN', label: '🇻🇳 Vietnam' },
  { value: 'MY', label: '🇲🇾 Malaysia' },
  { value: 'ID', label: '🇮🇩 Indonesia' },
  { value: 'PH', label: '🇵🇭 Philippines' },
  { value: 'PK', label: '🇵🇰 Pakistan' },
  { value: 'BD', label: '🇧🇩 Bangladesh' },
  { value: 'NG', label: '🇳🇬 Nigeria' },
  { value: 'EG', label: '🇪🇬 Egypt' },
  { value: 'ZA', label: '🇿🇦 South Africa' },
  { value: 'PL', label: '🇵🇱 Poland' },
  { value: 'NL', label: '🇳🇱 Netherlands' },
  { value: 'CL', label: '🇨🇱 Chile' },
  { value: 'CO', label: '🇨🇴 Colombia' },
  { value: 'AR', label: '🇦🇷 Argentina' },
  { value: 'PE', label: '🇵🇪 Peru' },
  { value: 'OTHER', label: '🌍 Other' },
]

async function uploadCert(e) {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const { data } = await api.post('/upload/public', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    form.certification_files.push(data.url)
    ElMessage.success(file.name + ' ✓')
  } catch { ElMessage.error('Upload failed') }
  e.target.value = ''
}

async function handleRegister() {
  errorMsg.value = ''
  successMsg.value = ''
  if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errorMsg.value = isZh ? '请输入正确的邮箱格式' : 'Please enter a valid email address'
    return
  }
  loading.value = true
  try {
    await api.post('/auth/register', form)
    successMsg.value = t('auth.regSubmitted')
    setTimeout(() => router.push('/login'), 2000)
  } catch (e) {
    const resp = e.response?.data
    if (resp?.error_type === 'username_exists') {
      errorMsg.value = t('auth.usernameExists')
    } else if (resp?.error_type === 'email_exists') {
      errorMsg.value = t('auth.emailExists')
    } else {
      errorMsg.value = resp?.error || t('auth.loginFailed')
    }
  } finally { loading.value = false }
}
</script>

<style scoped>
.auth-page {
  display: flex; align-items: center; justify-content: center; padding: 48px 0; min-height: 100vh;
  position: relative; overflow: hidden;
  background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 35%, #3b82f6 65%, #60a5fa 100%);
  background-size: 300% 300%;
  animation: gradientShift 8s ease infinite;
  margin-top: -96px; padding-top: 120px;
}
.auth-bg { position: absolute; inset: 0; overflow: hidden; }
.orb { position: absolute; border-radius: 50%; animation: orbFloat 10s ease-in-out infinite; }
.orb-1 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(96,165,250,.4) 0%, transparent 70%); top: -20%; left: -10%; filter: blur(60px); animation-duration: 8s; }
.orb-2 { width: 400px; height: 400px; background: radial-gradient(circle, rgba(147,51,234,.25) 0%, transparent 70%); bottom: -15%; right: -8%; filter: blur(70px); animation-delay: -3s; animation-duration: 11s; }
.orb-3 { width: 300px; height: 300px; background: radial-gradient(circle, rgba(255,255,255,.1) 0%, transparent 70%); top: 40%; right: 25%; filter: blur(50px); animation-delay: -6s; animation-duration: 9s; }
.register-card {
  width: 580px; position: relative; z-index: 1;
  background: #fff; border: none; border-radius: var(--radius-xl); padding: 44px;
  box-shadow: 0 20px 60px rgba(0,0,0,.15);
}
.register-card h2 { font-size: 26px; font-weight: 800; margin-bottom: 6px; color: var(--text); }
.auth-sub { color: var(--text-secondary); font-size: 14px; margin-bottom: 28px; }
.auth-error {
  display: flex; align-items: center; gap: 10px;
  background: #fef2f2; border: 1px solid #fecaca; border-radius: 12px;
  padding: 12px 16px; margin-bottom: 20px;
  color: #dc2626; font-size: 13px; font-weight: 500; line-height: 1.5;
}
.error-icon {
  width: 20px; height: 20px; border-radius: 50%; background: #dc2626; color: #fff;
  font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.auth-success {
  background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 12px;
  padding: 12px 16px; margin-bottom: 20px;
  color: #065f46; font-size: 13px; font-weight: 500; line-height: 1.5;
}
.register-card form { display: flex; flex-direction: column; gap: 16px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.register-card :deep(.el-button--primary) { background: var(--gradient-primary); border: none; box-shadow: 0 4px 16px rgba(37,99,235,.3); }
.register-card :deep(.el-button--primary:hover) { box-shadow: 0 8px 24px rgba(37,99,235,.45); transform: translateY(-1px); }
.auth-footer { text-align: center; margin-top: 24px; font-size: 13px; color: var(--text-secondary); }
.auth-footer a { color: var(--primary); font-weight: 600; }
.cert-upload { margin-top: 4px; }
.cert-label { font-size: 13px; color: var(--text-secondary); display: block; margin-bottom: 8px; }
.cert-files { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.cert-file { display: flex; align-items: center; gap: 6px; background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--radius); padding: 4px 10px; font-size: 12px; }
.cert-remove { background: none; border: none; color: var(--danger); cursor: pointer; font-size: 14px; }
</style>

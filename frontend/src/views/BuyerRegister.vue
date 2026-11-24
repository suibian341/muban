<template>
  <div class="auth-page">
    <div class="auth-bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
    </div>
    <div class="auth-card register-card fade-up">
      <h2>{{ t('auth.buyerRegTitle') }}</h2>
      <p class="auth-sub">{{ t('auth.buyerRegSub') }}</p>
      <div v-if="errorMsg" class="auth-error">
        <span class="error-icon">!</span>
        {{ errorMsg }}
      </div>
      <div v-if="successMsg" class="auth-success">
        {{ successMsg }}
      </div>
      <form @submit.prevent="handleRegister">
        <div class="form-grid">
          <el-input v-model="form.username" :placeholder="t('auth.username') + ' *'" size="large" :prefix-icon="UserIcon" />
          <el-input v-model="form.email" :placeholder="t('auth.email') + ' *'" size="large" type="email" />
          <el-input v-model="form.password" :placeholder="t('auth.password') + ' *'" type="password" size="large" :prefix-icon="Lock" show-password />
          <el-input v-model="form.password2" :placeholder="t('auth.confirmPassword')" type="password" size="large" :prefix-icon="Lock" show-password />
          <el-input v-model="form.company_name" :placeholder="t('auth.companyName')" size="large" />
          <el-select v-model="form.country" :placeholder="t('auth.buyerCountry')" size="large" filterable style="width:100%">
            <el-option v-for="c in countries" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </div>
        <el-input v-model="form.phone" :placeholder="t('auth.phone')" size="large" />
        <el-select v-model="form.source" :placeholder="isZh ? '您从哪里了解到我们？' : 'How did you find us?'" size="large" clearable style="width:100%">
          <el-option label="TikTok" value="tiktok" />
          <el-option label="Facebook" value="facebook" />
          <el-option label="Google" value="google" />
          <el-option label="Instagram" value="instagram" />
          <el-option label="LinkedIn" value="linkedin" />
          <el-option :label="isZh ? '朋友推荐' : 'Referral'" value="referral" />
          <el-option :label="isZh ? '其他' : 'Other'" value="other" />
        </el-select>
        <el-button type="primary" native-type="submit" :loading="loading" size="large" style="width:100%;font-weight:700;margin-top:8px">
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
import { User as UserIcon, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../api'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const form = reactive({ username: '', password: '', password2: '', email: '', company_name: '', country: '', phone: '', source: '' })
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

async function handleRegister() {
  errorMsg.value = ''
  successMsg.value = ''
  if (form.password !== form.password2) {
    errorMsg.value = t('auth.passwordMismatch')
    return
  }
  loading.value = true
  try {
    const { password2, ...payload } = form
    await api.post('/auth/register/buyer', payload)
    successMsg.value = t('auth.regSuccess')
    setTimeout(() => router.push('/login'), 2000)
  } catch (e) {
    const resp = e.response?.data
    if (resp?.error_type === 'username_exists') {
      errorMsg.value = t('auth.usernameExists')
    } else if (resp?.error_type === 'email_exists') {
      errorMsg.value = t('auth.emailExists')
    } else if (resp?.error_type === 'missing_fields') {
      errorMsg.value = isZh ? '请填写用户名和密码' : 'Username and password are required'
    } else {
      errorMsg.value = resp?.error || t('auth.loginFailed')
    }
  } finally { loading.value = false }
}
</script>

<style scoped>
.auth-page {
  display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 48px 0;
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
.auth-card {
  width: 420px; position: relative; z-index: 1;
  background: #fff; border: none; border-radius: var(--radius-xl); padding: 44px;
  box-shadow: 0 20px 60px rgba(0,0,0,.15);
}
.register-card { width: 540px; }
.auth-card h2 { font-size: 26px; font-weight: 800; margin-bottom: 6px; color: var(--text); }
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
.auth-card form { display: flex; flex-direction: column; gap: 16px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.auth-card :deep(.el-button--primary) { background: var(--gradient-primary); border: none; box-shadow: 0 4px 16px rgba(37,99,235,.3); }
.auth-card :deep(.el-button--primary:hover) { box-shadow: 0 8px 24px rgba(37,99,235,.45); transform: translateY(-1px); }
.auth-footer { text-align: center; margin-top: 24px; font-size: 13px; color: var(--text-secondary); }
.auth-footer a { color: var(--primary); font-weight: 600; }
</style>

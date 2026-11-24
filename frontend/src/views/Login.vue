<template>
  <div class="auth-page">
    <div class="auth-bg">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
    </div>
    <div class="auth-card fade-up">
      <h2>{{ t('auth.loginTitle') }}</h2>
      <p class="auth-sub">{{ t('auth.loginSub') }}</p>
      <div v-if="errorMsg" class="auth-error">
        <span class="error-icon">!</span>
        {{ errorMsg }}
      </div>
      <div v-if="warningMsg" class="auth-warning">
        {{ warningMsg }}
      </div>
      <form @submit.prevent="handleLogin">
        <el-input v-model="form.username" :placeholder="t('auth.username')" size="large" :prefix-icon="User" />
        <el-input v-model="form.password" :placeholder="t('auth.password')" type="password" size="large" :prefix-icon="Lock" show-password />
        <el-button type="primary" native-type="submit" :loading="loading" size="large" style="width:100%;font-weight:700;margin-top:8px">
          {{ t('auth.signIn') }}
        </el-button>
      </form>
      <p v-if="isB2B" class="auth-footer">{{ t('auth.newFactory') }} <router-link to="/register">{{ t('auth.registerHere') }}</router-link></p>
      <p class="auth-footer">{{ t('auth.newBuyer') }} <router-link to="/register/buyer">{{ t('auth.registerBuyerHere') }}</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuth } from '../store/auth'
import { useSiteMode } from '../composables/useSiteMode'
import { ElMessage } from 'element-plus'
import api from '../api'

const { t } = useI18n()
const router = useRouter()
const { login } = useAuth()
const { isB2B, loadSiteMode } = useSiteMode()
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const errorMsg = ref('')
const warningMsg = ref('')

onMounted(() => {
  loadSiteMode()
})

async function handleLogin() {
  errorMsg.value = ''
  warningMsg.value = ''
  loading.value = true
  try {
    const { data } = await api.post('/auth/login', form)
    login(data.token, data.user)
    ElMessage.success(t('auth.welcomeBack', { name: data.user.username }))

    // 根据角色跳转
    if (data.user.role === 'dev') {
      router.push('/dev')
    } else if (data.user.role === 'admin') {
      router.push('/admin')
    } else if (data.user.role === 'buyer') {
      router.push('/buyer')
    } else {
      router.push('/factory')
    }
  } catch (e) {
    const resp = e.response?.data
    if (resp?.error_type === 'user_not_found') {
      errorMsg.value = t('auth.userNotFound')
    } else if (resp?.error_type === 'wrong_password') {
      errorMsg.value = t('auth.wrongPassword')
    } else if (resp?.factory_status === 'pending') {
      warningMsg.value = t('auth.factoryPending')
    } else if (resp?.factory_status === 'rejected' && resp?.reason) {
      errorMsg.value = t('auth.factoryRejected') + resp.reason
    } else if (resp?.factory_status === 'disabled' && resp?.reason) {
      errorMsg.value = t('auth.accountDisabled') + resp.reason
    } else {
      errorMsg.value = t('auth.loginFailed')
    }
  } finally { loading.value = false }
}
</script>

<style scoped>
.auth-page {
  display: flex; align-items: center; justify-content: center; min-height: 100vh;
  position: relative; overflow: hidden;
  background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 35%, #3b82f6 65%, #60a5fa 100%);
  background-size: 300% 300%;
  animation: gradientShift 8s ease infinite;
  margin-top: -96px; padding-top: 96px;
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
.auth-warning {
  background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px;
  padding: 12px 16px; margin-bottom: 20px;
  color: #b45309; font-size: 13px; font-weight: 500; line-height: 1.5;
}
.auth-card form { display: flex; flex-direction: column; gap: 16px; }
.auth-card :deep(.el-button--primary) {
  background: var(--gradient-primary); border: none;
  box-shadow: 0 4px 16px rgba(37,99,235,.3);
  transition: all var(--transition-base);
}
.auth-card :deep(.el-button--primary:hover) { box-shadow: 0 8px 24px rgba(37,99,235,.45); transform: translateY(-1px); }
.auth-footer { text-align: center; margin-top: 24px; font-size: 13px; color: var(--text-secondary); }
.auth-footer a { color: var(--primary); font-weight: 600; }
</style>

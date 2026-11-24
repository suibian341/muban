<template>
  <div class="dev-dashboard">
    <div class="container">
      <div class="dash-header fade-up">
        <h1>🛠️ 开发者控制台</h1>
        <p>统一管理平台所有功能和配置</p>
      </div>

      <!-- 模式切换 -->
      <el-card class="mode-card fade-up fade-up-d1">
        <template #header>
          <div class="card-header">
            <span>🔄 站点模式切换</span>
          </div>
        </template>
        <div class="mode-switch">
          <el-radio-group v-model="currentMode" size="large" @change="handleModeChange">
            <el-radio-button label="b2b">
              <div class="mode-option">
                <div class="mode-label">🏭 B2B模式</div>
                <div class="mode-desc">工厂入驻 + 商品审核 + 询盘报价</div>
              </div>
            </el-radio-button>
            <el-radio-button label="b2c">
              <div class="mode-option">
                <div class="mode-label">🛒 B2C模式</div>
                <div class="mode-desc">独立站 + 直接上架 + 显示价格</div>
              </div>
            </el-radio-button>
          </el-radio-group>
        </div>
      </el-card>

      <!-- 快捷入口 -->
      <el-card class="actions-card fade-up fade-up-d2">
        <template #header>
          <div class="card-header">
            <span>⚡ 快捷入口</span>
          </div>
        </template>
        <div class="actions-grid">
          <router-link to="/dev/branding" class="action-item">
            <div class="action-icon" style="background: #ede9fe;">🎨</div>
            <div class="action-text">
              <div class="action-title">品牌设置</div>
              <div class="action-desc">Logo、品牌名称、描述</div>
            </div>
          </router-link>
          <router-link to="/dev/footer" class="action-item">
            <div class="action-icon" style="background: #e0f2fe;">📝</div>
            <div class="action-text">
              <div class="action-title">页脚编辑</div>
              <div class="action-desc">FAQ、物流、条款、关于</div>
            </div>
          </router-link>
        </div>
      </el-card>
    </div>

    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { useSiteMode } from '@/composables/useSiteMode'

const { siteMode, loadSiteMode, updateSiteMode } = useSiteMode()

// 模式切换
const currentMode = ref('b2b')

onMounted(async () => {
  await loadSiteMode()
  currentMode.value = siteMode.value
})

async function handleModeChange(newMode) {
  try {
    const success = await updateSiteMode(newMode)
    if (success) {
      ElMessage.success(`已切换到 ${newMode === 'b2b' ? 'B2B' : 'B2C'} 模式`)
      window.location.reload()
    } else {
      ElMessage.error('模式切换失败')
      currentMode.value = siteMode.value
    }
  } catch (error) {
    ElMessage.error('模式切换失败')
    currentMode.value = siteMode.value
  }
}
</script>

<style scoped>
.dev-dashboard {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px 0;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.dash-header {
  margin-bottom: 32px;
}

.dash-header h1 {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: #1f2937;
}

.dash-header p {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

.mode-card {
  margin-bottom: 24px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
}

.mode-switch {
  padding: 16px 0;
}

.mode-switch .el-radio-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  width: 100%;
}

.mode-switch .el-radio-button {
  flex: 1;
}

.mode-switch :deep(.el-radio-button__inner) {
  width: 100%;
  height: auto;
  padding: 20px;
  border-radius: 12px;
}

.mode-option {
  text-align: center;
}

.mode-label {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.mode-desc {
  font-size: 13px;
  color: #6b7280;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.stat-details {
  font-size: 12px;
  color: #9ca3af;
}

.actions-card {
  margin-bottom: 24px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  padding: 16px 0;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;
  cursor: pointer;
}

.action-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.action-text {
  flex: 1;
}

.action-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.action-desc {
  font-size: 12px;
  color: #9ca3af;
}

.dev-tabs {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-bar {
  margin-bottom: 16px;
}

.fade-up {
  animation: fadeUp 0.6s ease;
}

.fade-up-d1 {
  animation-delay: 0.1s;
  opacity: 0;
  animation-fill-mode: forwards;
}

.fade-up-d2 {
  animation-delay: 0.2s;
  opacity: 0;
  animation-fill-mode: forwards;
}

.fade-up-d3 {
  animation-delay: 0.3s;
  opacity: 0;
  animation-fill-mode: forwards;
}

.fade-up-d4 {
  animation-delay: 0.4s;
  opacity: 0;
  animation-fill-mode: forwards;
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

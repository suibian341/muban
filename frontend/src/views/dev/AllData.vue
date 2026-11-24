<template>
  <div class="all-data">
    <div class="page-header">
      <el-button @click="$router.back()" icon="el-icon-arrow-left">返回</el-button>
      <h1>📊 数据查看</h1>
    </div>

    <el-tabs v-model="activeTab">
      <!-- 用户数据 -->
      <el-tab-pane label="用户" name="users">
        <div class="tab-header">
          <el-select v-model="userRole" placeholder="筛选角色" clearable @change="loadUsers">
            <el-option label="全部" value="" />
            <el-option label="管理员" value="admin" />
            <el-option label="工厂" value="factory" />
            <el-option label="买家" value="buyer" />
            <el-option label="开发者" value="dev" />
          </el-select>
        </div>
        <el-table :data="users" border stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" width="150" />
          <el-table-column prop="role" label="角色" width="100">
            <template #default="{ row }">
              <el-tag :type="getRoleType(row.role)">{{ getRoleLabel(row.role) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="company_name" label="公司" />
          <el-table-column prop="country" label="国家" width="100" />
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '激活' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="注册时间" width="180" />
        </el-table>
        <el-pagination
          v-model:current-page="userPage"
          :page-size="20"
          :total="userTotal"
          layout="total, prev, pager, next"
          @current-change="loadUsers"
        />
      </el-tab-pane>

      <!-- 工厂数据 -->
      <el-tab-pane label="工厂" name="factories">
        <el-table :data="factories" border stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="company_name" label="公司名称" />
          <el-table-column prop="contact_person" label="联系人" width="120" />
          <el-table-column prop="phone" label="电话" width="150" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getFactoryStatusType(row.status)">
                {{ getFactoryStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="申请时间" width="180" />
        </el-table>
        <el-pagination
          v-model:current-page="factoryPage"
          :page-size="20"
          :total="factoryTotal"
          layout="total, prev, pager, next"
          @current-change="loadFactories"
        />
      </el-tab-pane>

      <!-- 商品数据 -->
      <el-tab-pane label="商品" name="products">
        <el-table :data="products" border stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="title" label="标题" min-width="200" />
          <el-table-column prop="factory_name" label="工厂" width="150" />
          <el-table-column prop="base_price" label="价格" width="100" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getProductStatusType(row.status)">
                {{ getProductStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="标记" width="150">
            <template #default="{ row }">
              <el-tag v-if="row.is_featured" size="small" type="warning">爆款</el-tag>
              <el-tag v-if="row.is_new" size="small" type="success">新品</el-tag>
              <el-tag v-if="row.is_clearance" size="small" type="danger">清仓</el-tag>
              <el-tag v-if="row.is_banner" size="small" type="primary">轮播</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="view_count" label="浏览" width="80" />
          <el-table-column prop="created_at" label="创建时间" width="180" />
        </el-table>
        <el-pagination
          v-model:current-page="productPage"
          :page-size="20"
          :total="productTotal"
          layout="total, prev, pager, next"
          @current-change="loadProducts"
        />
      </el-tab-pane>

      <!-- 询盘数据 -->
      <el-tab-pane label="询盘" name="inquiries">
        <el-table :data="inquiries" border stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="product_title" label="商品" min-width="200" />
          <el-table-column prop="contact_name" label="联系人" width="120" />
          <el-table-column prop="email" label="邮箱" width="200" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getInquiryStatusType(row.status)">
                {{ getInquiryStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="source" label="来源" width="100" />
          <el-table-column prop="created_at" label="提交时间" width="180" />
        </el-table>
        <el-pagination
          v-model:current-page="inquiryPage"
          :page-size="20"
          :total="inquiryTotal"
          layout="total, prev, pager, next"
          @current-change="loadInquiries"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const activeTab = ref('users')

// 用户
const users = ref([])
const userPage = ref(1)
const userTotal = ref(0)
const userRole = ref('')

// 工厂
const factories = ref([])
const factoryPage = ref(1)
const factoryTotal = ref(0)

// 商品
const products = ref([])
const productPage = ref(1)
const productTotal = ref(0)

// 询盘
const inquiries = ref([])
const inquiryPage = ref(1)
const inquiryTotal = ref(0)

onMounted(() => {
  loadUsers()
})

async function loadUsers() {
  try {
    const params = { page: userPage.value, per_page: 20 }
    if (userRole.value) params.role = userRole.value
    const { data } = await api.get('/dev/all-users', { params })
    users.value = data.items
    userTotal.value = data.total
  } catch (error) {
    ElMessage.error('加载用户数据失败')
  }
}

async function loadFactories() {
  try {
    const { data } = await api.get('/dev/all-factories', {
      params: { page: factoryPage.value, per_page: 20 }
    })
    factories.value = data.items
    factoryTotal.value = data.total
  } catch (error) {
    ElMessage.error('加载工厂数据失败')
  }
}

async function loadProducts() {
  try {
    const { data } = await api.get('/dev/all-products', {
      params: { page: productPage.value, per_page: 20 }
    })
    products.value = data.items
    productTotal.value = data.total
  } catch (error) {
    ElMessage.error('加载商品数据失败')
  }
}

async function loadInquiries() {
  try {
    const { data } = await api.get('/dev/all-inquiries', {
      params: { page: inquiryPage.value, per_page: 20 }
    })
    inquiries.value = data.items
    inquiryTotal.value = data.total
  } catch (error) {
    ElMessage.error('加载询盘数据失败')
  }
}

function getRoleType(role) {
  const types = { admin: 'danger', factory: 'warning', buyer: 'success', dev: 'primary' }
  return types[role] || 'info'
}

function getRoleLabel(role) {
  const labels = { admin: '管理员', factory: '工厂', buyer: '买家', dev: '开发者' }
  return labels[role] || role
}

function getFactoryStatusType(status) {
  const types = { pending: 'warning', approved: 'success', rejected: 'danger', disabled: 'info' }
  return types[status] || 'info'
}

function getFactoryStatusLabel(status) {
  const labels = { pending: '待审核', approved: '已通过', rejected: '已拒绝', disabled: '已禁用' }
  return labels[status] || status
}

function getProductStatusType(status) {
  const types = { draft: 'info', pending: 'warning', active: 'success', rejected: 'danger' }
  return types[status] || 'info'
}

function getProductStatusLabel(status) {
  const labels = { draft: '草稿', pending: '待审核', active: '已上架', rejected: '已拒绝' }
  return labels[status] || status
}

function getInquiryStatusType(status) {
  const types = { new: 'warning', replied: 'primary', closed: 'info' }
  return types[status] || 'info'
}

function getInquiryStatusLabel(status) {
  const labels = { new: '新询盘', replied: '已回复', closed: '已关闭' }
  return labels[status] || status
}
</script>

<style scoped>
.all-data {
  padding: 24px;
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
}

.tab-header {
  margin-bottom: 16px;
}

.el-pagination {
  margin-top: 16px;
  justify-content: center;
}
</style>

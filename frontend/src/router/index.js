import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('../views/HomePage.vue') },
  { path: '/products', component: () => import('../views/ProductList.vue') },
  { path: '/products/:id', component: () => import('../views/ProductDetail.vue') },
  { path: '/clearance', component: () => import('../views/ClearanceProducts.vue') },
  { path: '/about', component: () => import('../views/AboutUs.vue') },
  { path: '/faq', component: () => import('../views/FAQ.vue') },
  { path: '/shipping', component: () => import('../views/Shipping.vue') },
  { path: '/terms', component: () => import('../views/Terms.vue') },
  { path: '/login', component: () => import('../views/Login.vue') },
  { path: '/register', component: () => import('../views/Register.vue') },
  { path: '/register/buyer', component: () => import('../views/BuyerRegister.vue') },
  {
    path: '/buyer',
    component: () => import('../views/buyer/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'buyer' }
  },
  {
    path: '/factory',
    component: () => import('../views/factory/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'factory' }
  },
  {
    path: '/factory/products/new',
    component: () => import('../views/factory/ProductForm.vue'),
    meta: { requiresAuth: true, role: 'factory' }
  },
  {
    path: '/factory/products/:id/edit',
    component: () => import('../views/factory/ProductForm.vue'),
    meta: { requiresAuth: true, role: 'factory' }
  },
  {
    path: '/admin/products/new',
    component: () => import('../views/factory/ProductForm.vue'),
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin',
    component: () => import('../views/admin/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/inquiries',
    component: () => import('../views/admin/Inquiries.vue'),
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/products/:id/edit',
    component: () => import('../views/factory/ProductForm.vue'),
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/dev',
    component: () => import('../views/dev/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'dev' }
  },
  {
    path: '/dev/branding',
    component: () => import('../views/dev/BrandSettings.vue'),
    meta: { requiresAuth: true, role: 'dev' }
  },
  {
    path: '/dev/footer',
    component: () => import('../views/dev/FooterEditor.vue'),
    meta: { requiresAuth: true, role: 'dev' }
  },
  {
    path: '/dev/data',
    component: () => import('../views/dev/AllData.vue'),
    meta: { requiresAuth: true, role: 'dev' }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() { return { top: 0 } }
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user) return next('/login')
    // dev 角色可以访问所有后台
    if (user.role === 'dev') return next()
    // 其他角色需要匹配
    if (to.meta.role && user.role !== to.meta.role) return next('/')
  }
  next()
})

export default router

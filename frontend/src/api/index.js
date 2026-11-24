import axios from 'axios'
import { useAuth } from '../store/auth'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  config.headers['X-Lang'] = localStorage.getItem('lang') || 'zh'
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      // Don't redirect on login failures
      const url = err.config?.url || ''
      if (!url.includes('/auth/login')) {
        const { logout } = useAuth()
        logout()
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export default api

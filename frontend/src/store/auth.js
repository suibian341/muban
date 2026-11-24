import { reactive } from 'vue'

// 轻量全局状态，替代各组件独立读 localStorage
const stored = localStorage.getItem('user')
const state = reactive({
  user: stored ? JSON.parse(stored) : null,
})

export function useAuth() {
  function login(token, user) {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    state.user = user
  }

  function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    state.user = null
  }

  return { state, login, logout }
}

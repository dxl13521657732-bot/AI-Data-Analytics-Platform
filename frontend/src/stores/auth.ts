import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/api/auth'
import { apiLogin, apiRegister, apiGetMe } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<UserInfo | null>(null)

  const isAdmin = computed(() => user.value?.role === 'admin')
  const isEditor = computed(() => ['admin', 'editor'].includes(user.value?.role ?? ''))

  async function login(username: string, password: string) {
    const res = await apiLogin(username, password)
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('token', res.access_token)
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      user.value = await apiGetMe()
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  return { token, user, isAdmin, isEditor, login, fetchMe, logout }
})

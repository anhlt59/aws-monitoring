import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/core/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  const login = async (credentials: { email: string; password: string }) => {
    // TODO: Implement actual login logic
    console.log('Login:', credentials)
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout
  }
})

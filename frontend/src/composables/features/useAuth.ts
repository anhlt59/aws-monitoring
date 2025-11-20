import { ref, computed } from 'vue'
import { authApi } from '@/api'
import { STORAGE_KEYS } from '@/core/constants'
import type { LoginRequest, User, ApiError } from '@/core/types'

const user = ref<User | null>(null)
const accessToken = ref<string | null>(null)
const isLoading = ref(false)
const error = ref<ApiError | null>(null)

/**
 * Authentication composable
 */
export function useAuth() {
  const isAuthenticated = computed(() => !!user.value && !!accessToken.value)

  /**
   * Initialize auth state from localStorage
   */
  const initializeAuth = () => {
    const storedUser = localStorage.getItem(STORAGE_KEYS.USER)
    const storedToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)

    if (storedUser && storedToken) {
      try {
        user.value = JSON.parse(storedUser)
        accessToken.value = storedToken
      } catch (err) {
        clearAuth()
      }
    }
  }

  /**
   * Login with credentials
   */
  const login = async (credentials: LoginRequest): Promise<boolean> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await authApi.login(credentials)

      user.value = response.user
      accessToken.value = response.access_token

      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(response.user))
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.access_token)
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, response.refresh_token)

      return true
    } catch (err) {
      error.value = err as ApiError
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Logout current user
   */
  const logout = async () => {
    try {
      await authApi.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      clearAuth()
    }
  }

  /**
   * Clear auth state
   */
  const clearAuth = () => {
    user.value = null
    accessToken.value = null
    localStorage.removeItem(STORAGE_KEYS.USER)
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
  }

  /**
   * Get current user profile
   */
  const fetchProfile = async () => {
    isLoading.value = true
    error.value = null

    try {
      const profile = await authApi.getProfile()
      user.value = profile
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(profile))
    } catch (err) {
      error.value = err as ApiError
      clearAuth()
    } finally {
      isLoading.value = false
    }
  }

  // Initialize on first use
  if (!user.value && !accessToken.value) {
    initializeAuth()
  }

  return {
    user,
    accessToken,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    fetchProfile,
    clearAuth
  }
}

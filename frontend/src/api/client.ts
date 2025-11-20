import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { API_CONFIG, STORAGE_KEYS } from '@/core/constants'
import type { ApiError } from '@/core/types'

/**
 * Create axios instance with default configuration
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Request interceptor - Add auth token to requests
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Response interceptor - Handle errors globally
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const apiError: ApiError = {
      message: 'An unexpected error occurred',
      status: error.response?.status
    }

    if (error.response) {
      // Server responded with error status
      const data = error.response.data as any
      apiError.message = data?.message || data?.error || error.message
      apiError.code = data?.code
      apiError.details = data?.details

      // Handle 401 Unauthorized - redirect to login
      if (error.response.status === 401) {
        localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
        localStorage.removeItem(STORAGE_KEYS.USER)

        // Only redirect if not already on login page
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
    } else if (error.request) {
      // Request made but no response received
      apiError.message = 'No response from server. Please check your connection.'
    } else {
      // Error in request setup
      apiError.message = error.message
    }

    return Promise.reject(apiError)
  }
)

/**
 * Helper function to handle API errors
 */
export function handleApiError(error: unknown): ApiError {
  if (typeof error === 'object' && error !== null && 'message' in error) {
    return error as ApiError
  }
  return {
    message: 'An unexpected error occurred'
  }
}

import { apiClient } from '../client'
import type { LoginRequest, LoginResponse, UserProfile } from '@/core/types'

/**
 * Authentication API service
 */
export const authApi = {
  /**
   * Login with email and password
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/api/auth/login', credentials)
    return response.data
  },

  /**
   * Logout current user
   */
  async logout(): Promise<void> {
    await apiClient.post('/api/auth/logout')
  },

  /**
   * Get current user profile
   */
  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>('/api/auth/me')
    return response.data
  },

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<{ access_token: string }> {
    const response = await apiClient.post<{ access_token: string }>('/api/auth/refresh', {
      refresh_token: refreshToken
    })
    return response.data
  }
}

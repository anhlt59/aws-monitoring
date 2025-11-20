import type { User } from './user'

/**
 * Login request
 */
export interface LoginRequest {
  email: string
  password: string
}

/**
 * Login response
 */
export interface LoginResponse {
  access_token: string
  refresh_token: string
  user: User
}

/**
 * Auth state
 */
export interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
}

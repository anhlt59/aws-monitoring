import type { UserRole } from '../enums'

/**
 * User entity
 */
export interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  created_at: number
  last_login?: number
}

/**
 * User filters for querying
 */
export interface UserFilters {
  search?: string
  role?: UserRole
  is_active?: boolean
  page?: number
  page_size?: number
}

/**
 * Create user request
 */
export interface CreateUserRequest {
  email: string
  full_name: string
  role: UserRole
  password?: string
}

/**
 * Update user request
 */
export interface UpdateUserRequest {
  email?: string
  full_name?: string
  role?: UserRole
  is_active?: boolean
  password?: string
}

/**
 * User profile (current user)
 */
export interface UserProfile extends User {
  permissions: string[]
}

/**
 * User statistics
 */
export interface UserStats {
  total: number
  active: number
  by_role: Record<UserRole, number>
}

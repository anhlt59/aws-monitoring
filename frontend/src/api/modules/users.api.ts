import { apiClient } from '../client'
import type {
  User,
  UserFilters,
  CreateUserRequest,
  UpdateUserRequest,
  PaginatedResponse
} from '@/core/types'

/**
 * Users API service
 */
export const usersApi = {
  /**
   * Fetch paginated users with filters
   */
  async getUsers(filters: UserFilters = {}): Promise<PaginatedResponse<User>> {
    const response = await apiClient.get<PaginatedResponse<User>>('/api/users', {
      params: filters
    })
    return response.data
  },

  /**
   * Fetch single user by ID
   */
  async getUserById(id: string): Promise<User> {
    const response = await apiClient.get<User>(`/api/users/${id}`)
    return response.data
  },

  /**
   * Create new user
   */
  async createUser(data: CreateUserRequest): Promise<User> {
    const response = await apiClient.post<User>('/api/users', data)
    return response.data
  },

  /**
   * Update existing user
   */
  async updateUser(id: string, data: UpdateUserRequest): Promise<User> {
    const response = await apiClient.put<User>(`/api/users/${id}`, data)
    return response.data
  },

  /**
   * Delete user
   */
  async deleteUser(id: string): Promise<void> {
    await apiClient.delete(`/api/users/${id}`)
  }
}

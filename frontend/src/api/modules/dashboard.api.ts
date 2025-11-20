import { apiClient } from '../client'
import type { DashboardOverview, EventStats, TaskStats, UserStats } from '@/core/types'

/**
 * Dashboard API service
 */
export const dashboardApi = {
  /**
   * Get dashboard overview data
   */
  async getOverview(): Promise<DashboardOverview> {
    const response = await apiClient.get<DashboardOverview>('/api/dashboard/overview')
    return response.data
  },

  /**
   * Get event statistics
   */
  async getEventStats(): Promise<EventStats> {
    const response = await apiClient.get<EventStats>('/api/dashboard/events-stats')
    return response.data
  },

  /**
   * Get task statistics
   */
  async getTaskStats(): Promise<TaskStats> {
    const response = await apiClient.get<TaskStats>('/api/dashboard/tasks-stats')
    return response.data
  },

  /**
   * Get user statistics
   */
  async getUserStats(): Promise<UserStats> {
    const response = await apiClient.get<UserStats>('/api/dashboard/users-stats')
    return response.data
  }
}

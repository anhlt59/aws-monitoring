import { apiClient } from '../client'
import type {
  Task,
  TaskFilters,
  CreateTaskRequest,
  UpdateTaskRequest,
  AddCommentRequest,
  PaginatedResponse
} from '@/core/types'

/**
 * Tasks API service
 */
export const tasksApi = {
  /**
   * Fetch paginated tasks with filters
   */
  async getTasks(filters: TaskFilters = {}): Promise<PaginatedResponse<Task>> {
    const response = await apiClient.get<PaginatedResponse<Task>>('/api/tasks', {
      params: filters
    })
    return response.data
  },

  /**
   * Fetch single task by ID
   */
  async getTaskById(id: string): Promise<Task> {
    const response = await apiClient.get<Task>(`/api/tasks/${id}`)
    return response.data
  },

  /**
   * Create new task
   */
  async createTask(data: CreateTaskRequest): Promise<Task> {
    const response = await apiClient.post<Task>('/api/tasks', data)
    return response.data
  },

  /**
   * Update existing task
   */
  async updateTask(id: string, data: UpdateTaskRequest): Promise<Task> {
    const response = await apiClient.put<Task>(`/api/tasks/${id}`, data)
    return response.data
  },

  /**
   * Delete task
   */
  async deleteTask(id: string): Promise<void> {
    await apiClient.delete(`/api/tasks/${id}`)
  },

  /**
   * Add comment to task
   */
  async addComment(taskId: string, data: AddCommentRequest): Promise<void> {
    await apiClient.post(`/api/tasks/${taskId}/comments`, data)
  },

  /**
   * Update task status
   */
  async updateTaskStatus(taskId: string, status: string): Promise<Task> {
    const response = await apiClient.put<Task>(`/api/tasks/${taskId}/status`, { status })
    return response.data
  },

  /**
   * Create task from event
   */
  async createTaskFromEvent(eventId: string, data: CreateTaskRequest): Promise<Task> {
    const response = await apiClient.post<Task>(`/api/events/${eventId}/create-task`, data)
    return response.data
  }
}

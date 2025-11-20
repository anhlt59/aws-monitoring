import type { TaskStatus, TaskPriority } from '../enums'

/**
 * Task entity
 */
export interface Task {
  id: string
  title: string
  description: string
  status: TaskStatus
  priority: TaskPriority
  assigned_user_id: string
  assigned_user_name?: string
  event_id?: string
  event_details?: {
    account: string
    region: string
    source: string
    severity: string
  }
  due_date?: number
  created_at: number
  updated_at: number
  created_by: string
  comments?: TaskComment[]
}

/**
 * Task comment
 */
export interface TaskComment {
  id: string
  task_id: string
  user_id: string
  user_name: string
  comment: string
  created_at: number
}

/**
 * Task filters for querying
 */
export interface TaskFilters {
  status?: TaskStatus[]
  priority?: TaskPriority[]
  assigned_user_id?: string
  event_id?: string
  start_date?: number
  end_date?: number
  page?: number
  page_size?: number
}

/**
 * Create task request
 */
export interface CreateTaskRequest {
  title: string
  description: string
  priority: TaskPriority
  assigned_user_id: string
  event_id?: string
  due_date?: number
}

/**
 * Update task request
 */
export interface UpdateTaskRequest {
  title?: string
  description?: string
  status?: TaskStatus
  priority?: TaskPriority
  assigned_user_id?: string
  due_date?: number
}

/**
 * Add comment request
 */
export interface AddCommentRequest {
  comment: string
}

/**
 * Task statistics for dashboard
 */
export interface TaskStats {
  total: number
  by_status: Record<TaskStatus, number>
  by_priority: Record<TaskPriority, number>
  my_tasks: number
}

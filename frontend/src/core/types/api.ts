/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

/**
 * API error
 */
export interface ApiError {
  message: string
  code?: string
  details?: Record<string, any>
  status?: number
}

/**
 * Validation error
 */
export interface ValidationError {
  field: string
  message: string
}

/**
 * API response wrapper
 */
export interface ApiResponse<T> {
  data: T
  message?: string
}

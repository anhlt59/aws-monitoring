/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
  timestamp?: number;
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

/**
 * API error response
 */
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp?: number;
}

/**
 * Common error codes
 */
export enum ErrorCode {
  // Client errors (4xx)
  BadRequest = 'BAD_REQUEST',
  Unauthorized = 'UNAUTHORIZED',
  Forbidden = 'FORBIDDEN',
  NotFound = 'NOT_FOUND',
  ValidationError = 'VALIDATION_ERROR',

  // Server errors (5xx)
  InternalServerError = 'INTERNAL_SERVER_ERROR',
  ServiceUnavailable = 'SERVICE_UNAVAILABLE',
  GatewayTimeout = 'GATEWAY_TIMEOUT',

  // Business errors
  DuplicateEntry = 'DUPLICATE_ENTRY',
  ResourceConflict = 'RESOURCE_CONFLICT',
  OperationFailed = 'OPERATION_FAILED'
}

/**
 * HTTP request configuration
 */
export interface RequestConfig {
  headers?: Record<string, string>;
  params?: Record<string, string | number | boolean>;
  timeout?: number;
  retry?: boolean;
}

/**
 * Cursor-based pagination parameters
 */
export interface CursorPaginationParams {
  cursor?: string;
  limit?: number;
}

/**
 * Cursor-based paginated response
 */
export interface CursorPaginatedResponse<T> {
  items: T[];
  next_cursor?: string;
  has_more: boolean;
}

/**
 * Sort order
 */
export enum SortOrder {
  Ascending = 'asc',
  Descending = 'desc'
}

/**
 * Generic sort parameters
 */
export interface SortParams {
  field: string;
  order: SortOrder;
}

/**
 * Loading state for async operations
 */
export interface AsyncState<T> {
  data: T | null;
  isLoading: boolean;
  error: ApiError | null;
}

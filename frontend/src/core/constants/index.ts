export * from './routes'

/**
 * API configuration
 */
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:4566',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3
} as const

/**
 * Pagination defaults
 */
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100]
} as const

/**
 * Date format
 */
export const DATE_FORMAT = {
  FULL: 'PPpp',
  DATE_ONLY: 'PP',
  TIME_ONLY: 'p',
  SHORT: 'MM/dd/yyyy'
} as const

/**
 * Storage keys
 */
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user'
} as const

/**
 * Auto-refresh interval (milliseconds)
 */
export const AUTO_REFRESH_INTERVAL = 30000 // 30 seconds

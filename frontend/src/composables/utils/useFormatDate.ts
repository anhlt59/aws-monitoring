import { format, formatDistanceToNow } from 'date-fns'

/**
 * Date formatting utilities
 */
export function useFormatDate() {
  /**
   * Format Unix timestamp to readable date string
   */
  const formatDate = (timestamp: number, formatStr = 'PPpp'): string => {
    return format(new Date(timestamp * 1000), formatStr)
  }

  /**
   * Format Unix timestamp to relative time (e.g., "2 hours ago")
   */
  const formatRelativeTime = (timestamp: number): string => {
    return formatDistanceToNow(new Date(timestamp * 1000), { addSuffix: true })
  }

  /**
   * Format Unix timestamp to date only
   */
  const formatDateOnly = (timestamp: number): string => {
    return format(new Date(timestamp * 1000), 'PP')
  }

  /**
   * Format Unix timestamp to time only
   */
  const formatTimeOnly = (timestamp: number): string => {
    return format(new Date(timestamp * 1000), 'p')
  }

  return {
    formatDate,
    formatRelativeTime,
    formatDateOnly,
    formatTimeOnly
  }
}

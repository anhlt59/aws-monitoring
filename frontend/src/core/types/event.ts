import type { Severity } from '../enums'

/**
 * Event entity
 */
export interface Event {
  id: string
  account: string
  region: string
  source: string
  severity: Severity
  detail_type: string
  detail: Record<string, any>
  published_at: number
  created_at: number
  updated_at: number
}

/**
 * Event filters for querying
 */
export interface EventFilters {
  account?: string
  region?: string
  source?: string
  severity?: Severity[]
  detail_type?: string
  start_date?: number
  end_date?: number
  page?: number
  page_size?: number
}

/**
 * Event statistics for dashboard
 */
export interface EventStats {
  total: number
  by_severity: Record<Severity, number>
  by_source: Record<string, number>
  recent_events: Event[]
}

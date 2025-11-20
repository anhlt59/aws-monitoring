import type { EventStats } from './event'
import type { TaskStats } from './task'
import type { UserStats } from './user'

/**
 * Dashboard overview data
 */
export interface DashboardOverview {
  events: EventStats
  tasks: TaskStats
  users: UserStats
}

/**
 * Time series data point
 */
export interface TimeSeriesData {
  timestamp: number
  value: number
  label?: string
}

/**
 * Chart data
 */
export interface ChartData {
  labels: string[]
  datasets: Array<{
    label: string
    data: number[]
    backgroundColor?: string | string[]
    borderColor?: string | string[]
  }>
}

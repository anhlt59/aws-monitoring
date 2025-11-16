// Core domain types
export interface User {
  id: string
  email: string
  name: string
}

export interface AuthToken {
  token: string
  expiresAt: number
}

export interface Event {
  id: string
  account: string
  region: string
  source: string
  detail: Record<string, any>
  detail_type: string
  severity: number
  resources: string[]
  published_at: number
  updated_at: number
}

export interface Agent {
  account: string
  region: string
  status: string
  deployed_at: number
  created_at: number
}

export interface PaginationParams {
  page?: number
  limit?: number
  cursor?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  cursor?: string
  has_more: boolean
}

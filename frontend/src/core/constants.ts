export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001/api',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3
} as const;

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100
} as const;

export const POLLING = {
  EVENTS_REFRESH_INTERVAL: Number(import.meta.env.VITE_POLLING_INTERVAL) || 30000,
  AGENTS_REFRESH_INTERVAL: 60000
} as const;

export const APP = {
  TITLE: import.meta.env.VITE_APP_TITLE || 'AWS Monitoring',
  DEBUG: import.meta.env.VITE_ENABLE_DEBUG === 'true'
} as const;

export const ROUTES = {
  LOGIN: '/login',
  DASHBOARD: '/',
  EVENTS: '/events',
  EVENT_DETAIL: '/events/:id',
  AGENTS: '/agents',
  AGENT_DETAIL: '/agents/:account',
  REPORTS: '/reports',
  SETTINGS: '/settings'
} as const;

/**
 * Route names
 */
export const ROUTE_NAMES = {
  LOGIN: 'Login',
  DASHBOARD: 'Dashboard',
  EVENTS: 'Events',
  EVENT_DETAIL: 'EventDetail',
  TASKS: 'Tasks',
  TASK_DETAIL: 'TaskDetail',
  TASK_CREATE: 'TaskCreate',
  USERS: 'Users',
  USER_DETAIL: 'UserDetail',
  USER_CREATE: 'UserCreate',
  CONFIG: 'Configuration',
  PROFILE: 'Profile'
} as const

/**
 * Route paths
 */
export const ROUTE_PATHS = {
  LOGIN: '/login',
  DASHBOARD: '/',
  EVENTS: '/events',
  EVENT_DETAIL: '/events/:id',
  TASKS: '/tasks',
  TASK_DETAIL: '/tasks/:id',
  TASK_CREATE: '/tasks/new',
  USERS: '/users',
  USER_DETAIL: '/users/:id',
  USER_CREATE: '/users/new',
  CONFIG: '/configuration',
  PROFILE: '/profile'
} as const

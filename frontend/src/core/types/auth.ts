/**
 * User entity
 */
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  permissions: Permission[];
  created_at: number;
  last_login?: number;
}

/**
 * User roles
 */
export enum UserRole {
  Admin = 'admin',
  Operator = 'operator',
  Viewer = 'viewer'
}

/**
 * Permissions
 */
export enum Permission {
  ViewEvents = 'view:events',
  ManageEvents = 'manage:events',
  ViewAgents = 'view:agents',
  ManageAgents = 'manage:agents',
  ViewReports = 'view:reports',
  ManageReports = 'manage:reports',
  ViewSettings = 'view:settings',
  ManageSettings = 'manage:settings'
}

/**
 * Login credentials
 */
export interface LoginCredentials {
  email: string;
  password: string;
  remember_me?: boolean;
}

/**
 * Authentication token
 */
export interface AuthToken {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in: number;
}

/**
 * Authentication state
 */
export interface AuthState {
  user: User | null;
  token: AuthToken | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

/**
 * Login response
 */
export interface LoginResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in: number;
  user: User;
}

/**
 * User role enum
 */
export enum UserRole {
  Admin = 'admin',
  Manager = 'manager',
  User = 'user'
}

export const UserRoleLabels: Record<UserRole, string> = {
  [UserRole.Admin]: 'Administrator',
  [UserRole.Manager]: 'Manager',
  [UserRole.User]: 'User'
}

export const UserRoleDescriptions: Record<UserRole, string> = {
  [UserRole.Admin]: 'Full access to all features',
  [UserRole.Manager]: 'Can view all, create/edit tasks, limited user management',
  [UserRole.User]: 'Can view assigned tasks, update own tasks, view events'
}

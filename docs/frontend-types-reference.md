# Frontend Types Reference

This document provides example type definitions for the frontend application, showing how backend domain models translate to TypeScript interfaces.

## Type Definition Strategy

All types mirror the backend domain models defined in `src/domain/models/` and database schemas in `docs/db.md`.

## Core Types

### Event Types

```typescript
// core/types/event.ts

/**
 * Event severity levels
 * Maps to backend: src/domain/models/event.py
 */
export enum Severity {
  Unknown = 0,
  Low = 1,
  Medium = 2,
  High = 3,
  Critical = 4
}

/**
 * Monitoring event entity
 * Maps to backend: Event domain model
 */
export interface Event {
  id: string;
  account: string;
  region: string;
  source: string;
  detail: Record<string, unknown>;
  detail_type: string;
  severity: Severity;
  resources: string[];
  published_at: number;  // Unix timestamp
  updated_at: number;     // Unix timestamp
}

/**
 * Event filters for querying
 */
export interface EventFilters {
  account?: string;
  region?: string;
  source?: string;
  severity?: Severity | Severity[];
  detail_type?: string;
  start_date?: number;   // Unix timestamp
  end_date?: number;     // Unix timestamp
  page?: number;
  page_size?: number;
}

/**
 * Event detail types (specialized event details)
 */
export interface CloudWatchAlarmDetail {
  alarmName: string;
  configuration: {
    description?: string;
    metrics: AlarmMetric[];
  };
  previousState: AlarmState;
  state: AlarmState;
}

export interface AlarmState {
  reason: string;
  reasonData: string;
  timestamp: string;
  value: 'OK' | 'ALARM' | 'INSUFFICIENT_DATA';
}

export interface AlarmMetric {
  id: string;
  metricStat: {
    metric: {
      dimensions: Record<string, string>;
      name: string;
      namespace: string;
    };
    period: number;
    stat: string;
  };
  returnData: boolean;
}

/**
 * Lambda error event detail
 */
export interface LambdaErrorDetail {
  functionName: string;
  errorMessage: string;
  errorType: string;
  stackTrace?: string[];
  requestId: string;
}

/**
 * ECS task failure detail
 */
export interface ECSTaskFailureDetail {
  clusterArn: string;
  taskArn: string;
  taskDefinitionArn: string;
  desiredStatus: string;
  lastStatus: string;
  stoppedReason?: string;
  containers: ECSContainer[];
}

export interface ECSContainer {
  containerArn: string;
  name: string;
  exitCode?: number;
  reason?: string;
}
```

### Agent Types

```typescript
// core/types/agent.ts

/**
 * Agent deployment status
 * Maps to backend: src/domain/models/agent.py
 */
export enum AgentStatus {
  CreateComplete = 'CREATE_COMPLETE',
  CreateInProgress = 'CREATE_IN_PROGRESS',
  CreateFailed = 'CREATE_FAILED',
  UpdateComplete = 'UPDATE_COMPLETE',
  UpdateInProgress = 'UPDATE_IN_PROGRESS',
  UpdateFailed = 'UPDATE_FAILED',
  DeleteComplete = 'DELETE_COMPLETE',
  DeleteInProgress = 'DELETE_IN_PROGRESS',
  DeleteFailed = 'DELETE_FAILED',
  RollbackComplete = 'ROLLBACK_COMPLETE',
  RollbackInProgress = 'ROLLBACK_IN_PROGRESS'
}

/**
 * Agent entity
 */
export interface Agent {
  account: string;        // AWS Account ID
  region: string;         // AWS Region
  status: AgentStatus;
  deployed_at: number;    // Unix timestamp
  created_at: number;     // Unix timestamp
}

/**
 * Agent deployment request
 */
export interface AgentDeploymentRequest {
  account: string;
  region: string;
}

/**
 * Agent health information
 */
export interface AgentHealth {
  account: string;
  region: string;
  isHealthy: boolean;
  lastHeartbeat?: number;
  errorCount?: number;
  lastError?: string;
}

/**
 * Agent metrics
 */
export interface AgentMetrics {
  account: string;
  eventsPublished: number;
  errorsDetected: number;
  lastQueryTime?: number;
  averageQueryDuration?: number;
}
```

### Report Types

```typescript
// core/types/report.ts

/**
 * Daily report data
 */
export interface DailyReport {
  date: string;           // ISO date string (YYYY-MM-DD)
  summary: ReportSummary;
  eventsByAccount: EventsByAccount[];
  eventsBySeverity: EventsBySeverity[];
  topErrors: TopError[];
  agentHealth: AgentHealthSummary[];
}

/**
 * Report summary statistics
 */
export interface ReportSummary {
  totalEvents: number;
  criticalEvents: number;
  highEvents: number;
  mediumEvents: number;
  lowEvents: number;
  affectedAccounts: number;
  activeAgents: number;
}

/**
 * Events grouped by account
 */
export interface EventsByAccount {
  account: string;
  region: string;
  eventCount: number;
  criticalCount: number;
  highCount: number;
}

/**
 * Events grouped by severity
 */
export interface EventsBySeverity {
  severity: Severity;
  count: number;
  percentage: number;
}

/**
 * Top error types
 */
export interface TopError {
  errorType: string;
  count: number;
  affectedResources: string[];
  firstOccurrence: number;
  lastOccurrence: number;
}

/**
 * Agent health summary
 */
export interface AgentHealthSummary {
  account: string;
  region: string;
  status: AgentStatus;
  isHealthy: boolean;
  eventsPublished: number;
}

/**
 * Report filters
 */
export interface ReportFilters {
  start_date: number;     // Unix timestamp
  end_date: number;       // Unix timestamp
  accounts?: string[];
  regions?: string[];
}
```

### API Types

```typescript
// core/types/api.ts

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
  timestamp: number;
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
```

### Common Types

```typescript
// core/types/common.ts

/**
 * Generic timestamp range
 */
export interface TimeRange {
  start: number;          // Unix timestamp
  end: number;            // Unix timestamp
}

/**
 * AWS resource identifier
 */
export interface AWSResource {
  arn: string;
  type: string;
  name?: string;
  region?: string;
  account?: string;
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

/**
 * Form validation error
 */
export interface ValidationError {
  field: string;
  message: string;
}

/**
 * Generic key-value pair
 */
export interface KeyValue {
  key: string;
  value: string;
}

/**
 * Chart data point
 */
export interface ChartDataPoint {
  timestamp: number;
  value: number;
  label?: string;
}

/**
 * Time series data
 */
export interface TimeSeries {
  name: string;
  data: ChartDataPoint[];
}

/**
 * Notification types
 */
export enum NotificationType {
  Success = 'success',
  Error = 'error',
  Warning = 'warning',
  Info = 'info'
}

/**
 * Toast notification
 */
export interface ToastNotification {
  id: string;
  type: NotificationType;
  message: string;
  duration?: number;
  dismissible?: boolean;
}

/**
 * Theme mode
 */
export enum ThemeMode {
  Light = 'light',
  Dark = 'dark',
  System = 'system'
}

/**
 * User preferences
 */
export interface UserPreferences {
  theme: ThemeMode;
  locale: string;
  timezone: string;
  notifications: {
    enabled: boolean;
    sound: boolean;
  };
}
```

### Authentication Types

```typescript
// core/types/auth.ts

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
```

## Type Guards

```typescript
// core/types/guards.ts

/**
 * Type guards for runtime type checking
 */

export function isEvent(obj: unknown): obj is Event {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'account' in obj &&
    'severity' in obj
  );
}

export function isAgent(obj: unknown): obj is Agent {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'account' in obj &&
    'status' in obj
  );
}

export function isApiError(obj: unknown): obj is ApiError {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'code' in obj &&
    'message' in obj
  );
}

export function isPaginatedResponse<T>(
  obj: unknown
): obj is PaginatedResponse<T> {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'items' in obj &&
    'total' in obj &&
    'page' in obj &&
    Array.isArray((obj as PaginatedResponse<T>).items)
  );
}
```

## Type Utilities

```typescript
// core/types/utils.ts

/**
 * Make all properties optional
 */
export type PartialDeep<T> = {
  [P in keyof T]?: T[P] extends object ? PartialDeep<T[P]> : T[P];
};

/**
 * Pick specific properties and make them required
 */
export type RequireKeys<T, K extends keyof T> = T & Required<Pick<T, K>>;

/**
 * Extract keys of a specific type
 */
export type KeysOfType<T, V> = {
  [K in keyof T]: T[K] extends V ? K : never;
}[keyof T];

/**
 * Create a type from enum values
 */
export type EnumValues<T extends Record<string, string | number>> = T[keyof T];

/**
 * Nullable type
 */
export type Nullable<T> = T | null;

/**
 * Optional type
 */
export type Optional<T> = T | undefined;

/**
 * Array element type
 */
export type ArrayElement<T> = T extends (infer U)[] ? U : never;
```

## Usage Examples

### In API Service

```typescript
// api/modules/events.api.ts (structure only)
import type { Event, EventFilters, PaginatedResponse } from '@/core/types';

async function getEvents(
  filters: EventFilters
): Promise<PaginatedResponse<Event>> {
  // API call implementation
}

async function getEventById(id: string): Promise<Event> {
  // API call implementation
}
```

### In Composable

```typescript
// composables/features/useEvents.ts (structure only)
import type { Event, EventFilters, AsyncState } from '@/core/types';

function useEvents() {
  const state: AsyncState<Event[]> = {
    data: null,
    isLoading: false,
    error: null
  };

  async function fetchEvents(filters: EventFilters): Promise<void> {
    // Implementation
  }

  return { state, fetchEvents };
}
```

### In Component

```typescript
// components/modules/events/EventCard.vue (structure only)
import type { Event } from '@/core/types';

interface Props {
  event: Event;
}

const props = defineProps<Props>();
```

## Type Maintenance Guidelines

1. **Single Source of Truth**: All types defined in `core/types/`
2. **Backend Alignment**: Keep types synchronized with backend models
3. **Avoid Duplication**: Reuse and extend existing types
4. **Documentation**: Add JSDoc comments for complex types
5. **Export Strategy**: Use barrel exports in `index.ts` files
6. **Naming Convention**: Use PascalCase for types and interfaces
7. **Type vs Interface**: Use `interface` for object shapes, `type` for unions/intersections

## Type Organization

```
core/types/
├── index.ts              # Barrel export (re-exports all types)
├── event.ts              # Event-related types
├── agent.ts              # Agent-related types
├── report.ts             # Report-related types
├── api.ts                # API-related types
├── common.ts             # Shared/common types
├── auth.ts               # Authentication types
├── guards.ts             # Type guards
└── utils.ts              # Type utilities
```

Each file should export only related types and have a clear responsibility.

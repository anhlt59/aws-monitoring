# Frontend Codebase Index

**Generated**: 2025-11-17
**Project**: AWS Monitoring - Vue 3 Frontend
**Purpose**: Comprehensive index of frontend architecture, components, patterns, and dependencies

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Directory Structure](#directory-structure)
3. [Core Domain Layer](#core-domain-layer)
4. [Infrastructure Layer](#infrastructure-layer)
5. [Application Layer](#application-layer)
6. [Presentation Layer](#presentation-layer)
7. [Routing & Navigation](#routing--navigation)
8. [Build & Configuration](#build--configuration)
9. [Testing Strategy](#testing-strategy)
10. [Development Patterns](#development-patterns)
11. [Dependencies Map](#dependencies-map)
12. [Quick Reference](#quick-reference)

---

## Architecture Overview

### Layered Architecture Pattern

The frontend follows a **4-layer architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│      Presentation Layer (UI)            │  ← Pages, Components
├─────────────────────────────────────────┤
│      Application Layer (Logic)          │  ← Stores, Composables, Utils
├─────────────────────────────────────────┤
│      Infrastructure Layer (I/O)         │  ← API Client, Services
├─────────────────────────────────────────┤
│      Core Domain Layer (Models)         │  ← Types, Enums, Constants
└─────────────────────────────────────────┘
```

**Dependency Flow**: Presentation → Application → Infrastructure → Core
**Rule**: Upper layers depend on lower layers, never reversed

### Tech Stack Summary

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| Framework | Vue 3 | 3.5.24 | UI framework with Composition API |
| Language | TypeScript | 5.9.3 | Type-safe development |
| Build Tool | Vite | 7.2.2 | Fast dev server & bundler |
| State | Pinia | 3.0.4 | Global state management |
| Routing | Vue Router | 4.6.3 | Client-side routing |
| Styling | Tailwind CSS | 3.4.1 | Utility-first CSS framework |
| HTTP | Axios | 1.13.2 | API communication |
| Testing | Vitest | 4.0.9 | Unit & component testing |
| Utils | VueUse | 14.0.0 | Composition utilities |
| Dates | date-fns | 4.1.0 | Date manipulation |

---

## Directory Structure

### Complete File Tree

```
frontend/
├── public/                    # Static assets
│   └── vite.svg              # Vite logo
├── src/                      # Source code
│   ├── core/                 # Domain layer (types, enums, constants)
│   │   ├── types/
│   │   │   └── index.ts      # TypeScript interfaces
│   │   ├── enums/
│   │   │   └── index.ts      # Enumerations
│   │   └── constants.ts      # App constants
│   ├── api/                  # Infrastructure layer
│   │   └── client.ts         # Axios HTTP client
│   ├── store/                # Application layer - state
│   │   └── modules/
│   │       └── auth.store.ts # Auth state management
│   ├── composables/          # Application layer - logic (PLANNED)
│   ├── components/           # Presentation layer (PLANNED)
│   ├── pages/                # Presentation layer - routes
│   │   ├── Dashboard.vue     # Home dashboard
│   │   ├── Events/
│   │   │   └── EventsListPage.vue
│   │   ├── Agents/
│   │   │   └── AgentsListPage.vue
│   │   └── ErrorPages/
│   │       └── NotFound.vue
│   ├── router/               # Routing configuration
│   │   ├── index.ts          # Router setup
│   │   └── routes/
│   │       ├── index.ts      # Route definitions
│   │       └── guards.ts     # Navigation guards
│   ├── styles/               # Global styles
│   │   ├── main.css          # Tailwind imports
│   │   ├── variables.css     # CSS custom properties
│   │   └── utilities.css     # Custom utilities
│   ├── App.vue               # Root component
│   └── main.ts               # App entry point
├── index.html                # HTML entry point
├── package.json              # Dependencies
├── vite.config.ts            # Vite configuration
├── vitest.config.ts          # Test configuration
├── tailwind.config.js        # Tailwind configuration
├── tsconfig.json             # TypeScript root config
├── tsconfig.app.json         # App TypeScript config
├── tsconfig.node.json        # Node TypeScript config
├── postcss.config.js         # PostCSS configuration
├── CLAUDE.md                 # Development guide
└── README.md                 # Project documentation
```

### Directory Purposes

| Path | Purpose | Current State |
|------|---------|---------------|
| `src/core/` | Domain models (types, enums, constants) | ✅ Implemented |
| `src/api/` | HTTP client and API services | 🟡 Partial (client only) |
| `src/store/modules/` | Pinia state stores | 🟡 Partial (auth only) |
| `src/composables/` | Reusable composition functions | ❌ Not created |
| `src/components/` | Reusable UI components | ❌ Not created |
| `src/pages/` | Route entry point pages | ✅ Implemented (3 pages) |
| `src/router/` | Routing configuration | ✅ Implemented |
| `src/styles/` | Global CSS and Tailwind | ✅ Implemented |

---

## Core Domain Layer

### Location: `src/core/`

**Purpose**: Define business entities, domain types, and application constants

### Type Definitions (`src/core/types/index.ts`)

#### Domain Entities

```typescript
// User entity
interface User {
  id: string
  email: string
  name: string
}

// Authentication
interface AuthToken {
  token: string
  expiresAt: number
}

// AWS Monitoring Event
interface Event {
  id: string              // Unique identifier
  account: string         // AWS account ID
  region: string          // AWS region
  source: string          // Event source (e.g., "aws.ec2")
  detail: Record<string, any>  // Event payload
  detail_type: string     // Event type
  severity: number        // Severity level (0-4)
  resources: string[]     // ARNs of affected resources
  published_at: number    // Timestamp (ms)
  updated_at: number      // Timestamp (ms)
}

// Monitoring Agent
interface Agent {
  account: string         // AWS account ID
  region: string          // AWS region
  status: string          // Deployment status
  deployed_at: number     // Timestamp (ms)
  created_at: number      // Timestamp (ms)
}
```

#### API Response Types

```typescript
// Pagination parameters
interface PaginationParams {
  page?: number
  limit?: number
  cursor?: string
}

// Paginated API response
interface PaginatedResponse<T> {
  items: T[]
  total: number
  cursor?: string
  has_more: boolean
}
```

### Enumerations (`src/core/enums/index.ts`)

```typescript
// Event severity levels
enum EventSeverity {
  UNKNOWN = 0,
  LOW = 1,
  MEDIUM = 2,
  HIGH = 3,
  CRITICAL = 4
}

// Agent deployment status
enum AgentStatus {
  CREATE_IN_PROGRESS = 'CREATE_IN_PROGRESS',
  CREATE_COMPLETE = 'CREATE_COMPLETE',
  UPDATE_IN_PROGRESS = 'UPDATE_IN_PROGRESS',
  UPDATE_COMPLETE = 'UPDATE_COMPLETE',
  DELETE_IN_PROGRESS = 'DELETE_IN_PROGRESS',
  DELETE_COMPLETE = 'DELETE_COMPLETE',
  CREATE_FAILED = 'CREATE_FAILED',
  UPDATE_FAILED = 'UPDATE_FAILED',
  DELETE_FAILED = 'DELETE_FAILED'
}
```

### Constants (`src/core/constants.ts`)

```typescript
// API configuration
API_CONFIG {
  BASE_URL: 'http://localhost:3001/api'  // Configurable via VITE_API_BASE_URL
  TIMEOUT: 30000                          // 30 seconds
  RETRY_ATTEMPTS: 3
}

// Pagination defaults
PAGINATION {
  DEFAULT_PAGE_SIZE: 20
  MAX_PAGE_SIZE: 100
}

// Polling intervals
POLLING {
  EVENTS_REFRESH_INTERVAL: 30000         // 30 seconds (configurable)
  AGENTS_REFRESH_INTERVAL: 60000         // 60 seconds
}

// Application
APP {
  TITLE: 'AWS Monitoring'                 // Configurable via VITE_APP_TITLE
  DEBUG: false                            // Configurable via VITE_ENABLE_DEBUG
}
```

---

## Infrastructure Layer

### Location: `src/api/`

**Purpose**: Handle external dependencies, HTTP communication, and data fetching

### API Client (`src/api/client.ts`)

#### Architecture

- **Pattern**: Singleton Axios instance with interceptors
- **Base URL**: Configurable via `VITE_API_BASE_URL`
- **Timeout**: 30 seconds
- **Content Type**: `application/json`

#### Features

**Request Interceptor**:
- Auth token injection (TODO - currently commented out)
- Request ID generation for tracing

**Response Interceptor**:
- Global error handling
- 401 → Redirect to login
- 403 → Log forbidden access
- 5xx → Log server errors
- Network errors → Log network issues

#### HTTP Methods

```typescript
class ApiClient {
  get<T>(url: string, config?: AxiosRequestConfig): Promise<T>
  post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  delete<T>(url: string, config?: AxiosRequestConfig): Promise<T>
}
```

#### Usage Example

```typescript
import { apiClient } from '@/api/client'

// GET request
const events = await apiClient.get<Event[]>('/events')

// POST request
const newEvent = await apiClient.post<Event>('/events', eventData)

// PUT request
const updated = await apiClient.put<Event>(`/events/${id}`, updates)

// DELETE request
await apiClient.delete(`/events/${id}`)
```

### API Services (PLANNED)

**Missing Services** (should be created):
- `src/api/events.ts` - Events API service
- `src/api/agents.ts` - Agents API service
- `src/api/auth.ts` - Authentication API service

**Expected Pattern**:
```typescript
// src/api/events.ts (EXAMPLE)
import apiClient from './client'
import type { Event, PaginatedResponse, PaginationParams } from '@/core/types'

export const eventsApi = {
  async list(params?: PaginationParams): Promise<PaginatedResponse<Event>> {
    return apiClient.get('/events', { params })
  },

  async getById(id: string): Promise<Event> {
    return apiClient.get(`/events/${id}`)
  },

  async create(event: Partial<Event>): Promise<Event> {
    return apiClient.post('/events', event)
  }
}
```

---

## Application Layer

### Location: `src/store/`, `src/composables/`

**Purpose**: Business logic, state management, and reusable composition functions

### State Management - Pinia Stores

#### Auth Store (`src/store/modules/auth.store.ts`)

**Current Implementation**: Basic structure with TODO placeholders

```typescript
State:
- user: User | null           // Current user
- token: string | null        // JWT token
- isAuthenticated: boolean    // Computed from token

Actions:
- login(credentials)          // TODO: Implement
- logout()                    // Clear user & token
```

**Status**: 🟡 Partial implementation

#### Missing Stores (PLANNED)

1. **Events Store** (`src/store/modules/events.store.ts`)
   ```typescript
   State:
   - events: Event[]
   - loading: boolean
   - error: string | null
   - currentPage: number
   - totalItems: number

   Getters:
   - criticalEvents: Event[]
   - highSeverityEvents: Event[]
   - totalPages: number

   Actions:
   - fetchEvents(params?)
   - fetchEventById(id)
   - reset()
   ```

2. **Agents Store** (`src/store/modules/agents.store.ts`)
   ```typescript
   State:
   - agents: Agent[]
   - loading: boolean
   - error: string | null

   Actions:
   - fetchAgents()
   - fetchAgentById(account, region)
   - deployAgent(account, region)
   ```

### Composables (PLANNED)

**Purpose**: Encapsulate reusable logic using Composition API

**Missing Composables**:
- `src/composables/useEvents.ts` - Event management logic
- `src/composables/useAgents.ts` - Agent management logic
- `src/composables/usePagination.ts` - Pagination logic
- `src/composables/usePolling.ts` - Auto-refresh logic
- `src/composables/useErrorHandler.ts` - Error handling logic

**Expected Pattern**:
```typescript
// src/composables/useEvents.ts (EXAMPLE)
export function useEvents(params?: PaginationParams) {
  const events = ref<Event[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)

  async function fetchEvents() {
    loading.value = true
    try {
      const response = await eventsApi.list(params)
      events.value = response.items
    } catch (err) {
      error.value = err as Error
    } finally {
      loading.value = false
    }
  }

  onMounted(() => fetchEvents())

  return { events, loading, error, fetchEvents }
}
```

---

## Presentation Layer

### Location: `src/pages/`, `src/components/`

**Purpose**: UI components and page entry points

### Pages (`src/pages/`)

#### Dashboard (`src/pages/Dashboard.vue`)

**Purpose**: Landing page with navigation cards

**Current State**: ✅ Implemented (basic)

**Features**:
- Welcome message
- Navigation cards to Events and Agents pages
- Tailwind CSS styling

**Structure**:
```vue
<script setup lang="ts">
- message: ref<string>
</script>

<template>
- Container with hero section
- 2-column grid with navigation cards
  - Events card → /events
  - Agents card → /agents
</template>
```

#### Events List Page (`src/pages/Events/EventsListPage.vue`)

**Purpose**: Display and manage events

**Current State**: 🟡 Skeleton only

**Current Features**:
- Empty state message
- Back to dashboard link

**Planned Features**:
- Event list with pagination
- Filtering by severity, source, date
- Sorting capabilities
- Event detail modal
- Real-time updates via polling

#### Agents List Page (`src/pages/Agents/AgentsListPage.vue`)

**Purpose**: Display and manage monitoring agents

**Current State**: 🟡 Skeleton only

**Current Features**:
- Empty state message
- Back to dashboard link

**Planned Features**:
- Agent list by account/region
- Status indicators
- Deploy agent action
- Agent details
- Health monitoring

#### Not Found Page (`src/pages/ErrorPages/NotFound.vue`)

**Purpose**: 404 error page

**Current State**: ❌ Not implemented (route exists)

### Components (`src/components/`) - PLANNED

**Directory Structure** (recommended):
```
src/components/
├── common/              # Generic reusable components
│   ├── Button.vue
│   ├── Card.vue
│   ├── Modal.vue
│   ├── LoadingSpinner.vue
│   ├── EmptyState.vue
│   └── Pagination.vue
├── events/              # Event-specific components
│   ├── EventCard.vue
│   ├── EventList.vue
│   ├── EventFilters.vue
│   ├── EventDetail.vue
│   └── SeverityBadge.vue
└── agents/              # Agent-specific components
    ├── AgentCard.vue
    ├── AgentList.vue
    ├── AgentStatus.vue
    └── DeployAgentModal.vue
```

**Status**: ❌ Directory does not exist yet

---

## Routing & Navigation

### Location: `src/router/`

### Router Setup (`src/router/index.ts`)

**Configuration**:
- History mode: HTML5 History API (`createWebHistory`)
- Base URL: From `import.meta.env.BASE_URL`
- Guards: Setup via `setupGuards(router)`

### Route Definitions (`src/router/routes/index.ts`)

**Current Routes**:

| Path | Name | Component | Auth Required | Page Title |
|------|------|-----------|---------------|------------|
| `/` | Dashboard | Dashboard.vue | ❌ No | Dashboard |
| `/events` | Events | EventsListPage.vue | ❌ No | Events |
| `/agents` | Agents | AgentsListPage.vue | ❌ No | Agents |
| `/:pathMatch(.*)*` | NotFound | NotFound.vue | N/A | (404) |

**Route Features**:
- Lazy loading via dynamic imports
- Route meta: `requiresAuth`, `title`

### Navigation Guards (`src/router/routes/guards.ts`)

**Before Each (Auth Guard)**:
- Check `requiresAuth` meta
- Redirect to Login if unauthenticated
- Pass redirect query parameter

**After Each (Title Guard)**:
- Set document title from route meta
- Format: `{Page Title} - AWS Monitoring`

---

## Build & Configuration

### Vite Configuration (`vite.config.ts`)

**Plugins**:
- `@vitejs/plugin-vue` - Vue 3 SFC support

**Resolve**:
- Alias: `@` → `./src`

**Dev Server**:
- Port: `3000`
- Proxy: `/api` → `http://localhost:3001`
  - Rewrites path: `/api/events` → `/events`
  - Purpose: Proxy to LocalStack API Gateway

**Build**:
- Source maps: Enabled
- Manual chunks:
  - `vendor`: vue, vue-router, pinia
  - `ui`: @vueuse/core

### TypeScript Configuration

**Root Config (`tsconfig.json`)**:
- References app and node configs

**App Config (`tsconfig.app.json`)**:
- Extends: `@vue/tsconfig/tsconfig.dom.json`
- Strict mode: Enabled
- Unused locals/params: Error
- Path alias: `@/*` → `./src/*`
- Includes: `src/**/*.ts`, `src/**/*.tsx`, `src/**/*.vue`

**Node Config (`tsconfig.node.json`)**:
- For Vite config and build scripts

### Tailwind Configuration (`tailwind.config.js`)

**Content**: HTML and Vue/TS files in src

**Custom Theme Extensions**:

**Colors**:
```javascript
severity: {
  critical: '#DC2626',  // Red
  high: '#F59E0B',      // Amber
  medium: '#3B82F6',    // Blue
  low: '#10B981',       // Green
  unknown: '#6B7280'    // Gray
}

status: {
  active: '#10B981',    // Green
  inactive: '#EF4444',  // Red
  deploying: '#3B82F6', // Blue
  failed: '#DC2626'     // Red
}
```

**Fonts**:
- Sans: Inter, system-ui
- Mono: Fira Code, monospace

**Plugins**:
- `@tailwindcss/forms` - Form styling
- `@tailwindcss/typography` - Rich text styling

### Global Styles (`src/styles/`)

**main.css**:
- Imports: variables.css, utilities.css
- Tailwind directives: @tailwind base/components/utilities
- Base layer overrides: body, headings

**variables.css**:
- CSS custom properties
- Theme variables

**utilities.css**:
- Custom utility classes

---

## Testing Strategy

### Test Configuration (`vitest.config.ts`)

**Environment**: `happy-dom` (lightweight DOM simulation)

**Globals**: Enabled (no need to import `describe`, `it`, `expect`)

**Coverage**:
- Provider: v8
- Reporters: text, json, html
- Excludes: node_modules, .d.ts, .spec.ts, .test.ts

### Current Test State

**Status**: ❌ No tests exist yet

**Expected Test Structure**:
```
src/
├── __tests__/              # Test directory
│   ├── components/         # Component tests
│   ├── pages/              # Page tests
│   ├── store/              # Store tests
│   ├── composables/        # Composable tests
│   └── api/                # API service tests
```

**Coverage Goals** (from CLAUDE.md):
- Minimum: 80% overall
- Target: >90% for critical components
- 100%: Utilities, stores, composables

### Test Patterns (from CLAUDE.md)

**Component Testing**:
```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import EventCard from '@/components/events/EventCard.vue'

describe('EventCard', () => {
  it('renders event details correctly', () => {
    const wrapper = mount(EventCard, { props: { event: mockEvent } })
    expect(wrapper.text()).toContain('CloudWatch Alarm')
  })
})
```

**Store Testing**:
```typescript
import { setActivePinia, createPinia } from 'pinia'
import { useEventsStore } from '@/store/modules/events.store'

describe('Events Store', () => {
  beforeEach(() => setActivePinia(createPinia()))

  it('fetches events successfully', async () => {
    const store = useEventsStore()
    await store.fetchEvents()
    expect(store.events).toEqual(mockResponse.items)
  })
})
```

---

## Development Patterns

### Vue 3 Composition API Pattern

**Preferred Style**: `<script setup>` with TypeScript

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Event } from '@/core/types'

// Props interface
interface Props {
  eventId: string
  showDetails?: boolean
}

// Props with defaults
const props = withDefaults(defineProps<Props>(), {
  showDetails: false
})

// Emits (typed)
const emit = defineEmits<{
  update: [event: Event]
  delete: [id: string]
}>()

// Reactive state
const event = ref<Event | null>(null)
const loading = ref(false)

// Computed properties
const formattedDate = computed(() => {
  if (!event.value) return ''
  return new Date(event.value.published_at).toLocaleDateString()
})

// Methods
async function fetchEvent() {
  loading.value = true
  try {
    event.value = await eventsApi.getById(props.eventId)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => fetchEvent())
</script>

<template>
  <div v-if="loading">Loading...</div>
  <div v-else-if="event">
    <h2>{{ event.detail_type }}</h2>
    <p>{{ formattedDate }}</p>
  </div>
</template>

<style scoped>
/* Component-specific styles */
</style>
```

### Type Safety Patterns

**Explicit Types**:
```typescript
// Define interfaces
export interface Event {
  id: string
  severity: number
}

// Use type guards
export function isEvent(obj: unknown): obj is Event {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj
  )
}

// Generic responses
export interface ApiResponse<T> {
  data: T
  success: boolean
}
```

### Naming Conventions

**Files**:
- Components: PascalCase (e.g., `EventCard.vue`)
- Composables: camelCase with `use` prefix (e.g., `useEvents.ts`)
- Stores: camelCase with `.store.ts` suffix (e.g., `events.store.ts`)
- Types: kebab-case or index (e.g., `index.ts`)

**Code**:
- Variables: camelCase
- Constants: UPPER_SNAKE_CASE
- Types/Interfaces: PascalCase
- Enums: PascalCase

### API Integration Pattern

**3-Layer Pattern**:
1. **API Client** → HTTP communication
2. **API Service** → Endpoint-specific logic
3. **Store/Composable** → State management & business logic

```typescript
// 1. API Client (infrastructure)
const apiClient = new ApiClient()

// 2. API Service (infrastructure)
export const eventsApi = {
  list: (params) => apiClient.get('/events', { params }),
  getById: (id) => apiClient.get(`/events/${id}`)
}

// 3. Store (application)
export const useEventsStore = defineStore('events', () => {
  const events = ref([])

  async function fetchEvents() {
    events.value = await eventsApi.list()
  }

  return { events, fetchEvents }
})
```

---

## Dependencies Map

### Production Dependencies

| Package | Version | Purpose | Used In |
|---------|---------|---------|---------|
| `vue` | 3.5.24 | Core framework | Entire app |
| `pinia` | 3.0.4 | State management | stores/ |
| `vue-router` | 4.6.3 | Routing | router/ |
| `axios` | 1.13.2 | HTTP client | api/client.ts |
| `@vueuse/core` | 14.0.0 | Composition utilities | TBD |
| `date-fns` | 4.1.0 | Date formatting | TBD |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `vite` | 7.2.2 | Build tool & dev server |
| `vue-tsc` | 3.1.3 | TypeScript type checking |
| `typescript` | 5.9.3 | TypeScript compiler |
| `vitest` | 4.0.9 | Testing framework |
| `@vue/test-utils` | 2.4.6 | Vue component testing |
| `happy-dom` | 20.0.10 | DOM simulation for tests |
| `tailwindcss` | 3.4.1 | CSS framework |
| `@tailwindcss/forms` | 0.5.10 | Form styling plugin |
| `@tailwindcss/typography` | 0.5.19 | Typography plugin |
| `eslint` | 9.39.1 | Code linting |
| `prettier` | 3.6.2 | Code formatting |
| `autoprefixer` | 10.4.22 | CSS vendor prefixes |
| `postcss` | 8.5.6 | CSS processing |

### Internal Dependencies

**Import Patterns**:
```typescript
// Core domain
import type { Event, Agent } from '@/core/types'
import { EventSeverity } from '@/core/enums'
import { API_CONFIG } from '@/core/constants'

// Infrastructure
import { apiClient } from '@/api/client'

// Application
import { useAuthStore } from '@/store/modules/auth.store'

// Presentation
import EventCard from '@/components/events/EventCard.vue'
```

**Path Alias**: `@` resolves to `src/`

---

## Quick Reference

### Component Implementation Checklist

When adding a new component:
1. ✅ Create `.vue` file with PascalCase name
2. ✅ Use `<script setup lang="ts">`
3. ✅ Define Props interface if needed
4. ✅ Define Emits if needed
5. ✅ Add proper TypeScript types
6. ✅ Use Tailwind CSS for styling
7. ✅ Write component tests
8. ✅ Document props in comments

### Page Implementation Checklist

When adding a new page:
1. ✅ Create page in `src/pages/`
2. ✅ Add route to `src/router/routes/index.ts`
3. ✅ Set route meta (requiresAuth, title)
4. ✅ Create API service if needed
5. ✅ Create store if needed
6. ✅ Create composable for logic
7. ✅ Write page tests
8. ✅ Update navigation links

### Store Implementation Checklist

When adding a new store:
1. ✅ Create file in `src/store/modules/`
2. ✅ Use `defineStore` with setup syntax
3. ✅ Define state with proper types
4. ✅ Add computed getters
5. ✅ Add actions for mutations
6. ✅ Handle loading & error states
7. ✅ Write store tests
8. ✅ Mock in component tests

### API Service Implementation Checklist

When adding a new API service:
1. ✅ Create file in `src/api/`
2. ✅ Import types from `@/core/types`
3. ✅ Import apiClient
4. ✅ Export service object with methods
5. ✅ Add proper TypeScript return types
6. ✅ Handle errors appropriately
7. ✅ Write service tests
8. ✅ Document expected responses

### Development Workflow

**Starting Development**:
```bash
cd frontend
npm install           # First time only
npm run dev           # Start dev server on :3000
```

**Common Commands**:
```bash
npm run dev           # Dev server with HMR
npm run build         # Production build
npm run preview       # Preview production build
npm run test          # Run tests
npm run test:ui       # Tests with UI
npm run test:coverage # Coverage report
npm run lint          # Check linting
npm run lint:fix      # Fix linting issues
npm run format        # Format with Prettier
npm run type-check    # Check TypeScript types
```

**Pre-commit Checklist**:
- [ ] `npm run lint` passes
- [ ] `npm run type-check` passes
- [ ] `npm run test` passes
- [ ] Coverage > 80%

### File Locations Quick Reference

| What | Where |
|------|-------|
| Types | `src/core/types/index.ts` |
| Enums | `src/core/enums/index.ts` |
| Constants | `src/core/constants.ts` |
| API Client | `src/api/client.ts` |
| API Services | `src/api/{domain}.ts` |
| Stores | `src/store/modules/{domain}.store.ts` |
| Composables | `src/composables/use{Name}.ts` |
| Components | `src/components/{domain}/{Name}.vue` |
| Pages | `src/pages/{Feature}/{Name}Page.vue` |
| Routes | `src/router/routes/index.ts` |
| Guards | `src/router/routes/guards.ts` |
| Styles | `src/styles/` |

### Environment Variables

**Development** (`.env.development`):
```bash
VITE_API_BASE_URL=http://localhost:3001/api
VITE_APP_TITLE=AWS Monitoring
VITE_ENABLE_DEBUG=true
VITE_POLLING_INTERVAL=30000
```

**Production** (`.env.production`):
```bash
VITE_API_BASE_URL=https://api.production.com
VITE_APP_TITLE=AWS Monitoring
VITE_ENABLE_DEBUG=false
```

**Access in code**:
```typescript
import.meta.env.VITE_API_BASE_URL
import.meta.env.VITE_ENABLE_DEBUG
```

### Known Issues & TODs

**High Priority**:
1. ❌ No components directory exists
2. ❌ No tests exist
3. ❌ Auth not implemented (TODO comments in code)
4. ❌ Events API service missing
5. ❌ Agents API service missing
6. ❌ Events store missing
7. ❌ Agents store missing
8. ❌ No composables implemented

**Medium Priority**:
1. 🟡 Pages are skeleton only (Events, Agents)
2. 🟡 No error boundaries
3. 🟡 No loading states in pages
4. 🟡 No pagination implementation
5. 🟡 No filtering/sorting

**Low Priority**:
1. 📝 Environment files not created
2. 📝 No PWA configuration
3. 📝 No analytics integration
4. 📝 No monitoring/logging setup

---

## Index Metadata

**Last Updated**: 2025-11-17
**Indexed Files**: 31
**Directories Mapped**: 17
**Lines of Code**: ~800 (excluding dependencies)
**Test Coverage**: 0% (no tests exist)
**Documentation Coverage**: High (CLAUDE.md exists)

**Index Completeness**:
- ✅ Directory structure: 100%
- ✅ Core types: 100%
- ✅ API client: 100%
- ✅ Routing: 100%
- ✅ Configuration: 100%
- 🟡 Stores: 33% (1 of 3 expected)
- 🟡 Pages: 60% (basic implementation)
- ❌ Components: 0%
- ❌ Composables: 0%
- ❌ Tests: 0%
- ❌ API Services: 33% (client only)

**Next Steps for Developers**:
1. Create component library (`src/components/`)
2. Implement API services for events and agents
3. Create stores for events and agents
4. Develop composables for reusable logic
5. Write comprehensive tests (target >80% coverage)
6. Implement actual page functionality (not just skeletons)
7. Add error handling and loading states
8. Implement authentication flow

---

**End of Frontend Index**

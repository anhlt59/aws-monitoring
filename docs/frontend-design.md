# Frontend Application Design

## Overview

This document outlines the frontend architecture for the AWS Monitoring application using Vue 3, TypeScript, and Tailwind CSS. The design follows Separation of Concerns principles and maps to the hexagonal architecture used in the backend.

## Architecture Mapping (Backend → Frontend)

| Backend Layer | Frontend Equivalent | Purpose |
|---------------|-------------------|---------|
| Domain (models, use cases) | `core/` + `composables/` | Business logic and domain entities |
| Ports (interfaces) | `core/types/` | Contracts and type definitions |
| Adapters (repositories, AWS services) | `api/` | External service communication |
| Entrypoints (Lambda handlers, API Gateway) | `pages/` + `router/` | Application entry points |
| Common (utilities, config) | `utils/` + `core/constants.ts` | Shared utilities |

## Complete Directory Structure

```
frontend/
├── public/                          # Static assets served as-is
│   ├── favicon.ico
│   └── robots.txt
│
├── src/
│   ├── assets/                      # Build-time static resources
│   │   ├── images/
│   │   │   ├── logo.svg
│   │   │   └── icons/
│   │   └── fonts/
│   │
│   ├── core/                        # Domain Layer (Business Entities)
│   │   ├── types/                   # TypeScript Interfaces/Types
│   │   │   ├── event.ts            # Monitoring event types
│   │   │   ├── agent.ts            # Agent types
│   │   │   ├── api.ts              # API request/response types
│   │   │   ├── common.ts           # Shared types (Pagination, etc.)
│   │   │   └── index.ts            # Type exports
│   │   ├── enums/                   # Enumerations
│   │   │   ├── severity.ts         # Event severity levels
│   │   │   ├── status.ts           # Agent/deployment status
│   │   │   └── index.ts
│   │   └── constants.ts             # Global constants
│   │
│   ├── api/                         # Infrastructure Layer (External Communication)
│   │   ├── modules/                 # Domain-specific API services
│   │   │   ├── events.api.ts       # Event-related API calls
│   │   │   ├── agents.api.ts       # Agent-related API calls
│   │   │   └── reports.api.ts      # Report-related API calls
│   │   ├── client.ts                # HTTP client configuration (Axios/Fetch)
│   │   ├── interceptors.ts          # Request/response interceptors
│   │   └── index.ts                 # API exports
│   │
│   ├── composables/                 # Application Logic Layer (Business Logic)
│   │   ├── features/                # Feature-specific composables
│   │   │   ├── useEvents.ts        # Event fetching, filtering, pagination
│   │   │   ├── useAgents.ts        # Agent management logic
│   │   │   ├── useReports.ts       # Report generation logic
│   │   │   └── useAuth.ts          # Authentication logic
│   │   ├── ui/                      # UI-related composables
│   │   │   ├── useModal.ts         # Modal state management
│   │   │   ├── useToast.ts         # Toast notifications
│   │   │   ├── useTheme.ts         # Theme switching
│   │   │   └── usePagination.ts    # Pagination logic
│   │   └── utils/                   # Utility composables
│   │       ├── useDebounce.ts
│   │       ├── useAsync.ts         # Async state management
│   │       └── useLocalStorage.ts
│   │
│   ├── store/                       # State Management (Pinia)
│   │   ├── modules/
│   │   │   ├── auth.store.ts       # Authentication state
│   │   │   ├── events.store.ts     # Events cache/state
│   │   │   ├── agents.store.ts     # Agents state
│   │   │   └── ui.store.ts         # UI state (sidebar, theme, etc.)
│   │   └── index.ts                 # Store setup and exports
│   │
│   ├── components/                  # Presentation Layer
│   │   ├── base/                    # Dumb/UI Components (no business logic)
│   │   │   ├── buttons/
│   │   │   │   ├── BaseButton.vue
│   │   │   │   └── IconButton.vue
│   │   │   ├── inputs/
│   │   │   │   ├── BaseInput.vue
│   │   │   │   ├── BaseSelect.vue
│   │   │   │   ├── BaseTextarea.vue
│   │   │   │   └── DateRangePicker.vue
│   │   │   ├── layout/
│   │   │   │   ├── Card.vue
│   │   │   │   ├── Container.vue
│   │   │   │   └── Grid.vue
│   │   │   ├── feedback/
│   │   │   │   ├── Modal.vue
│   │   │   │   ├── Toast.vue
│   │   │   │   ├── Alert.vue
│   │   │   │   ├── Spinner.vue
│   │   │   │   └── Badge.vue
│   │   │   ├── navigation/
│   │   │   │   ├── Tabs.vue
│   │   │   │   └── Pagination.vue
│   │   │   └── data-display/
│   │   │       ├── Table.vue
│   │   │       ├── EmptyState.vue
│   │   │       └── StatCard.vue
│   │   │
│   │   ├── modules/                 # Smart/Feature Components (with business logic)
│   │   │   ├── events/
│   │   │   │   ├── EventList.vue           # List of events with filtering
│   │   │   │   ├── EventCard.vue           # Single event display
│   │   │   │   ├── EventFilters.vue        # Filter controls
│   │   │   │   ├── EventDetails.vue        # Detailed event view
│   │   │   │   └── SeverityIndicator.vue   # Visual severity display
│   │   │   ├── agents/
│   │   │   │   ├── AgentList.vue           # List of agents
│   │   │   │   ├── AgentCard.vue           # Single agent display
│   │   │   │   ├── AgentStatusBadge.vue    # Status indicator
│   │   │   │   └── AgentDeploymentForm.vue # Deployment form
│   │   │   ├── reports/
│   │   │   │   ├── DailyReportSummary.vue  # Report summary view
│   │   │   │   ├── ReportFilters.vue       # Report filtering
│   │   │   │   └── ReportChart.vue         # Data visualization
│   │   │   ├── dashboard/
│   │   │   │   ├── DashboardStats.vue      # Overview statistics
│   │   │   │   ├── RecentEvents.vue        # Recent events widget
│   │   │   │   └── AgentHealthMap.vue      # Agent health overview
│   │   │   └── auth/
│   │   │       └── LoginForm.vue           # Authentication form
│   │   │
│   │   └── layout/                  # App-level layout components
│   │       ├── AppHeader.vue
│   │       ├── AppSidebar.vue
│   │       ├── AppFooter.vue
│   │       └── AppLayout.vue
│   │
│   ├── pages/                       # Route Entry Points (Views)
│   │   ├── Dashboard.vue            # Main dashboard page
│   │   ├── Events/
│   │   │   ├── EventsListPage.vue  # Events listing page
│   │   │   └── EventDetailPage.vue # Event detail page
│   │   ├── Agents/
│   │   │   ├── AgentsListPage.vue  # Agents listing page
│   │   │   └── AgentDetailPage.vue # Agent detail page
│   │   ├── Reports/
│   │   │   └── ReportsPage.vue     # Reports page
│   │   ├── Auth/
│   │   │   └── LoginPage.vue       # Login page
│   │   └── ErrorPages/
│   │       ├── NotFound.vue        # 404 page
│   │       └── ServerError.vue     # 500 page
│   │
│   ├── router/                      # Vue Router Configuration
│   │   ├── routes/
│   │   │   ├── index.ts            # Main routes definition
│   │   │   ├── auth.routes.ts      # Auth-related routes
│   │   │   └── guards.ts           # Route guards (auth, permissions)
│   │   └── index.ts                 # Router setup
│   │
│   ├── styles/                      # Global Styles & Tailwind Config
│   │   ├── main.css                 # Tailwind imports + global styles
│   │   ├── variables.css            # CSS custom properties
│   │   └── utilities.css            # Custom Tailwind utilities
│   │
│   ├── utils/                       # Utility Functions
│   │   ├── datetime.ts              # Date/time formatting
│   │   ├── formatters.ts            # Data formatters
│   │   ├── validators.ts            # Validation helpers
│   │   └── storage.ts               # LocalStorage helpers
│   │
│   ├── App.vue                      # Root component
│   └── main.ts                      # Application entry point
│
├── tests/                           # Test files (mirrors src/ structure)
│   ├── unit/
│   │   ├── components/
│   │   ├── composables/
│   │   └── utils/
│   └── e2e/
│
├── .env.development                 # Development environment variables
├── .env.production                  # Production environment variables
├── index.html                       # HTML entry point
├── package.json                     # Node dependencies
├── tailwind.config.js               # Tailwind CSS configuration
├── tsconfig.json                    # TypeScript configuration
├── vite.config.ts                   # Vite build configuration
└── README.md                        # Frontend documentation
```

## Layer Responsibilities

### 1. Core Layer (`core/`)

**Purpose:** Define the domain model and business entities (equivalent to backend domain layer)

**Contains:**
- **types/**: TypeScript interfaces for all domain entities
- **enums/**: Enumeration types for constants
- **constants.ts**: Application-wide constants

**Rules:**
- Pure TypeScript (no Vue imports)
- No external dependencies except TypeScript utilities
- These types are the source of truth for the entire application

**Example Type Structure:**

```typescript
// core/types/event.ts
interface Event {
  id: string;
  account: string;
  region: string;
  source: string;
  detail: Record<string, unknown>;
  detail_type: string;
  severity: Severity;
  resources: string[];
  published_at: number;
  updated_at: number;
}

// core/types/api.ts
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}
```

### 2. API Layer (`api/`)

**Purpose:** External service communication (equivalent to backend adapters)

**Contains:**
- **modules/**: Domain-specific API services
- **client.ts**: HTTP client setup (Axios/Fetch configuration)
- **interceptors.ts**: Request/response interceptors

**Rules:**
- All API calls go through this layer
- Returns typed responses using core types
- Handles HTTP errors and transforms to domain errors
- No business logic - only communication

**Responsibilities:**
- Configure base URL, headers, timeouts
- Handle authentication tokens
- Transform API responses to domain types
- Error handling and retry logic

### 3. Composables Layer (`composables/`)

**Purpose:** Reusable business logic (equivalent to backend use cases)

**Contains:**
- **features/**: Feature-specific business logic
- **ui/**: UI state and interaction logic
- **utils/**: Generic reusable logic

**Rules:**
- Uses Vue's Composition API (ref, computed, watch, etc.)
- Can call API layer and store
- Returns reactive state and methods
- Reusable across multiple components

**Responsibilities:**
- Data fetching and caching
- Form validation and submission
- Complex calculations
- Side effect management

**Example Composable Pattern:**

```typescript
// composables/features/useEvents.ts
function useEvents() {
  // State
  const events = ref<Event[]>([]);
  const isLoading = ref(false);
  const error = ref<ApiError | null>(null);

  // Computed
  const criticalEvents = computed(() =>
    events.value.filter(e => e.severity === Severity.Critical)
  );

  // Methods
  const fetchEvents = async (filters: EventFilters) => {
    // API call logic
  };

  const refreshEvents = async () => {
    // Refresh logic
  };

  // Return public interface
  return {
    events,
    isLoading,
    error,
    criticalEvents,
    fetchEvents,
    refreshEvents
  };
}
```

### 4. Store Layer (`store/`)

**Purpose:** Global state management using Pinia

**Contains:**
- **modules/**: Domain-specific stores
- **index.ts**: Store configuration

**When to use Store vs Composable:**
- **Store**: Global state shared across many components (auth, user preferences)
- **Composable**: Local state or logic for specific features

**Example Store Structure:**

```typescript
// store/modules/auth.store.ts
defineStore('auth', () => {
  const user = ref<User | null>(null);
  const token = ref<string | null>(null);
  const isAuthenticated = computed(() => !!token.value);

  const login = async (credentials: LoginCredentials) => {
    // Login logic
  };

  const logout = () => {
    // Logout logic
  };

  return { user, token, isAuthenticated, login, logout };
});
```

### 5. Components Layer (`components/`)

**Purpose:** UI presentation (split into dumb and smart components)

#### 5.1. Base Components (`components/base/`)

**Characteristics:**
- No business logic
- Receive data via props only
- Emit events for parent handling
- Highly reusable
- Styled with Tailwind CSS

**Categories:**
- **buttons/**: All button variants
- **inputs/**: Form inputs (text, select, date, etc.)
- **layout/**: Layout primitives (card, container, grid)
- **feedback/**: User feedback (modal, toast, alert, spinner)
- **navigation/**: Navigation elements (tabs, pagination)
- **data-display/**: Data presentation (table, empty state, stats)

#### 5.2. Module Components (`components/modules/`)

**Characteristics:**
- Contains presentation logic
- Uses composables and stores
- Composed of base components
- Feature-specific

**Organization:** Group by feature (events, agents, reports, dashboard, auth)

### 6. Pages Layer (`pages/`)

**Purpose:** Route entry points (equivalent to backend entrypoints)

**Characteristics:**
- One page per route
- Composes module components
- Minimal logic (delegates to composables)
- Handles page-level concerns (metadata, loading states)

**Naming Convention:**
- `{Feature}ListPage.vue` for listing pages
- `{Feature}DetailPage.vue` for detail pages
- `{Feature}Page.vue` for single purpose pages

### 7. Router Layer (`router/`)

**Purpose:** Application routing and navigation

**Contains:**
- **routes/**: Route definitions organized by feature
- **guards.ts**: Route guards for authentication and authorization

**Features:**
- Lazy loading for code splitting
- Route metadata (title, auth requirements)
- Navigation guards

## Data Flow Architecture

### Read Flow (Display Data)

```
User Action (Page)
    ↓
Composable (useEvents)
    ↓
API Service (events.api.ts)
    ↓
HTTP Client (axios)
    ↓
Backend API Gateway
    ↓
Response transforms through same path back
    ↓
Component renders with reactive data
```

### Write Flow (Modify Data)

```
User Action (Form Submit)
    ↓
Module Component (EventFilters)
    ↓
Composable (useEvents.createEvent)
    ↓
API Service (events.api.ts)
    ↓
Backend Lambda
    ↓
Success/Error handling
    ↓
Update local state (optimistic or after response)
    ↓
UI updates reactively
```

### State Management Flow

```
User Action
    ↓
Component calls Store action
    ↓
Store updates state
    ↓
Components using store react automatically
```

## Integration with Backend

### API Endpoints Mapping

| Backend Endpoint | Frontend API Service | Composable | Page |
|-----------------|---------------------|------------|------|
| `GET /events` | `events.api.ts::getEvents()` | `useEvents()` | `EventsListPage.vue` |
| `GET /events/{id}` | `events.api.ts::getEventById()` | `useEvents()` | `EventDetailPage.vue` |
| `GET /agents` | `agents.api.ts::getAgents()` | `useAgents()` | `AgentsListPage.vue` |
| `POST /agents` | `agents.api.ts::createAgent()` | `useAgents()` | `AgentsListPage.vue` |
| `PUT /agents/{id}` | `agents.api.ts::updateAgent()` | `useAgents()` | `AgentDetailPage.vue` |

### Environment Configuration

```typescript
// core/constants.ts
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL,
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3
};

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100
};

export const POLLING = {
  EVENTS_REFRESH_INTERVAL: 30000, // 30 seconds
  AGENTS_REFRESH_INTERVAL: 60000  // 1 minute
};
```

## Key Design Principles

### 1. Separation of Concerns

Each layer has a single responsibility:
- **Core**: Data structures
- **API**: Communication
- **Composables**: Business logic
- **Components**: Presentation
- **Pages**: Routing
- **Store**: Global state

### 2. Dependency Direction

Dependencies flow inward:
```
Pages → Components → Composables → API → Backend
         ↓              ↓
       Store         Core Types
```

### 3. Type Safety

- All data structures defined in `core/types/`
- API responses typed
- Component props typed
- Store state typed
- No `any` types in production code

### 4. Reusability

- Base components are highly reusable
- Composables encapsulate reusable logic
- Utils provide pure functions
- Store modules are domain-focused

### 5. Testability

- Base components: Test props and events
- Module components: Test with mocked composables
- Composables: Test with mocked API
- API: Test with mocked HTTP client

## Styling Strategy (Tailwind CSS)

### Component Styling Approach

1. **Base Components**: Use Tailwind utility classes directly
2. **Module Components**: Compose base components, minimal custom styling
3. **Pages**: Layout only, no styling logic

### Tailwind Configuration

```javascript
// tailwind.config.js structure
module.exports = {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Custom color palette for severity levels
        severity: {
          critical: '#DC2626',
          high: '#F59E0B',
          medium: '#3B82F6',
          low: '#10B981',
          unknown: '#6B7280'
        },
        // Custom color palette for agent status
        status: {
          active: '#10B981',
          inactive: '#EF4444',
          deploying: '#3B82F6'
        }
      },
      spacing: {
        // Custom spacing if needed
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ]
};
```

### Custom Utilities

```css
/* styles/utilities.css */
@layer utilities {
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }

  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
}
```

## State Management Strategy

### When to use Pinia Store

Use for:
- Authentication state (user, token)
- Global UI state (theme, sidebar open/closed)
- User preferences
- Data that needs to persist across navigation

### When to use Composables

Use for:
- Feature-specific data fetching
- Form state
- Local component state
- Temporary UI state

### When to use Component State

Use for:
- Purely presentational state (hover, focus)
- Single-component state
- Ephemeral UI state

## Performance Considerations

### Code Splitting

- Lazy load routes: `component: () => import('./pages/Events/EventsListPage.vue')`
- Lazy load heavy components
- Dynamic imports for large libraries

### Caching Strategy

- API layer caches GET requests (configurable TTL)
- Store persists to localStorage (auth, preferences)
- Implement stale-while-revalidate pattern

### Optimizations

- Virtual scrolling for large lists (events table)
- Debounce search inputs
- Throttle scroll events
- Memoize expensive computed properties

## Error Handling Strategy

### Levels of Error Handling

1. **API Layer**: Transform HTTP errors to domain errors
2. **Composables**: Catch and expose errors to components
3. **Components**: Display errors to users
4. **Global**: Catch-all error boundary

### Error Display

- Toast notifications for transient errors
- Inline errors for form validation
- Empty states for failed data fetching
- Error pages for critical failures

## Development Workflow

### Component Development Flow

1. Define types in `core/types/`
2. Create API service in `api/modules/`
3. Develop composable in `composables/features/`
4. Build base components if needed
5. Create module components using base components
6. Compose page from module components
7. Add route in `router/routes/`
8. Write tests

### Testing Strategy

- **Unit Tests**: Base components, composables, utils
- **Integration Tests**: Module components with mocked API
- **E2E Tests**: Critical user flows (login, view events, filter)

## File Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Vue Components | PascalCase | `EventList.vue`, `BaseButton.vue` |
| Composables | camelCase with `use` prefix | `useEvents.ts`, `useDebounce.ts` |
| API Services | camelCase with `.api` suffix | `events.api.ts`, `agents.api.ts` |
| Types | PascalCase | `Event`, `Agent`, `ApiResponse` |
| Stores | camelCase with `.store` suffix | `auth.store.ts`, `events.store.ts` |
| Utils | camelCase | `datetime.ts`, `formatters.ts` |
| Pages | PascalCase with `Page` suffix | `EventsListPage.vue`, `DashboardPage.vue` |

## Next Steps for Implementation

1. **Project Setup**: Initialize Vite + Vue 3 + TypeScript + Tailwind
2. **Core Types**: Define all domain types matching backend models
3. **API Client**: Configure HTTP client with interceptors
4. **Base Components**: Build UI component library
5. **Authentication**: Implement auth flow (login, token management)
6. **Dashboard**: Create main dashboard as first feature
7. **Events Module**: Implement events listing and filtering
8. **Agents Module**: Implement agents management
9. **Reports Module**: Implement reports visualization

## Summary

This frontend architecture provides:

- **Clear separation of concerns** matching your backend hexagonal architecture
- **Type safety** throughout the application
- **Scalability** through modular design
- **Maintainability** with consistent patterns
- **Testability** at every layer
- **Developer experience** familiar to backend developers

The structure allows backend developers to easily understand the frontend codebase by mapping it to familiar concepts like domain models, use cases, adapters, and entrypoints.

# Frontend Development Guide

This guide provides detailed instructions for working with the Vue 3 frontend codebase.

## Tech Stack

- **Framework**: Vue 3 (Composition API with `<script setup>`)
- **Language**: TypeScript 5.9
- **Build Tool**: Vite 7.x
- **State Management**: Pinia 3.x
- **Routing**: Vue Router 4.x
- **Styling**: Tailwind CSS 3.x
- **HTTP Client**: Axios 1.x
- **Testing**: Vitest 4.x, Vue Test Utils
- **Utilities**: VueUse, date-fns

## Architecture

The frontend follows a layered architecture with clear separation of concerns:

### Core Layer (`src/core/`)

**Domain layer containing business logic foundations**

- `types/` - TypeScript type definitions
  - Event, Agent, ApiResponse interfaces
  - Request/Response types
- `enums/` - Enumerations
  - EventSeverity, AgentStatus, etc.
- `constants.ts` - Application constants
  - API endpoints, pagination defaults, etc.

### Infrastructure Layer (`src/api/`)

**External dependencies and HTTP communication**

- `client.ts` - Axios HTTP client with interceptors
  - Request/response interceptors
  - Error handling
  - Authentication token injection
- Service modules for API communication
  - `events.ts` - Events API service
  - `agents.ts` - Agents API service

### Application Layer

**Business logic and state management**

- `store/` - Pinia stores for global state
  - `modules/auth.store.ts` - Authentication state
  - `modules/events.store.ts` - Events state
  - `modules/agents.store.ts` - Agents state
- `composables/` - Reusable composition functions
  - `useEvents.ts` - Event management logic
  - `useAgents.ts` - Agent management logic
  - `usePagination.ts` - Pagination logic
- `utils/` - Utility functions
  - Date formatting, string manipulation, etc.

### Presentation Layer

**UI components and pages**

- `components/` - Reusable UI components
  - `common/` - Generic components (Button, Card, Modal, etc.)
  - `events/` - Event-specific components
  - `agents/` - Agent-specific components
- `pages/` - Route entry points
  - `Dashboard.vue`
  - `Events/EventsListPage.vue`
  - `Agents/AgentsListPage.vue`
- `router/` - Routing configuration
  - `index.ts` - Router setup
  - `routes/` - Route definitions and guards
- `styles/` - Global styles
  - `main.css` - Tailwind imports
  - `variables.css` - CSS custom properties
  - `utilities.css` - Custom utility classes

## Commands

### Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Testing

```bash
# Run tests
npm run test

# Run tests with UI
npm run test:ui

# Generate coverage report
npm run test:coverage
```

### Code Quality

```bash
# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Format code with Prettier
npm run format

# Check TypeScript types
npm run type-check
```

## Best Practices

### Component Structure

```vue
<script setup lang="ts">
// ✅ PREFERRED: Composition API with script setup
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
const error = ref<string | null>(null)

// Computed properties
const formattedDate = computed(() => {
  if (!event.value) return ''
  return new Date(event.value.publishedAt).toLocaleDateString()
})

const isHighSeverity = computed(() => {
  return event.value?.severity === 'HIGH' || event.value?.severity === 'CRITICAL'
})

// Methods
async function fetchEvent() {
  loading.value = true
  error.value = null

  try {
    event.value = await eventsApi.getById(props.eventId)
  } catch (err) {
    error.value = 'Failed to fetch event'
    console.error('Failed to fetch event:', err)
  } finally {
    loading.value = false
  }
}

function handleDelete() {
  emit('delete', props.eventId)
}

// Lifecycle hooks
onMounted(() => {
  fetchEvent()
})
</script>

<template>
  <div class="event-card">
    <!-- Loading state -->
    <div v-if="loading" class="loading">
      Loading...
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <!-- Content -->
    <div v-else-if="event" class="content">
      <h2 class="title">{{ event.detailType }}</h2>
      <p class="date">{{ formattedDate }}</p>

      <div v-if="showDetails" class="details">
        <!-- Details content -->
      </div>

      <button
        v-if="isHighSeverity"
        @click="handleDelete"
        class="delete-btn"
      >
        Delete
      </button>
    </div>
  </div>
</template>

<style scoped>
.event-card {
  @apply rounded-lg border border-gray-200 p-4 shadow-sm;
}

.title {
  @apply text-xl font-semibold text-gray-900;
}

.date {
  @apply text-sm text-gray-500;
}

.delete-btn {
  @apply mt-4 rounded bg-red-600 px-4 py-2 text-white hover:bg-red-700;
}
</style>
```

### Type Safety

```typescript
// ✅ Define explicit types
// src/core/types/event.ts
export interface Event {
  id: string
  account: string
  region?: string
  detail: Record<string, unknown>
  detailType: string
  severity: EventSeverity
  publishedAt: number
}

export enum EventSeverity {
  Low = 'LOW',
  Medium = 'MEDIUM',
  High = 'HIGH',
  Critical = 'CRITICAL'
}

// ✅ Use type guards
export function isEvent(obj: unknown): obj is Event {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'account' in obj &&
    'detailType' in obj
  )
}

// ✅ Generic API response
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

// ✅ Pagination types
export interface PaginationParams {
  page: number
  limit: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  hasNext: boolean
  hasPrev: boolean
}
```

### State Management with Pinia

```typescript
// stores/modules/events.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Event, PaginationParams } from '@/core/types'
import { eventsApi } from '@/api/events'

export const useEventsStore = defineStore('events', () => {
  // State
  const events = ref<Event[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const currentPage = ref(1)
  const totalItems = ref(0)
  const itemsPerPage = ref(10)

  // Getters
  const criticalEvents = computed(() =>
    events.value.filter(e => e.severity === 'CRITICAL')
  )

  const highSeverityEvents = computed(() =>
    events.value.filter(e =>
      e.severity === 'HIGH' || e.severity === 'CRITICAL'
    )
  )

  const totalPages = computed(() =>
    Math.ceil(totalItems.value / itemsPerPage.value)
  )

  // Actions
  async function fetchEvents(params?: PaginationParams) {
    loading.value = true
    error.value = null

    try {
      const response = await eventsApi.list({
        page: params?.page || currentPage.value,
        limit: params?.limit || itemsPerPage.value,
        ...params
      })

      events.value = response.items
      totalItems.value = response.total
      currentPage.value = response.page
    } catch (err) {
      error.value = 'Failed to fetch events'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  async function fetchEventById(id: string) {
    loading.value = true
    error.value = null

    try {
      const event = await eventsApi.getById(id)
      return event
    } catch (err) {
      error.value = `Failed to fetch event ${id}`
      console.error(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  function reset() {
    events.value = []
    loading.value = false
    error.value = null
    currentPage.value = 1
    totalItems.value = 0
  }

  return {
    // State
    events,
    loading,
    error,
    currentPage,
    totalItems,
    itemsPerPage,
    // Getters
    criticalEvents,
    highSeverityEvents,
    totalPages,
    // Actions
    fetchEvents,
    fetchEventById,
    reset
  }
})
```

### Composables Pattern

```typescript
// composables/useEvents.ts
import { ref, computed, onMounted } from 'vue'
import type { Event, PaginationParams } from '@/core/types'
import { eventsApi } from '@/api/events'

export function useEvents(params?: PaginationParams) {
  const events = ref<Event[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const currentPage = ref(params?.page || 1)
  const totalItems = ref(0)

  const hasNextPage = computed(() => {
    return currentPage.value * (params?.limit || 10) < totalItems.value
  })

  const hasPrevPage = computed(() => {
    return currentPage.value > 1
  })

  async function fetchEvents() {
    loading.value = true
    error.value = null

    try {
      const response = await eventsApi.list({
        page: currentPage.value,
        limit: params?.limit || 10,
        ...params
      })

      events.value = response.items
      totalItems.value = response.total
    } catch (err) {
      error.value = err as Error
      console.error('Failed to fetch events:', err)
    } finally {
      loading.value = false
    }
  }

  function nextPage() {
    if (hasNextPage.value) {
      currentPage.value++
      fetchEvents()
    }
  }

  function prevPage() {
    if (hasPrevPage.value) {
      currentPage.value--
      fetchEvents()
    }
  }

  function goToPage(page: number) {
    currentPage.value = page
    fetchEvents()
  }

  onMounted(() => {
    fetchEvents()
  })

  return {
    events,
    loading,
    error,
    currentPage,
    totalItems,
    hasNextPage,
    hasPrevPage,
    fetchEvents,
    nextPage,
    prevPage,
    goToPage
  }
}
```

### API Client Pattern

```typescript
// api/client.ts
import axios, { type AxiosInstance, type AxiosError } from 'axios'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Add request ID for tracing
    config.headers['X-Request-ID'] = crypto.randomUUID()

    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Return data directly
    return response.data
  },
  (error: AxiosError) => {
    // Handle errors globally
    if (error.response) {
      // Server responded with error status
      const status = error.response.status

      if (status === 401) {
        // Unauthorized - redirect to login
        localStorage.removeItem('auth_token')
        window.location.href = '/login'
      } else if (status === 403) {
        // Forbidden
        console.error('Access forbidden')
      } else if (status >= 500) {
        // Server error
        console.error('Server error:', error.response.data)
      }
    } else if (error.request) {
      // Request made but no response
      console.error('Network error:', error.message)
    }

    return Promise.reject(error)
  }
)

export default apiClient
```

```typescript
// api/events.ts
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
  },

  async update(id: string, event: Partial<Event>): Promise<Event> {
    return apiClient.put(`/events/${id}`, event)
  },

  async delete(id: string): Promise<void> {
    return apiClient.delete(`/events/${id}`)
  }
}
```

## Testing

### Component Testing

```typescript
// __tests__/components/EventCard.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, type VueWrapper } from '@vue/test-utils'
import EventCard from '@/components/events/EventCard.vue'
import type { Event } from '@/core/types'
import { EventSeverity } from '@/core/enums'

describe('EventCard', () => {
  let wrapper: VueWrapper
  const mockEvent: Event = {
    id: '123',
    account: '000000000000',
    detailType: 'CloudWatch Alarm',
    severity: EventSeverity.High,
    publishedAt: Date.now(),
    detail: { AlarmName: 'TestAlarm' }
  }

  beforeEach(() => {
    wrapper = mount(EventCard, {
      props: { event: mockEvent }
    })
  })

  it('renders event details correctly', () => {
    expect(wrapper.text()).toContain('CloudWatch Alarm')
    expect(wrapper.find('.severity-badge').classes()).toContain('severity-high')
  })

  it('emits delete event when delete button clicked', async () => {
    await wrapper.find('.delete-btn').trigger('click')

    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')?.[0]).toEqual([mockEvent.id])
  })

  it('shows details when showDetails prop is true', async () => {
    await wrapper.setProps({ showDetails: true })

    expect(wrapper.find('.details').exists()).toBe(true)
  })

  it('formats date correctly', () => {
    const dateText = wrapper.find('.date').text()
    expect(dateText).toBeTruthy()
    expect(dateText).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/)
  })
})
```

### Store Testing

```typescript
// __tests__/stores/events.store.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useEventsStore } from '@/store/modules/events.store'
import { eventsApi } from '@/api/events'

// Mock the API
vi.mock('@/api/events', () => ({
  eventsApi: {
    list: vi.fn(),
    getById: vi.fn()
  }
}))

describe('Events Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetches events successfully', async () => {
    const mockResponse = {
      items: [{ id: '1', detailType: 'Test' }],
      total: 1,
      page: 1,
      limit: 10
    }

    vi.mocked(eventsApi.list).mockResolvedValue(mockResponse)

    const store = useEventsStore()
    await store.fetchEvents()

    expect(store.events).toEqual(mockResponse.items)
    expect(store.totalItems).toBe(1)
    expect(store.loading).toBe(false)
    expect(store.error).toBe(null)
  })

  it('handles fetch errors', async () => {
    vi.mocked(eventsApi.list).mockRejectedValue(new Error('Network error'))

    const store = useEventsStore()
    await store.fetchEvents()

    expect(store.events).toEqual([])
    expect(store.error).toBeTruthy()
    expect(store.loading).toBe(false)
  })

  it('filters critical events correctly', () => {
    const store = useEventsStore()
    store.events = [
      { id: '1', severity: 'CRITICAL' },
      { id: '2', severity: 'HIGH' },
      { id: '3', severity: 'CRITICAL' }
    ]

    expect(store.criticalEvents).toHaveLength(2)
    expect(store.criticalEvents.every(e => e.severity === 'CRITICAL')).toBe(true)
  })
})
```

### Coverage Expectations

- **Minimum**: 80% overall coverage
- **Target**: >90% for critical components
- **100%**: Utility functions, stores, and composables

## Common Development Tasks

### Adding a New Page

1. **Create page component** in `src/pages/`
   ```vue
   <!-- src/pages/NewFeature/NewFeaturePage.vue -->
   <script setup lang="ts">
   import { ref, onMounted } from 'vue'

   const data = ref([])

   onMounted(async () => {
     // Fetch data
   })
   </script>

   <template>
     <div class="new-feature-page">
       <h1>New Feature</h1>
       <!-- Content -->
     </div>
   </template>
   ```

2. **Add route** in `src/router/routes/index.ts`
   ```typescript
   {
     path: '/new-feature',
     name: 'NewFeature',
     component: () => import('@/pages/NewFeature/NewFeaturePage.vue'),
     meta: { requiresAuth: true }
   }
   ```

3. **Create API service** in `src/api/`
4. **Add Pinia store** if needed in `src/store/modules/`
5. **Write tests** in `src/__tests__/`

### Adding a New Component

1. **Create component** in `src/components/`
2. **Define TypeScript interfaces/props**
3. **Follow composition API with `<script setup>`**
4. **Use Tailwind CSS for styling**
5. **Write component tests**
6. **Export from index file** (if using barrel exports)

### Adding API Integration

1. **Define types** in `src/core/types/`
2. **Create API service** in `src/api/`
3. **Update Axios client** if needed
4. **Create composable** in `src/composables/`
5. **Update store** if needed
6. **Add tests** for API service and composable

## Security Guidelines

- ✅ No sensitive data in localStorage (use secure HTTP-only cookies)
- ✅ Sanitize user input to prevent XSS
- ✅ Use environment variables for API endpoints
- ✅ Implement CSRF protection
- ✅ Content Security Policy headers
- ✅ API key/token rotation strategy
- ✅ Validate all user inputs
- ✅ Use HTTPS in production

## Performance Considerations

- **Code splitting**: Use dynamic imports for routes
- **Lazy loading**: Load components on-demand
- **Virtual scrolling**: For large lists (use libraries like vue-virtual-scroller)
- **Debounce**: Debounce search inputs and API calls
- **Caching**: Cache API responses when appropriate
- **Bundle optimization**: Tree-shaking and minification
- **Image optimization**: Use modern formats (WebP, AVIF)
- **Component memoization**: Use `computed` and `memo` appropriately

## Troubleshooting

### Dependency Conflicts
```bash
# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Type Errors
```bash
# Run type check to see all issues
npm run type-check

# Common issues:
# - Missing type definitions: npm install -D @types/package-name
# - Incorrect imports: Check import paths
# - Missing generics: Add type parameters
```

### Build Failures
```bash
# Check for missing environment variables
cat .env.development

# Verify all imports exist
npm run type-check

# Clear Vite cache
rm -rf node_modules/.vite
```

### API Connection Issues
```bash
# Verify backend is running
curl http://localhost:3001/api/health

# Check environment variable
echo $VITE_API_BASE_URL

# Check network tab in browser DevTools
```

## Environment Setup

### Required Environment Variables

Located in `frontend/.env.development`:
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:3001/api

# Application
VITE_APP_NAME=AWS Monitoring
VITE_APP_VERSION=1.0.0

# Feature Flags
VITE_ENABLE_DEBUG=true
```

Located in `frontend/.env.production`:
```bash
# API Configuration
VITE_API_BASE_URL=https://api.production.com

# Application
VITE_APP_NAME=AWS Monitoring
VITE_APP_VERSION=1.0.0

# Feature Flags
VITE_ENABLE_DEBUG=false
```

### Node.js Version

Ensure Node.js >= 18 is installed:
```bash
node --version
# v18.x or higher

# Using nvm
nvm install 18
nvm use 18
```

## Additional Resources

- Main documentation: `../docs/`
- Frontend overview: `../docs/frontend-overview.md`
- Quick start: `../docs/frontend-quick-start.md`
- Design documentation: `../docs/frontend-design.md`
- Implementation guide: `../docs/frontend-implementation-guide.md`
- Types reference: `../docs/frontend-types-reference.md`
- API specification: `../docs/api-specification.yaml`

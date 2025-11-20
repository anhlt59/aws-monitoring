# Frontend Development Guide

This guide provides instructions for developing the AWS Monitoring CMS frontend application.

## Overview

The frontend is a Vue 3 + TypeScript application following a clean layered architecture with:
- **Domain Layer**: Types, enums, constants (framework-agnostic)
- **Infrastructure Layer**: API services, HTTP client
- **Application Layer**: Composables, business logic
- **Presentation Layer**: Vue components, pages

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test
```

## Architecture

### Directory Structure

```
src/
├── core/              # Domain layer (types, enums, constants)
│   ├── types/         # TypeScript interfaces
│   ├── enums/         # Enums and their labels
│   └── constants/     # App constants
├── api/               # Infrastructure layer
│   ├── client.ts      # Axios instance with interceptors
│   └── modules/       # API service modules
├── composables/       # Application layer
│   ├── features/      # Feature composables (useAuth, useEvents, etc.)
│   └── utils/         # Utility composables
├── components/        # Presentation layer
│   ├── base/          # Reusable UI components
│   ├── modules/       # Feature-specific components
│   └── layout/        # Layout components
├── pages/             # Route entry points
├── router/            # Vue Router configuration
└── styles/            # Global styles
```

### Key Patterns

#### 1. Composables for Business Logic

Composables encapsulate business logic and API calls:

```typescript
// composables/features/useEvents.ts
export function useEvents() {
  const events = ref<Event[]>([])
  const isLoading = ref(false)
  const error = ref<ApiError | null>(null)

  const fetchEvents = async () => {
    isLoading.value = true
    try {
      const response = await eventsApi.getEvents()
      events.value = response.items
    } catch (err) {
      error.value = err as ApiError
    } finally {
      isLoading.value = false
    }
  }

  return { events, isLoading, error, fetchEvents }
}
```

#### 2. API Services

API services handle HTTP requests:

```typescript
// api/modules/events.api.ts
export const eventsApi = {
  async getEvents(filters: EventFilters): Promise<PaginatedResponse<Event>> {
    const response = await apiClient.get<PaginatedResponse<Event>>('/api/events', {
      params: filters
    })
    return response.data
  }
}
```

#### 3. Component Composition

Components use composables and focus on presentation:

```vue
<script setup lang="ts">
import { onMounted } from 'vue'
import { useEvents } from '@/composables/features'

const { events, isLoading, fetchEvents } = useEvents()

onMounted(() => {
  fetchEvents()
})
</script>

<template>
  <div v-if="isLoading">Loading...</div>
  <div v-else>
    <div v-for="event in events" :key="event.id">
      {{ event.detail_type }}
    </div>
  </div>
</template>
```

## Development Workflow

### Adding a New Feature

Follow this sequence:

1. **Define Types** → `core/types/your-feature.ts`
2. **Create API Service** → `api/modules/your-feature.api.ts`
3. **Build Composable** → `composables/features/useYourFeature.ts`
4. **Create Base Components** (if needed) → `components/base/`
5. **Build Module Components** → `components/modules/`
6. **Create Page** → `pages/YourFeaturePage.vue`
7. **Add Route** → `router/index.ts`

### Example: Adding Event Filters

**1. Update types:**
```typescript
// core/types/event.ts
export interface EventFilters {
  severity?: Severity[]
  start_date?: number
  end_date?: number
}
```

**2. Update API service:**
```typescript
// api/modules/events.api.ts
async getEvents(filters: EventFilters): Promise<PaginatedResponse<Event>> {
  return await apiClient.get('/api/events', { params: filters })
}
```

**3. Update composable:**
```typescript
// composables/features/useEvents.ts
const setFilters = (newFilters: Partial<EventFilters>) => {
  filters.value = { ...filters.value, ...newFilters }
  fetchEvents()
}

return { /* ... */, setFilters }
```

**4. Create filter component:**
```vue
<!-- components/modules/EventFilters.vue -->
<script setup lang="ts">
const emit = defineEmits<{ (e: 'change', filters: EventFilters): void }>()
// Filter UI logic
</script>
```

**5. Use in page:**
```vue
<!-- pages/EventsPage.vue -->
<EventFilters @change="setFilters" />
```

## Code Style Guidelines

### TypeScript

- Use strict TypeScript
- Define interfaces for all data structures
- Avoid `any` type
- Use type inference where appropriate

```typescript
// Good
interface User {
  id: string
  name: string
}

const users = ref<User[]>([])

// Bad
const users = ref<any>([])
```

### Vue Components

- Use `<script setup>` syntax
- Define props and emits with TypeScript
- Use composition API
- Keep components focused and small

```vue
<script setup lang="ts">
interface Props {
  title: string
  count?: number
}

interface Emits {
  (e: 'update', value: number): void
}

const props = withDefaults(defineProps<Props>(), {
  count: 0
})

const emit = defineEmits<Emits>()
</script>
```

### Styling

- Use Tailwind CSS utility classes
- Avoid custom CSS when possible
- Use `@apply` for repeated patterns
- Keep styling in components

```vue
<template>
  <button class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700">
    Click me
  </button>
</template>
```

## Testing

### Unit Tests

Test composables and utility functions:

```typescript
import { describe, it, expect, vi } from 'vitest'
import { useEvents } from '@/composables/features/useEvents'

describe('useEvents', () => {
  it('should fetch events', async () => {
    const { events, fetchEvents } = useEvents()
    await fetchEvents()
    expect(events.value).toBeDefined()
  })
})
```

### Component Tests

Test component behavior:

```typescript
import { mount } from '@vue/test-utils'
import EventList from '@/components/modules/EventList.vue'

describe('EventList', () => {
  it('should render events', () => {
    const wrapper = mount(EventList, {
      props: { events: mockEvents }
    })
    expect(wrapper.text()).toContain('Event 1')
  })
})
```

## Common Tasks

### Adding a New Page

1. Create page component in `pages/`
2. Add route in `router/index.ts`
3. Add navigation link in `AppLayout.vue`

### Adding a New API Endpoint

1. Define request/response types in `core/types/`
2. Add method to API service in `api/modules/`
3. Use in composable

### Creating a Reusable Component

1. Create in `components/base/`
2. Use generic types for flexibility
3. Document props and emits
4. Add to component library

## Troubleshooting

### Type Errors

Run type check:
```bash
npm run type-check
```

Common issues:
- Missing type definitions
- Incorrect generic types
- Type inference failures

### API Connection Issues

Check:
- Backend is running
- API base URL is correct
- CORS is configured
- Authentication token is valid

### Build Failures

Common causes:
- Missing dependencies
- Type errors
- Environment variables not set

## Performance Optimization

### Code Splitting

Use dynamic imports for routes:
```typescript
{
  path: '/events',
  component: () => import('@/pages/EventsPage.vue')
}
```

### Lazy Loading Components

```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

const HeavyComponent = defineAsyncComponent(() =>
  import('./HeavyComponent.vue')
)
</script>
```

### Computed Properties

Use computed for derived state:
```typescript
const criticalEvents = computed(() =>
  events.value.filter(e => e.severity === Severity.Critical)
)
```

## Best Practices

1. **Keep components small** - Max 200 lines
2. **Use composables** - Extract logic from components
3. **Type everything** - Use TypeScript properly
4. **Avoid prop drilling** - Use provide/inject for deep data
5. **Handle errors** - Always catch and display errors
6. **Loading states** - Show feedback during async operations
7. **Accessibility** - Use semantic HTML and ARIA labels
8. **Mobile-first** - Design for mobile, enhance for desktop

## Resources

- [Vue 3 Documentation](https://vuejs.org/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Vue Router Documentation](https://router.vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)

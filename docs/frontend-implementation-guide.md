# Frontend Implementation Guide

This guide provides practical examples of implementing features in the frontend architecture, showing how different layers work together.

## Feature Implementation Flow

When implementing a new feature, follow this sequence:

1. **Define Types** → `core/types/`
2. **Create API Service** → `api/modules/`
3. **Build Composable** → `composables/features/`
4. **Create Base Components** (if needed) → `components/base/`
5. **Build Module Components** → `components/modules/`
6. **Create Page** → `pages/`
7. **Add Route** → `router/routes/`

## Example: Events Listing Feature

### Step 1: Define Types

```typescript
// core/types/event.ts
export interface Event {
  id: string;
  account: string;
  region: string;
  source: string;
  severity: Severity;
  detail_type: string;
  published_at: number;
  // ... other fields
}

export interface EventFilters {
  account?: string;
  region?: string;
  severity?: Severity[];
  start_date?: number;
  end_date?: number;
  page?: number;
  page_size?: number;
}
```

### Step 2: Create API Service

```typescript
// api/modules/events.api.ts
import { apiClient } from '../client';
import type { Event, EventFilters, PaginatedResponse } from '@/core/types';

export const eventsApi = {
  /**
   * Fetch paginated events with filters
   */
  async getEvents(filters: EventFilters): Promise<PaginatedResponse<Event>> {
    const response = await apiClient.get<PaginatedResponse<Event>>('/events', {
      params: filters
    });
    return response.data;
  },

  /**
   * Fetch single event by ID
   */
  async getEventById(id: string): Promise<Event> {
    const response = await apiClient.get<Event>(`/events/${id}`);
    return response.data;
  },

  /**
   * Delete event
   */
  async deleteEvent(id: string): Promise<void> {
    await apiClient.delete(`/events/${id}`);
  }
};
```

### Step 3: Build Composable

```typescript
// composables/features/useEvents.ts
import { ref, computed, watch } from 'vue';
import { eventsApi } from '@/api/modules/events.api';
import type { Event, EventFilters, ApiError, Severity } from '@/core/types';

export function useEvents() {
  // State
  const events = ref<Event[]>([]);
  const isLoading = ref(false);
  const error = ref<ApiError | null>(null);
  const totalEvents = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(20);

  // Filters
  const filters = ref<EventFilters>({
    page: 1,
    page_size: 20
  });

  // Computed
  const hasMore = computed(() => {
    return events.value.length < totalEvents.value;
  });

  const criticalEvents = computed(() =>
    events.value.filter(e => e.severity === Severity.Critical)
  );

  const hasEvents = computed(() => events.value.length > 0);

  // Methods
  const fetchEvents = async () => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await eventsApi.getEvents(filters.value);
      events.value = response.items;
      totalEvents.value = response.total;
      currentPage.value = response.page;
    } catch (err) {
      error.value = err as ApiError;
      events.value = [];
    } finally {
      isLoading.value = false;
    }
  };

  const refreshEvents = async () => {
    await fetchEvents();
  };

  const setFilters = (newFilters: Partial<EventFilters>) => {
    filters.value = { ...filters.value, ...newFilters, page: 1 };
    fetchEvents();
  };

  const nextPage = () => {
    if (hasMore.value) {
      filters.value.page = (filters.value.page || 1) + 1;
      fetchEvents();
    }
  };

  const previousPage = () => {
    if ((filters.value.page || 1) > 1) {
      filters.value.page = (filters.value.page || 1) - 1;
      fetchEvents();
    }
  };

  const clearFilters = () => {
    filters.value = { page: 1, page_size: 20 };
    fetchEvents();
  };

  // Auto-refresh every 30 seconds
  const startAutoRefresh = () => {
    return setInterval(refreshEvents, 30000);
  };

  const stopAutoRefresh = (intervalId: number) => {
    clearInterval(intervalId);
  };

  // Public interface
  return {
    // State
    events,
    isLoading,
    error,
    filters,
    totalEvents,
    currentPage,
    pageSize,

    // Computed
    hasMore,
    criticalEvents,
    hasEvents,

    // Methods
    fetchEvents,
    refreshEvents,
    setFilters,
    nextPage,
    previousPage,
    clearFilters,
    startAutoRefresh,
    stopAutoRefresh
  };
}
```

### Step 4: Create Base Components

```vue
<!-- components/base/data-display/Table.vue -->
<script setup lang="ts" generic="T">
interface Column {
  key: string;
  label: string;
  sortable?: boolean;
  width?: string;
}

interface Props {
  columns: Column[];
  data: T[];
  isLoading?: boolean;
  emptyMessage?: string;
}

interface Emits {
  (e: 'row-click', row: T): void;
  (e: 'sort', column: string): void;
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  emptyMessage: 'No data available'
});

const emit = defineEmits<Emits>();

const handleRowClick = (row: T) => {
  emit('row-click', row);
};

const handleSort = (column: Column) => {
  if (column.sortable) {
    emit('sort', column.key);
  }
};
</script>

<template>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            :class="[
              'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
              column.sortable ? 'cursor-pointer hover:bg-gray-100' : ''
            ]"
            :style="{ width: column.width }"
            @click="handleSort(column)"
          >
            {{ column.label }}
          </th>
        </tr>
      </thead>

      <tbody class="bg-white divide-y divide-gray-200">
        <!-- Loading state -->
        <tr v-if="isLoading">
          <td :colspan="columns.length" class="px-6 py-4 text-center">
            <Spinner />
          </td>
        </tr>

        <!-- Empty state -->
        <tr v-else-if="data.length === 0">
          <td :colspan="columns.length" class="px-6 py-4 text-center text-gray-500">
            {{ emptyMessage }}
          </td>
        </tr>

        <!-- Data rows -->
        <tr
          v-else
          v-for="(row, index) in data"
          :key="index"
          class="hover:bg-gray-50 cursor-pointer"
          @click="handleRowClick(row)"
        >
          <td
            v-for="column in columns"
            :key="column.key"
            class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
          >
            <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
              {{ row[column.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
```

```vue
<!-- components/base/feedback/Badge.vue -->
<script setup lang="ts">
type BadgeVariant = 'success' | 'error' | 'warning' | 'info' | 'neutral';
type BadgeSize = 'sm' | 'md' | 'lg';

interface Props {
  variant?: BadgeVariant;
  size?: BadgeSize;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'neutral',
  size: 'md'
});

const variantClasses = {
  success: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800',
  warning: 'bg-yellow-100 text-yellow-800',
  info: 'bg-blue-100 text-blue-800',
  neutral: 'bg-gray-100 text-gray-800'
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base'
};
</script>

<template>
  <span
    :class="[
      'inline-flex items-center font-medium rounded-full',
      variantClasses[variant],
      sizeClasses[size]
    ]"
  >
    <slot />
  </span>
</template>
```

### Step 5: Build Module Components

```vue
<!-- components/modules/events/EventList.vue -->
<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useEvents } from '@/composables/features/useEvents';
import Table from '@/components/base/data-display/Table.vue';
import Badge from '@/components/base/feedback/Badge.vue';
import EventFilters from './EventFilters.vue';
import SeverityIndicator from './SeverityIndicator.vue';
import type { Event } from '@/core/types';

const router = useRouter();
const {
  events,
  isLoading,
  error,
  fetchEvents,
  setFilters,
  nextPage,
  previousPage,
  hasMore,
  currentPage,
  totalEvents,
  startAutoRefresh,
  stopAutoRefresh
} = useEvents();

// Auto-refresh
let refreshInterval: number | null = null;

onMounted(async () => {
  await fetchEvents();
  refreshInterval = startAutoRefresh();
});

onUnmounted(() => {
  if (refreshInterval) {
    stopAutoRefresh(refreshInterval);
  }
});

// Table configuration
const columns = [
  { key: 'severity', label: 'Severity', width: '120px' },
  { key: 'account', label: 'Account', width: '150px' },
  { key: 'region', label: 'Region', width: '120px' },
  { key: 'detail_type', label: 'Type', sortable: true },
  { key: 'source', label: 'Source', sortable: true },
  { key: 'published_at', label: 'Time', width: '180px', sortable: true }
];

// Event handlers
const handleRowClick = (event: Event) => {
  router.push({ name: 'EventDetail', params: { id: event.id } });
};

const handleFiltersChange = (newFilters: any) => {
  setFilters(newFilters);
};

// Format timestamp
const formatTimestamp = (timestamp: number) => {
  return new Date(timestamp * 1000).toLocaleString();
};
</script>

<template>
  <div class="space-y-4">
    <!-- Filters -->
    <EventFilters @change="handleFiltersChange" />

    <!-- Error state -->
    <Alert v-if="error" variant="error">
      {{ error.message }}
    </Alert>

    <!-- Table -->
    <Card>
      <Table
        :columns="columns"
        :data="events"
        :is-loading="isLoading"
        empty-message="No events found"
        @row-click="handleRowClick"
      >
        <!-- Custom cell: Severity -->
        <template #cell-severity="{ row }">
          <SeverityIndicator :severity="row.severity" />
        </template>

        <!-- Custom cell: Account -->
        <template #cell-account="{ value }">
          <Badge variant="neutral">{{ value }}</Badge>
        </template>

        <!-- Custom cell: Published At -->
        <template #cell-published_at="{ value }">
          {{ formatTimestamp(value) }}
        </template>
      </Table>

      <!-- Pagination -->
      <div class="flex items-center justify-between px-6 py-4 border-t">
        <div class="text-sm text-gray-700">
          Showing {{ events.length }} of {{ totalEvents }} events
        </div>
        <div class="flex gap-2">
          <BaseButton
            :disabled="currentPage === 1"
            @click="previousPage"
          >
            Previous
          </BaseButton>
          <BaseButton
            :disabled="!hasMore"
            @click="nextPage"
          >
            Next
          </BaseButton>
        </div>
      </div>
    </Card>
  </div>
</template>
```

```vue
<!-- components/modules/events/EventFilters.vue -->
<script setup lang="ts">
import { ref } from 'vue';
import { Severity } from '@/core/types';
import BaseSelect from '@/components/base/inputs/BaseSelect.vue';
import DateRangePicker from '@/components/base/inputs/DateRangePicker.vue';
import BaseButton from '@/components/base/buttons/BaseButton.vue';

interface Emits {
  (e: 'change', filters: any): void;
}

const emit = defineEmits<Emits>();

// Filter state
const selectedAccount = ref<string>('');
const selectedRegion = ref<string>('');
const selectedSeverity = ref<Severity[]>([]);
const dateRange = ref<{ start: number; end: number } | null>(null);

// Options
const accountOptions = ref([
  { value: '', label: 'All Accounts' },
  { value: '123456789012', label: '123456789012' },
  // ... populated from API
]);

const regionOptions = ref([
  { value: '', label: 'All Regions' },
  { value: 'us-east-1', label: 'US East 1' },
  { value: 'us-west-2', label: 'US West 2' }
]);

const severityOptions = [
  { value: Severity.Critical, label: 'Critical' },
  { value: Severity.High, label: 'High' },
  { value: Severity.Medium, label: 'Medium' },
  { value: Severity.Low, label: 'Low' }
];

// Methods
const applyFilters = () => {
  emit('change', {
    account: selectedAccount.value || undefined,
    region: selectedRegion.value || undefined,
    severity: selectedSeverity.value.length > 0 ? selectedSeverity.value : undefined,
    start_date: dateRange.value?.start,
    end_date: dateRange.value?.end
  });
};

const resetFilters = () => {
  selectedAccount.value = '';
  selectedRegion.value = '';
  selectedSeverity.value = [];
  dateRange.value = null;
  emit('change', {});
};
</script>

<template>
  <Card class="p-4">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Account filter -->
      <BaseSelect
        v-model="selectedAccount"
        :options="accountOptions"
        label="Account"
      />

      <!-- Region filter -->
      <BaseSelect
        v-model="selectedRegion"
        :options="regionOptions"
        label="Region"
      />

      <!-- Severity filter -->
      <BaseSelect
        v-model="selectedSeverity"
        :options="severityOptions"
        label="Severity"
        multiple
      />

      <!-- Date range filter -->
      <DateRangePicker
        v-model="dateRange"
        label="Date Range"
      />
    </div>

    <!-- Actions -->
    <div class="flex gap-2 mt-4">
      <BaseButton variant="primary" @click="applyFilters">
        Apply Filters
      </BaseButton>
      <BaseButton variant="secondary" @click="resetFilters">
        Reset
      </BaseButton>
    </div>
  </Card>
</template>
```

```vue
<!-- components/modules/events/SeverityIndicator.vue -->
<script setup lang="ts">
import { computed } from 'vue';
import { Severity } from '@/core/types';
import Badge from '@/components/base/feedback/Badge.vue';

interface Props {
  severity: Severity;
}

const props = defineProps<Props>();

const severityConfig = {
  [Severity.Critical]: {
    label: 'Critical',
    variant: 'error' as const,
    icon: '🔴'
  },
  [Severity.High]: {
    label: 'High',
    variant: 'warning' as const,
    icon: '🟠'
  },
  [Severity.Medium]: {
    label: 'Medium',
    variant: 'info' as const,
    icon: '🔵'
  },
  [Severity.Low]: {
    label: 'Low',
    variant: 'success' as const,
    icon: '🟢'
  },
  [Severity.Unknown]: {
    label: 'Unknown',
    variant: 'neutral' as const,
    icon: '⚪'
  }
};

const config = computed(() => severityConfig[props.severity]);
</script>

<template>
  <Badge :variant="config.variant">
    <span class="mr-1">{{ config.icon }}</span>
    {{ config.label }}
  </Badge>
</template>
```

### Step 6: Create Page

```vue
<!-- pages/Events/EventsListPage.vue -->
<script setup lang="ts">
import { useMeta } from '@/composables/ui/useMeta';
import EventList from '@/components/modules/events/EventList.vue';
import Container from '@/components/base/layout/Container.vue';

// Set page metadata
useMeta({
  title: 'Events - AWS Monitoring',
  description: 'View and filter monitoring events'
});
</script>

<template>
  <Container>
    <div class="py-6">
      <!-- Page header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">
          Monitoring Events
        </h1>
        <p class="mt-2 text-sm text-gray-600">
          View and filter events from all monitored accounts
        </p>
      </div>

      <!-- Event list -->
      <EventList />
    </div>
  </Container>
</template>
```

### Step 7: Add Route

```typescript
// router/routes/index.ts
import type { RouteRecordRaw } from 'vue-router';

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/pages/Dashboard.vue'),
    name: 'Dashboard',
    meta: {
      requiresAuth: true,
      title: 'Dashboard'
    }
  },
  {
    path: '/events',
    name: 'Events',
    children: [
      {
        path: '',
        name: 'EventsList',
        component: () => import('@/pages/Events/EventsListPage.vue'),
        meta: {
          requiresAuth: true,
          title: 'Events'
        }
      },
      {
        path: ':id',
        name: 'EventDetail',
        component: () => import('@/pages/Events/EventDetailPage.vue'),
        meta: {
          requiresAuth: true,
          title: 'Event Details'
        }
      }
    ]
  }
  // ... more routes
];
```

## Data Flow Example

### Scenario: User Filters Events by Severity

1. **User Action**: User selects "Critical" severity in `EventFilters.vue`
2. **Component**: `EventFilters.vue` emits change event with new filters
3. **Parent Component**: `EventList.vue` receives event and calls `setFilters()`
4. **Composable**: `useEvents.setFilters()` updates filter state and calls `fetchEvents()`
5. **API Service**: `eventsApi.getEvents()` makes HTTP request with filters
6. **HTTP Client**: Axios sends GET request to backend API
7. **Backend**: API Gateway → Lambda → DynamoDB query
8. **Response**: Data flows back through same layers
9. **State Update**: Composable updates `events` ref
10. **UI Update**: Vue's reactivity triggers re-render of `EventList.vue`

### State Update Flow

```
User Interaction
    ↓
EventFilters.vue (emit 'change')
    ↓
EventList.vue (receive event)
    ↓
useEvents.setFilters() (composable)
    ↓
eventsApi.getEvents() (API service)
    ↓
axios.get() (HTTP client)
    ↓
[Network Request to Backend]
    ↓
[Response from Backend]
    ↓
Transform response to Event[]
    ↓
Update events ref (reactive state)
    ↓
Vue re-renders EventList.vue
    ↓
Table.vue updates with new data
```

## Advanced Patterns

### Pattern 1: Optimistic Updates

```typescript
// composables/features/useEvents.ts
const deleteEvent = async (id: string) => {
  // Optimistic update
  const originalEvents = [...events.value];
  events.value = events.value.filter(e => e.id !== id);

  try {
    await eventsApi.deleteEvent(id);
    // Success - keep the updated state
  } catch (err) {
    // Rollback on error
    events.value = originalEvents;
    error.value = err as ApiError;
  }
};
```

### Pattern 2: Debounced Search

```typescript
// composables/features/useEventSearch.ts
import { ref, watch } from 'vue';
import { useDebounce } from '@/composables/utils/useDebounce';

export function useEventSearch() {
  const searchQuery = ref('');
  const debouncedQuery = useDebounce(searchQuery, 500);

  watch(debouncedQuery, (newQuery) => {
    // Trigger search with debounced value
    if (newQuery.length >= 3) {
      performSearch(newQuery);
    }
  });

  return { searchQuery };
}
```

### Pattern 3: Infinite Scroll

```typescript
// composables/features/useInfiniteEvents.ts
export function useInfiniteEvents() {
  const events = ref<Event[]>([]);
  const cursor = ref<string | undefined>(undefined);
  const hasMore = ref(true);

  const loadMore = async () => {
    if (!hasMore.value || isLoading.value) return;

    isLoading.value = true;
    try {
      const response = await eventsApi.getEventsPaginated({ cursor: cursor.value });
      events.value.push(...response.items);
      cursor.value = response.next_cursor;
      hasMore.value = response.has_more;
    } finally {
      isLoading.value = false;
    }
  };

  return { events, loadMore, hasMore };
}
```

### Pattern 4: Real-time Updates with WebSocket

```typescript
// composables/features/useRealtimeEvents.ts
import { ref, onMounted, onUnmounted } from 'vue';

export function useRealtimeEvents() {
  const events = ref<Event[]>([]);
  let ws: WebSocket | null = null;

  const connect = () => {
    ws = new WebSocket('wss://api.example.com/events');

    ws.onmessage = (message) => {
      const newEvent = JSON.parse(message.data);
      // Add to beginning of list
      events.value.unshift(newEvent);
      // Keep only last 100 events
      if (events.value.length > 100) {
        events.value = events.value.slice(0, 100);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  const disconnect = () => {
    if (ws) {
      ws.close();
      ws = null;
    }
  };

  onMounted(connect);
  onUnmounted(disconnect);

  return { events };
}
```

### Pattern 5: Form Handling

```typescript
// composables/features/useAgentForm.ts
import { ref, computed } from 'vue';
import type { AgentDeploymentRequest, ValidationError } from '@/core/types';

export function useAgentForm() {
  const formData = ref<AgentDeploymentRequest>({
    account: '',
    region: ''
  });

  const errors = ref<ValidationError[]>([]);
  const isSubmitting = ref(false);

  const isValid = computed(() => {
    return formData.value.account.length > 0 && formData.value.region.length > 0;
  });

  const validate = (): boolean => {
    errors.value = [];

    if (!formData.value.account) {
      errors.value.push({ field: 'account', message: 'Account is required' });
    }

    if (!formData.value.region) {
      errors.value.push({ field: 'region', message: 'Region is required' });
    }

    return errors.value.length === 0;
  };

  const submitForm = async () => {
    if (!validate()) return;

    isSubmitting.value = true;
    try {
      await agentsApi.createAgent(formData.value);
      // Success handling
      return true;
    } catch (err) {
      // Error handling
      return false;
    } finally {
      isSubmitting.value = false;
    }
  };

  const resetForm = () => {
    formData.value = { account: '', region: '' };
    errors.value = [];
  };

  return {
    formData,
    errors,
    isValid,
    isSubmitting,
    submitForm,
    resetForm
  };
}
```

## Testing Examples

### Unit Test: Composable

```typescript
// tests/unit/composables/useEvents.test.ts
import { describe, it, expect, vi } from 'vitest';
import { useEvents } from '@/composables/features/useEvents';
import { eventsApi } from '@/api/modules/events.api';

vi.mock('@/api/modules/events.api');

describe('useEvents', () => {
  it('should fetch events successfully', async () => {
    const mockEvents = [
      { id: '1', account: '123', severity: Severity.High }
    ];

    vi.mocked(eventsApi.getEvents).mockResolvedValue({
      items: mockEvents,
      total: 1,
      page: 1,
      page_size: 20,
      has_more: false
    });

    const { events, fetchEvents, isLoading } = useEvents();

    await fetchEvents();

    expect(isLoading.value).toBe(false);
    expect(events.value).toEqual(mockEvents);
  });
});
```

### Unit Test: Component

```typescript
// tests/unit/components/SeverityIndicator.test.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import SeverityIndicator from '@/components/modules/events/SeverityIndicator.vue';
import { Severity } from '@/core/types';

describe('SeverityIndicator', () => {
  it('should render critical severity correctly', () => {
    const wrapper = mount(SeverityIndicator, {
      props: { severity: Severity.Critical }
    });

    expect(wrapper.text()).toContain('Critical');
    expect(wrapper.find('.badge').classes()).toContain('bg-red-100');
  });
});
```

## Performance Tips

1. **Lazy Loading**: Use dynamic imports for routes and heavy components
2. **Virtual Scrolling**: For large lists (1000+ items)
3. **Memoization**: Use `computed()` for expensive calculations
4. **Debouncing**: For search and filter inputs
5. **Request Deduplication**: Cancel pending requests when new ones are made
6. **Caching**: Cache API responses in composables or Pinia stores

## Summary

This implementation guide shows:

- How to implement a complete feature from types to UI
- How different layers interact (API → Composable → Component)
- Common patterns for data fetching, forms, and real-time updates
- Testing strategies for composables and components
- Performance optimization techniques

Follow these patterns for consistent, maintainable code across your frontend application.

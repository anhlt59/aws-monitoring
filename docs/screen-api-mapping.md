# Screen-to-API Mapping

This document maps each frontend screen to its corresponding API endpoints and data flow.

## Overview

Each screen integrates with specific API endpoints to fetch, display, and modify data. This mapping helps developers understand:
- Which API endpoints are used by each screen
- When API calls are triggered
- How data flows through the application

---

## 1. Login Screen (`/login`)

### API Endpoints

| Endpoint | Method | Purpose | Trigger |
|----------|--------|---------|---------|
| `/auth/login` | POST | Authenticate user | User clicks "Login" button |
| `/auth/refresh` | POST | Refresh access token | Token expiration (automatic) |

### Data Flow

```
[Login Form]
    ↓ (email, password)
POST /auth/login
    ↓ (200 OK)
[Store JWT token in localStorage]
    ↓
[Navigate to Dashboard]
```

### Request/Response Examples

**Login Request:**
```typescript
// composables/features/useAuth.ts
const login = async (credentials: LoginCredentials) => {
  const response = await authApi.login(credentials);
  // Store tokens
  localStorage.setItem('access_token', response.access_token);
  localStorage.setItem('refresh_token', response.refresh_token);
  // Update store
  authStore.setUser(response.user);
  authStore.setToken(response.access_token);
  // Navigate
  router.push('/dashboard');
};
```

---

## 2. Dashboard Screen (`/dashboard`)

### API Endpoints

| Endpoint | Method | Purpose | Trigger | Frequency |
|----------|--------|---------|---------|-----------|
| `/dashboard/stats` | GET | Get summary statistics | Page mount | Every 30s |
| `/events?limit=10&sort=-published_at` | GET | Get recent events | Page mount | Every 30s |
| `/agents` | GET | Get agent status | Page mount | Every 60s |
| `/dashboard/timeline?days=7` | GET | Get events timeline | Page mount | Every 60s |

### Data Flow

```
[Dashboard Page Mount]
    ↓
[Parallel API Calls]
    ├── GET /dashboard/stats → [Stats Cards]
    ├── GET /events?limit=10 → [Recent Events Widget]
    ├── GET /agents → [Agent Health Widget]
    └── GET /dashboard/timeline → [Timeline Chart]
```

### Implementation Example

```typescript
// composables/features/useDashboard.ts
export function useDashboard() {
  const stats = ref<DashboardStats | null>(null);
  const recentEvents = ref<Event[]>([]);
  const agents = ref<Agent[]>([]);
  const timeline = ref<TimelineData[]>([]);
  const isLoading = ref(true);

  const fetchDashboardData = async () => {
    isLoading.value = true;
    try {
      // Parallel API calls
      const [statsData, eventsData, agentsData, timelineData] =
        await Promise.all([
          dashboardApi.getStats(),
          eventsApi.getEvents({ limit: 10, sort: '-published_at' }),
          agentsApi.getAgents(),
          dashboardApi.getTimeline({ days: 7 })
        ]);

      stats.value = statsData;
      recentEvents.value = eventsData.items;
      agents.value = agentsData;
      timeline.value = timelineData.data;
    } catch (err) {
      error.value = err as ApiError;
    } finally {
      isLoading.value = false;
    }
  };

  // Auto-refresh
  onMounted(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // 30s
    onUnmounted(() => clearInterval(interval));
  });

  return { stats, recentEvents, agents, timeline, isLoading };
}
```

---

## 3. Events List Screen (`/events`)

### API Endpoints

| Endpoint | Method | Purpose | Trigger | Notes |
|----------|--------|---------|---------|-------|
| `/events` | GET | Get filtered events | Page mount, filter change | With query params |
| `/events/accounts` | GET | Get account list | Page mount | For filter dropdown |
| `/events/regions` | GET | Get region list | Page mount | For filter dropdown |
| `/events/export` | GET | Export events | User clicks "Export" | Download file |

### Query Parameters

```
GET /events?
  account=123456789012&
  region=us-east-1&
  severity=3&severity=4&
  start_date=1705276800&
  end_date=1705363200&
  search=lambda&
  page=1&
  page_size=20&
  sort=-published_at
```

### Data Flow

```
[Events List Page]
    ↓
[Initial Load]
    ├── GET /events/accounts → [Account Filter Options]
    ├── GET /events/regions → [Region Filter Options]
    └── GET /events → [Events Table]

[User Changes Filters]
    ↓ (account, region, severity, dates)
[Update URL Query Params]
    ↓
GET /events?{filters}
    ↓
[Update Events Table]
```

### Implementation Example

```typescript
// composables/features/useEvents.ts
export function useEvents() {
  const events = ref<Event[]>([]);
  const total = ref(0);
  const filters = ref<EventFilters>({
    page: 1,
    page_size: 20,
    sort: '-published_at'
  });

  const fetchEvents = async () => {
    isLoading.value = true;
    try {
      const response = await eventsApi.getEvents(filters.value);
      events.value = response.items;
      total.value = response.total;

      // Update URL to reflect filters (for shareable links)
      router.replace({
        query: { ...filters.value }
      });
    } catch (err) {
      error.value = err as ApiError;
    } finally {
      isLoading.value = false;
    }
  };

  const setFilters = (newFilters: Partial<EventFilters>) => {
    filters.value = { ...filters.value, ...newFilters, page: 1 };
    fetchEvents();
  };

  // Load filters from URL on mount
  onMounted(() => {
    const queryFilters = router.currentRoute.value.query;
    if (Object.keys(queryFilters).length > 0) {
      filters.value = { ...filters.value, ...queryFilters };
    }
    fetchEvents();
  });

  return { events, total, filters, setFilters, fetchEvents };
}
```

---

## 4. Event Detail Screen (`/events/:id`)

### API Endpoints

| Endpoint | Method | Purpose | Trigger |
|----------|--------|---------|---------|
| `/events/{id}` | GET | Get event details | Page mount |
| `/events/{id}/related` | GET | Get related events | Page mount |
| `/events/{id}` | PATCH | Update event | User acknowledges or adds notes |

### Data Flow

```
[Event Detail Page Mount]
    ↓ (event ID from route)
[Parallel API Calls]
    ├── GET /events/{id} → [Event Details Cards]
    └── GET /events/{id}/related → [Related Events Sidebar]

[User Acknowledges Event]
    ↓
PATCH /events/{id} { acknowledged: true }
    ↓
[Update Event Status]
```

### Implementation Example

```typescript
// pages/Events/EventDetailPage.vue
<script setup lang="ts">
import { useRoute } from 'vue-router';
import { useEventDetail } from '@/composables/features/useEventDetail';

const route = useRoute();
const eventId = route.params.id as string;

const { event, relatedEvents, updateEvent, isLoading } =
  useEventDetail(eventId);

const acknowledgeEvent = async () => {
  await updateEvent({ acknowledged: true });
};
</script>
```

```typescript
// composables/features/useEventDetail.ts
export function useEventDetail(eventId: string) {
  const event = ref<Event | null>(null);
  const relatedEvents = ref<Event[]>([]);

  const fetchEventDetails = async () => {
    const [eventData, relatedData] = await Promise.all([
      eventsApi.getEventById(eventId),
      eventsApi.getRelatedEvents(eventId, { limit: 10 })
    ]);

    event.value = eventData;
    relatedEvents.value = relatedData.items;
  };

  const updateEvent = async (updates: Partial<Event>) => {
    const updated = await eventsApi.updateEvent(eventId, updates);
    event.value = updated;
  };

  onMounted(fetchEventDetails);

  return { event, relatedEvents, updateEvent };
}
```

---

## 5. Agents List Screen (`/agents`)

### API Endpoints

| Endpoint | Method | Purpose | Trigger |
|----------|--------|---------|---------|
| `/agents` | GET | Get all agents | Page mount, every 60s |
| `/agents` | POST | Deploy new agent | User clicks "Deploy" |
| `/agents/{account}` | DELETE | Delete agent | User confirms deletion |
| `/agents/{account}/redeploy` | POST | Redeploy agent | User clicks "Redeploy" |

### Data Flow

```
[Agents List Page]
    ↓
GET /agents
    ↓
[Display Agents Table]

[User Deploys New Agent]
    ↓ (account, region, config)
POST /agents
    ↓ (201 Created)
[Show deployment progress]
    ↓
[Poll agent status every 5s until complete]
    ↓
GET /agents
    ↓
[Update agents list]
```

### Implementation Example

```typescript
// composables/features/useAgents.ts
export function useAgents() {
  const agents = ref<Agent[]>([]);
  const deployingAgents = ref<Set<string>>(new Set());

  const deployAgent = async (request: AgentDeploymentRequest) => {
    const agent = await agentsApi.deployAgent(request);

    // Add to tracking set
    deployingAgents.value.add(agent.account);

    // Poll status until deployment complete
    const pollInterval = setInterval(async () => {
      const updated = await agentsApi.getAgent(agent.account);

      if (updated.status === 'CREATE_COMPLETE' ||
          updated.status === 'CREATE_FAILED') {
        deployingAgents.value.delete(agent.account);
        clearInterval(pollInterval);
        await fetchAgents(); // Refresh list
      }
    }, 5000); // Poll every 5 seconds
  };

  return { agents, deployAgent, deployingAgents };
}
```

---

## 6. Agent Detail Screen (`/agents/:account`)

### API Endpoints

| Endpoint | Method | Purpose | Trigger | Frequency |
|----------|--------|---------|---------|-----------|
| `/agents/{account}` | GET | Get agent details | Page mount | Once |
| `/agents/{account}/metrics` | GET | Get agent metrics | Page mount | Every 60s |
| `/agents/{account}/health` | GET | Get health status | Page mount | Every 30s |
| `/events?agent_account={account}&limit=10` | GET | Get recent events | Page mount | Every 60s |
| `/agents/{account}` | PUT | Update configuration | User saves config | On demand |

### Data Flow

```
[Agent Detail Page Mount]
    ↓ (account from route)
[Parallel API Calls]
    ├── GET /agents/{account} → [Agent Info Card]
    ├── GET /agents/{account}/metrics → [Metrics Cards]
    ├── GET /agents/{account}/health → [Health Card]
    └── GET /events?agent_account={account} → [Recent Events]

[User Updates Configuration]
    ↓ (new config)
PUT /agents/{account}
    ↓
[Refresh agent details]
```

---

## 7. Reports Screen (`/reports`)

### API Endpoints

| Endpoint | Method | Purpose | Trigger |
|----------|--------|---------|---------|
| `/reports/daily?date={date}` | GET | Get daily report | Date selection |
| `/reports/custom` | POST | Generate custom report | User clicks "Generate" |
| `/reports` | GET | List previous reports | Page mount |
| `/reports/{id}/download?format={fmt}` | GET | Download report | User clicks download |

### Data Flow

```
[Reports Page - Daily Tab]
    ↓ (selected date)
GET /reports/daily?date=2024-01-15
    ↓
[Display Report with Charts]

[User Downloads Report]
    ↓ (format: pdf)
GET /reports/{id}/download?format=pdf
    ↓
[Download PDF file]

[Reports Page - Custom Tab]
    ↓ (date range, filters)
POST /reports/custom
    ↓
[Generate report]
    ↓
[Display custom report]
```

### Implementation Example

```typescript
// composables/features/useReports.ts
export function useReports() {
  const dailyReport = ref<DailyReport | null>(null);
  const selectedDate = ref(new Date());

  const fetchDailyReport = async (date: Date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    const report = await reportsApi.getDailyReport(dateStr);
    dailyReport.value = report;
  };

  const generateCustomReport = async (params: CustomReportParams) => {
    const report = await reportsApi.generateCustomReport(params);
    return report;
  };

  const downloadReport = async (reportId: string, format: 'pdf' | 'csv') => {
    const blob = await reportsApi.downloadReport(reportId, format);
    // Trigger browser download
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report-${reportId}.${format}`;
    a.click();
  };

  watch(selectedDate, fetchDailyReport);
  onMounted(() => fetchDailyReport(selectedDate.value));

  return { dailyReport, selectedDate, generateCustomReport, downloadReport };
}
```

---

## 8. Settings Screen (`/settings`)

### API Endpoints

| Endpoint | Method | Purpose | Trigger |
|----------|--------|---------|---------|
| `/users/me` | GET | Get user profile | Page mount |
| `/users/me` | PUT | Update profile | User saves changes |
| `/users/me/change-password` | POST | Change password | User submits password form |
| `/settings/notifications` | GET | Get notification settings | Tab switch |
| `/settings/notifications` | PUT | Update notification settings | User saves settings |
| `/settings/system` | GET | Get system settings (admin) | Tab switch |
| `/settings/system` | PUT | Update system settings (admin) | User saves settings |

### Data Flow

```
[Settings Page - Profile Tab]
    ↓
GET /users/me
    ↓
[Display Profile Form]

[User Updates Profile]
    ↓ (name, email)
PUT /users/me
    ↓
[Show success message]

[Settings Page - Notifications Tab]
    ↓
GET /settings/notifications
    ↓
[Display Notification Preferences]

[User Updates Preferences]
    ↓ (severity preferences)
PUT /settings/notifications
    ↓
[Show success message]
```

---

## API Integration Patterns

### Pattern 1: Optimistic Updates

For immediate UI feedback, update local state before API call:

```typescript
const acknowledgeEvent = async (eventId: string) => {
  // Optimistic update
  const originalEvent = { ...event.value };
  event.value.acknowledged = true;

  try {
    // API call
    await eventsApi.updateEvent(eventId, { acknowledged: true });
  } catch (err) {
    // Rollback on error
    event.value = originalEvent;
    showError('Failed to acknowledge event');
  }
};
```

### Pattern 2: Polling for Status Updates

For long-running operations like agent deployment:

```typescript
const pollAgentStatus = async (account: string) => {
  const poll = async () => {
    const agent = await agentsApi.getAgent(account);

    if (agent.status === 'CREATE_COMPLETE' ||
        agent.status === 'CREATE_FAILED') {
      return agent; // Stop polling
    }

    await new Promise(resolve => setTimeout(resolve, 5000));
    return poll(); // Continue polling
  };

  return poll();
};
```

### Pattern 3: Debounced Search

For search inputs, debounce API calls:

```typescript
const searchQuery = ref('');
const debouncedQuery = useDebounce(searchQuery, 500);

watch(debouncedQuery, async (query) => {
  if (query.length >= 3) {
    const results = await eventsApi.searchEvents(query);
    events.value = results.items;
  }
});
```

### Pattern 4: Infinite Scroll

For large datasets, use cursor-based pagination:

```typescript
const events = ref<Event[]>([]);
const cursor = ref<string | undefined>();
const hasMore = ref(true);

const loadMore = async () => {
  if (!hasMore.value) return;

  const response = await eventsApi.getEventsPaginated({ cursor: cursor.value });
  events.value.push(...response.items);
  cursor.value = response.next_cursor;
  hasMore.value = response.has_more;
};
```

### Pattern 5: Request Cancellation

Cancel pending requests when component unmounts:

```typescript
import axios from 'axios';

export function useEvents() {
  const cancelToken = ref<CancelTokenSource | null>(null);

  const fetchEvents = async () => {
    // Cancel previous request
    if (cancelToken.value) {
      cancelToken.value.cancel('New request initiated');
    }

    // Create new cancel token
    cancelToken.value = axios.CancelToken.source();

    try {
      const response = await eventsApi.getEvents(
        filters.value,
        { cancelToken: cancelToken.value.token }
      );
      events.value = response.items;
    } catch (err) {
      if (!axios.isCancel(err)) {
        error.value = err as ApiError;
      }
    }
  };

  onUnmounted(() => {
    if (cancelToken.value) {
      cancelToken.value.cancel('Component unmounted');
    }
  });

  return { fetchEvents };
}
```

---

## Error Handling

### Global Error Interceptor

```typescript
// api/interceptors.ts
apiClient.interceptors.response.use(
  response => response,
  error => {
    const apiError: ApiError = {
      code: error.response?.data?.code || 'UNKNOWN_ERROR',
      message: error.response?.data?.message || 'An error occurred',
      details: error.response?.data?.details
    };

    // Handle specific errors
    if (error.response?.status === 401) {
      // Token expired - refresh or redirect to login
      authStore.logout();
      router.push('/login');
    } else if (error.response?.status === 403) {
      // Insufficient permissions
      showToast({ type: 'error', message: 'Insufficient permissions' });
    } else if (error.response?.status === 429) {
      // Rate limit exceeded
      showToast({ type: 'warning', message: 'Too many requests. Please wait.' });
    }

    return Promise.reject(apiError);
  }
);
```

### Screen-Level Error Handling

```typescript
// composables/features/useEvents.ts
const fetchEvents = async () => {
  isLoading.value = true;
  error.value = null;

  try {
    const response = await eventsApi.getEvents(filters.value);
    events.value = response.items;
  } catch (err) {
    const apiError = err as ApiError;
    error.value = apiError;

    // Show user-friendly error
    showToast({
      type: 'error',
      message: apiError.message || 'Failed to load events'
    });
  } finally {
    isLoading.value = false;
  }
};
```

---

## Caching Strategy

### API Response Caching

```typescript
// api/cache.ts
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

export function getCachedOrFetch<T>(
  key: string,
  fetchFn: () => Promise<T>
): Promise<T> {
  const cached = cache.get(key);

  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return Promise.resolve(cached.data);
  }

  return fetchFn().then(data => {
    cache.set(key, { data, timestamp: Date.now() });
    return data;
  });
}

// Usage
const getAgents = () => {
  return getCachedOrFetch('agents', () =>
    apiClient.get<Agent[]>('/agents').then(r => r.data)
  );
};
```

---

## Summary

This mapping provides:
- **Clear endpoint usage** for each screen
- **Data flow diagrams** showing API call sequences
- **Implementation examples** with real code patterns
- **Integration patterns** for common scenarios
- **Error handling** strategies
- **Caching** approaches

Use this as a reference when implementing frontend screens to ensure consistent API integration across the application.

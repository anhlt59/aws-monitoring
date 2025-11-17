# Frontend Architecture Index

**Project**: AWS Monitoring - Serverless Multi-Account Monitoring Solution
**Status**: No Frontend Implementation (Backend API Only)
**Generated**: 2025-11-17

---

## Current State

**The AWS Monitoring project currently has NO frontend implementation.** It is a pure backend API service providing:

- REST API endpoints via API Gateway
- Event-driven processing via Lambda functions
- Slack notifications for monitoring events

The project exposes REST APIs that can be consumed by:
- External frontend applications
- CLI tools
- Other microservices
- Monitoring dashboards (e.g., Grafana, custom dashboards)

---

## Available REST APIs

The backend provides the following REST API endpoints that a frontend could consume:

### Events API

**Base URL**: `https://{api-gateway-url}/events`

#### Endpoints

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/events` | List monitoring events with pagination | `{items: Event[], limit, next, previous}` |
| GET | `/events/{id}` | Get single event by ID | `Event` |

#### Event Model Schema

```typescript
interface Event {
  id: string;                    // Event ID
  account: string;               // AWS Account ID
  region: string | null;         // AWS Region
  source: string;                // Event source (aws.cloudwatch, aws.health, etc.)
  detail: Record<string, any>;   // Event detail payload
  detail_type: string | null;    // Event detail type
  resources: string[];           // ARNs of affected resources
  published_at: number;          // Unix timestamp
  updated_at: number;            // Unix timestamp
}
```

#### Query Parameters (List Events)

```typescript
interface ListEventsParams {
  start_date?: number;    // Unix timestamp - filter start
  end_date?: number;      // Unix timestamp - filter end
  limit?: number;         // Items per page (default: 50, max: 100)
  direction?: 'asc' | 'desc';  // Sort order (default: 'desc')
  cursor?: string;        // Pagination cursor (base64 encoded)
}
```

#### Response Format (List Events)

```typescript
interface ListEventsResponse {
  items: Event[];         // Array of events
  limit: number;          // Items per page
  next: string | null;    // Next page cursor (base64)
  previous: string | null;// Previous page cursor (base64)
}
```

### Agents API

**Base URL**: `https://{api-gateway-url}/agents`

#### Endpoints

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/agents` | List all monitoring agents | `{items: Agent[]}` |
| GET | `/agents/{id}` | Get single agent by account ID | `Agent` |
| POST | `/agents` | Create new agent | `Agent` |
| PATCH | `/agents/{id}` | Update agent | `Agent` |
| DELETE | `/agents/{id}` | Delete agent | `204 No Content` |

#### Agent Model Schema

```typescript
interface Agent {
  account: string;        // AWS Account ID
  region: string;         // AWS Region
  status: string;         // Deployment status (CREATE_COMPLETE, UPDATE_COMPLETE, etc.)
  deployed_at: number;    // Unix timestamp of deployment
  created_at: number;     // Unix timestamp of creation
}
```

#### Create/Update Agent Payload

```typescript
interface CreateAgentPayload {
  account: string;
  region: string;
  status?: string;
}

interface UpdateAgentPayload {
  region?: string;
  status?: string;
  deployed_at?: number;
}
```

---

## Enumerations & Constants

### Event Sources

```typescript
enum EventSource {
  CLOUDWATCH = 'aws.cloudwatch',
  HEALTH = 'aws.health',
  GUARDDUTY = 'aws.guardduty',
  CLOUDFORMATION = 'aws.cloudformation',
  ECS = 'aws.ecs',
  LAMBDA = 'aws.lambda'
}
```

### Severity Levels

```typescript
enum SeverityLevel {
  UNKNOWN = 0,
  LOW = 1,
  MEDIUM = 2,
  HIGH = 3,
  CRITICAL = 4
}
```

### CloudWatch Alarm States

```typescript
enum AlarmState {
  OK = 'OK',
  ALARM = 'ALARM',
  INSUFFICIENT_DATA = 'INSUFFICIENT_DATA'
}
```

### CloudFormation Stack Status

```typescript
enum CfnStackStatus {
  CREATE_IN_PROGRESS = 'CREATE_IN_PROGRESS',
  CREATE_COMPLETE = 'CREATE_COMPLETE',
  CREATE_FAILED = 'CREATE_FAILED',
  UPDATE_IN_PROGRESS = 'UPDATE_IN_PROGRESS',
  UPDATE_COMPLETE = 'UPDATE_COMPLETE',
  UPDATE_FAILED = 'UPDATE_FAILED',
  DELETE_IN_PROGRESS = 'DELETE_IN_PROGRESS',
  DELETE_COMPLETE = 'DELETE_COMPLETE',
  DELETE_FAILED = 'DELETE_FAILED'
}
```

---

## Frontend Development Guidelines

If implementing a frontend for this project, consider the following:

### Recommended Tech Stack

#### Framework Options

**React + TypeScript** (Recommended)
- Modern, widely adopted
- Strong TypeScript support
- Rich ecosystem
- Server-side rendering with Next.js

**Vue 3 + TypeScript**
- Lighter weight alternative
- Good TypeScript support
- Simpler learning curve

**Svelte + TypeScript**
- Minimal runtime overhead
- Reactive by default
- Growing ecosystem

#### State Management

- **TanStack Query (React Query)** - Server state management
- **Zustand** or **Jotai** - Client state management
- **Redux Toolkit** - For complex state requirements

#### UI Component Libraries

- **shadcn/ui** - Modern, accessible components
- **Material-UI (MUI)** - Comprehensive component library
- **Ant Design** - Enterprise-grade components
- **Chakra UI** - Accessible, composable components

#### Data Fetching

- **TanStack Query** - Caching, pagination, optimistic updates
- **SWR** - Stale-while-revalidate pattern
- **Axios** - HTTP client with interceptors

#### Visualization (for Monitoring Dashboard)

- **Recharts** - React charting library
- **Chart.js + react-chartjs-2** - Popular charting
- **Apache ECharts** - Rich, interactive charts
- **D3.js** - Custom, complex visualizations

### Architecture Recommendations

#### Project Structure

```
frontend/
├── src/
│   ├── api/                  # API client and types
│   │   ├── client.ts         # Axios/Fetch client configuration
│   │   ├── events.ts         # Events API calls
│   │   ├── agents.ts         # Agents API calls
│   │   └── types.ts          # TypeScript interfaces
│   ├── components/           # Reusable components
│   │   ├── common/           # Common UI components
│   │   ├── events/           # Event-specific components
│   │   ├── agents/           # Agent-specific components
│   │   └── charts/           # Chart components
│   ├── pages/                # Page components
│   │   ├── Dashboard.tsx     # Main dashboard
│   │   ├── Events.tsx        # Events list/detail
│   │   ├── Agents.tsx        # Agents management
│   │   └── Reports.tsx       # Reports view
│   ├── hooks/                # Custom React hooks
│   │   ├── useEvents.ts      # Events data fetching
│   │   ├── useAgents.ts      # Agents data fetching
│   │   └── usePagination.ts  # Pagination logic
│   ├── stores/               # State management
│   │   ├── authStore.ts      # Authentication state
│   │   └── uiStore.ts        # UI state
│   ├── utils/                # Utility functions
│   │   ├── dateFormat.ts     # Date formatting
│   │   ├── eventHelpers.ts   # Event processing
│   │   └── api.ts            # API helpers
│   └── types/                # TypeScript types
│       ├── event.ts          # Event types
│       ├── agent.ts          # Agent types
│       └── api.ts            # API response types
├── public/                   # Static assets
├── package.json
└── tsconfig.json
```

#### API Client Setup

```typescript
// src/api/client.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://api.example.com';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

#### Events API Client

```typescript
// src/api/events.ts
import { apiClient } from './client';
import type { Event, ListEventsParams, ListEventsResponse } from './types';

export const eventsApi = {
  list: async (params?: ListEventsParams): Promise<ListEventsResponse> => {
    const response = await apiClient.get<ListEventsResponse>('/events', { params });
    return response.data;
  },

  get: async (id: string): Promise<Event> => {
    const response = await apiClient.get<Event>(`/events/${id}`);
    return response.data;
  },
};
```

#### Custom Hook for Events

```typescript
// src/hooks/useEvents.ts
import { useQuery } from '@tanstack/react-query';
import { eventsApi } from '@/api/events';
import type { ListEventsParams } from '@/api/types';

export const useEvents = (params?: ListEventsParams) => {
  return useQuery({
    queryKey: ['events', params],
    queryFn: () => eventsApi.list(params),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
};

export const useEvent = (id: string) => {
  return useQuery({
    queryKey: ['event', id],
    queryFn: () => eventsApi.get(id),
    enabled: !!id,
  });
};
```

### Key Features to Implement

#### 1. Dashboard

**Features:**
- Real-time event stream
- Summary cards (total events, critical events, agents status)
- Timeline chart of events by severity
- Quick filters (last 1h, 6h, 24h, 7d)

**Components:**
- `<Dashboard />` - Main container
- `<SummaryCards />` - Metrics cards
- `<EventTimeline />` - Time-series chart
- `<RecentEvents />` - Latest events list

#### 2. Events List

**Features:**
- Paginated event list
- Filtering by date range, severity, source, account
- Search functionality
- Sort by timestamp
- Export to CSV/JSON

**Components:**
- `<EventsList />` - Main list container
- `<EventCard />` - Individual event display
- `<EventFilters />` - Filter controls
- `<Pagination />` - Pagination controls

#### 3. Event Detail

**Features:**
- Full event details
- JSON viewer for event payload
- Related events
- Timeline of status changes

**Components:**
- `<EventDetail />` - Main detail view
- `<JsonViewer />` - Formatted JSON display
- `<ResourceLinks />` - AWS Console links

#### 4. Agents Management

**Features:**
- List all monitoring agents
- Agent status (active, inactive, failed)
- Add/edit/delete agents
- Deployment history

**Components:**
- `<AgentsList />` - Agents table
- `<AgentForm />` - Create/edit form
- `<AgentStatus />` - Status indicator

#### 5. Reports

**Features:**
- Daily/weekly reports view
- Event statistics and trends
- Download reports as PDF
- Scheduled report configuration

**Components:**
- `<ReportsView />` - Reports container
- `<ReportChart />` - Visualizations
- `<ReportExport />` - Export options

### Authentication & Authorization

If implementing authentication:

**Options:**
1. **AWS Cognito** - Native AWS integration
2. **Auth0** - Third-party auth service
3. **Custom JWT** - DIY authentication

**Implementation:**
- Protect API Gateway with Cognito authorizer
- Store JWT in localStorage or httpOnly cookie
- Implement refresh token flow
- Role-based access control (RBAC)

### Real-Time Updates

For real-time event updates:

**Options:**
1. **WebSockets via API Gateway**
   - Enable WebSocket API in API Gateway
   - Lambda functions for connect/disconnect/message
   - Push events to connected clients

2. **Server-Sent Events (SSE)**
   - Long-lived HTTP connections
   - One-way server-to-client communication

3. **Polling**
   - Periodic API calls (every 30-60 seconds)
   - Simple, works everywhere
   - Higher latency

**Recommended**: WebSockets for real-time, or polling with TanStack Query for simplicity.

### Error Handling

```typescript
// src/api/errorHandler.ts
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export const handleApiError = (error: any): ApiError => {
  if (error.response) {
    // Server responded with error
    return new ApiError(
      error.response.data?.message || 'An error occurred',
      error.response.status,
      error.response.data
    );
  } else if (error.request) {
    // Request made but no response
    return new ApiError('No response from server', 0);
  } else {
    // Error setting up request
    return new ApiError(error.message, 0);
  }
};
```

### Performance Optimization

**Strategies:**
- Use pagination for large lists
- Implement virtual scrolling for long lists
- Lazy load components with React.lazy()
- Memoize expensive computations with useMemo()
- Debounce search inputs
- Optimize images and assets
- Use CDN for static assets
- Implement service worker for offline support

### Testing

**Testing Stack:**
- **Vitest** - Unit testing
- **React Testing Library** - Component testing
- **Playwright** or **Cypress** - E2E testing
- **MSW (Mock Service Worker)** - API mocking

**Test Coverage:**
- API client functions
- Custom hooks
- Component rendering
- User interactions
- Error states

### Deployment

**Hosting Options:**
1. **AWS S3 + CloudFront**
   - Static site hosting
   - CDN distribution
   - Low cost

2. **AWS Amplify**
   - Automated builds and deployments
   - Built-in CI/CD
   - Preview environments

3. **Vercel** or **Netlify**
   - Easy deployment
   - Automatic HTTPS
   - Edge functions

**CI/CD:**
- GitHub Actions or GitLab CI
- Automated testing
- Build optimization
- Deploy to staging/production

---

## Integration Checklist

When building a frontend:

### API Integration
- [ ] Set up API client with base URL
- [ ] Implement authentication flow
- [ ] Create typed interfaces for all API responses
- [ ] Add request/response interceptors
- [ ] Handle error responses gracefully
- [ ] Implement retry logic for failed requests

### Components
- [ ] Dashboard with summary metrics
- [ ] Events list with pagination
- [ ] Event detail view
- [ ] Agents management interface
- [ ] Filters and search functionality
- [ ] Loading states
- [ ] Error states
- [ ] Empty states

### State Management
- [ ] Set up TanStack Query or similar
- [ ] Configure caching strategy
- [ ] Implement optimistic updates
- [ ] Handle real-time updates

### Testing
- [ ] Unit tests for API client
- [ ] Component tests
- [ ] Integration tests
- [ ] E2E tests for critical flows

### Performance
- [ ] Implement pagination
- [ ] Add virtual scrolling for large lists
- [ ] Optimize bundle size
- [ ] Lazy load components
- [ ] Add loading skeletons

### Deployment
- [ ] Set up CI/CD pipeline
- [ ] Configure environment variables
- [ ] Set up staging environment
- [ ] Configure CDN
- [ ] Add monitoring (Sentry, LogRocket, etc.)

---

## Future Considerations

### Advanced Features

**Real-Time Monitoring:**
- WebSocket integration for live event stream
- Live metrics dashboard
- Alert notifications

**Analytics:**
- Event trend analysis
- Anomaly detection visualization
- Custom dashboards

**Collaboration:**
- User comments on events
- Event assignment and workflows
- Team notifications

**Integrations:**
- Export to external systems
- Webhook configurations
- Third-party integrations (PagerDuty, Opsgenie)

---

## Example Component Implementation

### Events List Component

```typescript
// src/components/events/EventsList.tsx
import { useState } from 'react';
import { useEvents } from '@/hooks/useEvents';
import { EventCard } from './EventCard';
import { Pagination } from '@/components/common/Pagination';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorAlert } from '@/components/common/ErrorAlert';

export const EventsList = () => {
  const [filters, setFilters] = useState({
    limit: 50,
    direction: 'desc' as const,
    cursor: undefined,
  });

  const { data, isLoading, error, refetch } = useEvents(filters);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorAlert error={error} onRetry={refetch} />;
  }

  return (
    <div className="events-list">
      <div className="events-header">
        <h2>Monitoring Events</h2>
        <button onClick={() => refetch()}>Refresh</button>
      </div>

      <div className="events-grid">
        {data?.items.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>

      <Pagination
        hasNext={!!data?.next}
        hasPrevious={!!data?.previous}
        onNext={() => setFilters((f) => ({ ...f, cursor: data?.next }))}
        onPrevious={() => setFilters((f) => ({ ...f, cursor: data?.previous }))}
      />
    </div>
  );
};
```

---

**Index Version**: 1.0.0
**Last Updated**: 2025-11-17
**Status**: Planning Document (No Implementation Yet)

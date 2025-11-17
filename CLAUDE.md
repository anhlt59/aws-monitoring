# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack serverless AWS monitoring application with:
- **Backend**: Python 3.13 serverless backend using hexagonal architecture
- **Frontend**: Vue 3 + TypeScript frontend with Tailwind CSS
- **Infrastructure**: AWS services (Lambda, DynamoDB, EventBridge, CloudWatch)

## Repository Structure

```
aws-monitoring/
├── backend/           # Python backend (serverless, domain-driven design)
│   ├── src/          # Source code (domain, adapters, entrypoints)
│   ├── tests/        # Test files
│   ├── statics/      # Jinja templates for notifications
│   ├── pyproject.toml
│   ├── poetry.lock
│   ├── serverless.yml
│   └── .env.local
├── frontend/         # Vue 3 frontend
│   ├── src/          # Frontend source (pages, components, store, etc.)
│   ├── public/       # Static assets
│   └── package.json
├── infra/           # Infrastructure as Code (Serverless Framework)
│   ├── configs/     # Environment-specific configs
│   ├── functions/   # Lambda function definitions
│   ├── resources/   # CloudFormation templates
│   └── plugins/     # Serverless plugins
├── ops/             # Operations and deployment scripts
│   ├── deployment/  # Deploy, package, bootstrap scripts
│   ├── development/ # Install, start, coverage scripts
│   └── tools/       # CLI tools (monitoring profile manager)
├── docs/            # Documentation
└── Makefile         # Common development commands
```

## Rules

- At the end of each task, summarize what has been completed and what remains
- **Backend**: Follow hexagonal architecture principles: Domain → Ports → Adapters
- **Frontend**: Follow composition API patterns and single responsibility components
- Maintain test coverage above 90% for both backend and frontend
- Use specific exception types in Python, avoid broad `except Exception` handlers
- All new code must include type hints (Python) and proper TypeScript types (Frontend)
- Use Pydantic validation for backend data models
- Follow Vue 3 Composition API with `<script setup>` syntax in frontend

---

# Backend Development

## Tech Stack

- **Runtime**: Python 3.13
- **Framework**: Serverless Framework 4.x
- **Database**: DynamoDB (single-table design with PynamoDB ORM)
- **Infrastructure**: AWS Lambda, API Gateway, EventBridge, SNS, S3, CloudWatch
- **Validation**: Pydantic v2.11.0 with strict type safety
- **Testing**: Pytest, Coverage, Moto (AWS mocking)
- **Local Development**: LocalStack, Docker

## Backend Architecture

The backend follows hexagonal architecture (ports and adapters pattern):

### Domain Layer (`backend/src/domain/`)

- **Models**: Core business entities (Event, Agent) with domain logic
- **Ports**: Interfaces defining contracts for external dependencies
  - `repositories.py` - Data persistence interfaces
  - `notifier.py` - Notification interfaces
  - `publisher.py` - Event publishing interfaces
  - `logs.py` - Log query interfaces
- **Use Cases**: Business logic orchestration
  - `daily_report.py` - Generate daily monitoring reports
  - `insert_monitoring_event.py` - Process incoming events
  - `query_error_logs.py` - Query CloudWatch logs for errors
  - `update_deployment.py` - Handle deployment updates

### Adapters Layer (`backend/src/adapters/`)

- **Database** (`backend/src/adapters/db/`):
  - `models/` - DynamoDB-specific entity representations
  - `mappers/` - Convert between domain and database models
  - `repositories/` - Implement domain repository interfaces
- **AWS Services** (`backend/src/adapters/aws/`):
  - `cloudwatch.py` - CloudWatch Logs Insights queries
  - `eventbridge.py` - Event publishing
  - `ecs.py` - ECS task management
  - `lambda_function.py` - Lambda invocations
- **External Services**:
  - `notifiers/` - Slack, email notifications
  - `logs.py` - CloudWatch log adapter
  - `publisher.py` - EventBridge publisher

### Entry Points (`backend/src/entrypoints/`)

- **Functions** (`backend/src/entrypoints/functions/`):
  - Lambda handlers for business operations
  - Minimal logic, delegates to use cases
- **API Gateway** (`backend/src/entrypoints/apigw/`):
  - REST API endpoints for events and agents

### Common Layer (`backend/src/common/`)

- Shared utilities, configurations, logger, exceptions
- Cross-cutting concerns

## Backend Commands

```bash
# Development
make install        # Install Python & Node.js dependencies
make activate       # Activate Python virtual environment
make test           # Run backend tests with coverage
make coverage       # Generate HTML coverage report
make start          # Start LocalStack and deploy backend

# Deployment
make deploy         # Deploy to environment (stage=local by default)
make package        # Create deployment artifacts
make destroy        # Remove deployed stack
make bootstrap      # Prepare S3 buckets and IAM roles

# Monitoring Tool
make mon            # Launch monitoring profile manager
```

### Backend-Specific Commands

```bash
# From backend directory
cd backend

# Run specific test file
poetry run pytest tests/integrations/api/test_events.py -v

# Run tests with AWS mocking
poetry run pytest tests/ --cov=src --cov-report=html

# Check types
poetry run mypy src/

# Format code
poetry run ruff check src/ --fix
```

## Backend Best Practices

### Error Handling Pattern

```python
# ❌ AVOID: Broad exception handling
try:
    operation()
except Exception as err:
    raise InternalServerError(f"Error: {err}")

# ✅ PREFERRED: Specific exception types
try:
    operation()
except DoesNotExist as err:
    raise NotFoundError(f"Resource not found: {err}")
except PutError as err:
    raise UnprocessedError(f"Database error: {err}")
except Exception as err:
    logger.exception("Unexpected error")
    raise InternalServerError(f"Internal error: {err}")
```

### Repository Pattern Usage

- Base repository: `backend/src/adapters/db/repositories/base.py`
- Use generic methods: `_get()`, `_query()`, `_create()`, `_update()`, `_delete()`
- Always use mappers to convert between domain and persistence models
- Example: `backend/src/adapters/db/repositories/event.py`

### Type Safety with Pydantic

```python
# All domain models use Pydantic v2
from pydantic import BaseModel, Field, field_validator

class Event(BaseModel):
    id: str
    account: str
    region: str | None = None
    detail: dict
    published_at: int = Field(default_factory=current_utc_timestamp)

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not value:
            raise ValueError("ID cannot be empty")
        return value
```

### Batch Processing Pattern

```python
# Use chunking utility for batch operations
from backend.src.common.utils.objects import chunks

for chunk in chunks(log_groups, chunk_size=10):
    # Process in batches to avoid rate limits
    results = process_batch(chunk)
```

## Backend Testing

### Test Structure

- Test files mirror source structure in `backend/tests/`
- Integration tests: `backend/tests/integrations/`
- Adapter tests: `backend/tests/adapters/`
- Test fixtures: `backend/tests/conftest.py`
- Mock data: `backend/tests/data/`

### Coverage Expectations

- Minimum: 88% overall coverage (current baseline)
- Target: >90% coverage for new features
- Critical paths: 100% coverage (repositories, use cases)

### AWS Service Mocking

- Use `moto` library for AWS service mocking
- LocalStack for integration testing
- Example setup in `backend/tests/conftest.py`

## Backend File Reference

**Error Handling**:
- Exception definitions: `backend/src/common/exceptions.py`
- Repository error handling: `backend/src/adapters/db/repositories/base.py`

**Configuration**:
- Environment variables: `backend/src/common/constants.py`
- Serverless configs: `infra/configs/`

**Core Business Logic**:
- Event processing: `backend/src/domain/use_cases/insert_monitoring_event.py`
- Log querying: `backend/src/domain/use_cases/query_error_logs.py`
- Daily reports: `backend/src/domain/use_cases/daily_report.py`

**AWS Service Adapters**:
- CloudWatch: `backend/src/adapters/aws/cloudwatch.py`
- EventBridge: `backend/src/adapters/aws/eventbridge.py`
- ECS: `backend/src/adapters/aws/ecs.py`
- Lambda: `backend/src/adapters/aws/lambda_function.py`

**Notification Templates**:
- Template directory: `backend/statics/templates/`
- Template constants: `backend/src/common/constants.py`

---

# Frontend Development

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

## Frontend Architecture

The frontend follows a layered architecture with clear separation of concerns:

### Core Layer (`frontend/src/core/`)

Domain layer containing business logic foundations:
- `types/` - TypeScript type definitions (Event, Agent, ApiResponse)
- `enums/` - Enumerations (EventSeverity, AgentStatus, etc.)
- `constants.ts` - Application constants

### Infrastructure Layer (`frontend/src/api/`)

External dependencies and HTTP communication:
- `client.ts` - Axios HTTP client with interceptors
- Service modules for API communication (events, agents, etc.)

### Application Layer

Business logic and state management:
- `store/` - Pinia stores for global state
- `composables/` - Reusable composition functions
- `utils/` - Utility functions

### Presentation Layer

UI components and pages:
- `components/` - Reusable UI components
- `pages/` - Route entry points
- `router/` - Routing configuration
- `styles/` - Global styles (Tailwind, CSS variables)

## Frontend Commands

```bash
# From frontend directory
cd frontend

# Development
npm install          # Install dependencies
npm run dev          # Start dev server (http://localhost:3000)
npm run build        # Build for production
npm run preview      # Preview production build

# Testing
npm run test         # Run tests
npm run test:ui      # Run tests with UI
npm run test:coverage # Generate coverage report

# Code Quality
npm run lint         # Lint code
npm run lint:fix     # Fix linting issues
npm run format       # Format code with Prettier
npm run type-check   # Check TypeScript types
```

## Frontend Best Practices

### Component Structure

```vue
<script setup lang="ts">
// ✅ PREFERRED: Composition API with script setup
import { ref, computed, onMounted } from 'vue'
import type { Event } from '@/core/types'

interface Props {
  eventId: string
  showDetails?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: false
})

const emit = defineEmits<{
  update: [event: Event]
  delete: [id: string]
}>()

// Reactive state
const event = ref<Event | null>(null)
const loading = ref(false)

// Computed properties
const formattedDate = computed(() => {
  return event.value ? formatDate(event.value.publishedAt) : ''
})

// Methods
async function fetchEvent() {
  loading.value = true
  try {
    event.value = await eventsApi.getById(props.eventId)
  } catch (error) {
    console.error('Failed to fetch event:', error)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  fetchEvent()
})
</script>

<template>
  <div v-if="loading">Loading...</div>
  <div v-else-if="event" class="event-card">
    <h2>{{ event.detailType }}</h2>
    <p>{{ formattedDate }}</p>
    <div v-if="showDetails">
      <!-- Details content -->
    </div>
  </div>
</template>

<style scoped>
.event-card {
  @apply rounded-lg border border-gray-200 p-4 shadow-sm;
}
</style>
```

### Type Safety

```typescript
// ✅ Define explicit types
interface Event {
  id: string
  account: string
  region?: string
  detail: Record<string, unknown>
  detailType: string
  severity: EventSeverity
  publishedAt: number
}

// ✅ Use type guards
function isEvent(obj: unknown): obj is Event {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'account' in obj
  )
}

// ✅ Generic API response
interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}
```

### State Management with Pinia

```typescript
// stores/events.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Event } from '@/core/types'

export const useEventsStore = defineStore('events', () => {
  // State
  const events = ref<Event[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const criticalEvents = computed(() =>
    events.value.filter(e => e.severity === EventSeverity.Critical)
  )

  // Actions
  async function fetchEvents() {
    loading.value = true
    error.value = null
    try {
      const response = await eventsApi.list()
      events.value = response.data
    } catch (err) {
      error.value = 'Failed to fetch events'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  return {
    events,
    loading,
    error,
    criticalEvents,
    fetchEvents
  }
})
```

### Composables Pattern

```typescript
// composables/useEvents.ts
import { ref, onMounted } from 'vue'
import type { Event } from '@/core/types'
import { eventsApi } from '@/api/events'

export function useEvents() {
  const events = ref<Event[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)

  async function fetchEvents() {
    loading.value = true
    error.value = null
    try {
      const response = await eventsApi.list()
      events.value = response.data
    } catch (err) {
      error.value = err as Error
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    fetchEvents()
  })

  return {
    events,
    loading,
    error,
    fetchEvents
  }
}
```

### API Client Pattern

```typescript
// api/client.ts
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if needed
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // Handle errors globally
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default apiClient
```

## Frontend Testing

### Component Testing

```typescript
// __tests__/EventCard.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EventCard from '@/components/EventCard.vue'
import type { Event } from '@/core/types'

describe('EventCard', () => {
  const mockEvent: Event = {
    id: '123',
    account: '000000000000',
    detailType: 'CloudWatch Alarm',
    severity: EventSeverity.High,
    publishedAt: Date.now()
  }

  it('renders event details correctly', () => {
    const wrapper = mount(EventCard, {
      props: { event: mockEvent }
    })

    expect(wrapper.text()).toContain('CloudWatch Alarm')
    expect(wrapper.find('.severity-badge').classes()).toContain('severity-high')
  })

  it('emits delete event when delete button clicked', async () => {
    const wrapper = mount(EventCard, {
      props: { event: mockEvent }
    })

    await wrapper.find('.delete-btn').trigger('click')
    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')?.[0]).toEqual([mockEvent.id])
  })
})
```

### Coverage Expectations

- Minimum: 80% overall coverage
- Target: >90% for critical components
- 100% coverage for utility functions and stores

## Frontend File Structure

```
frontend/src/
├── core/              # Domain layer
│   ├── types/         # TypeScript interfaces
│   │   └── index.ts
│   ├── enums/         # Enumerations
│   │   └── index.ts
│   └── constants.ts   # Application constants
├── api/               # Infrastructure layer
│   ├── client.ts      # Axios client
│   └── events.ts      # Events API service
├── composables/       # Reusable composition functions
│   └── useEvents.ts
├── store/             # Pinia stores
│   └── modules/
│       ├── auth.store.ts
│       └── events.store.ts
├── components/        # Reusable components
│   ├── common/        # Generic components
│   └── events/        # Event-specific components
├── pages/             # Route entry points
│   ├── Dashboard.vue
│   ├── Events/
│   │   └── EventsListPage.vue
│   └── Agents/
│       └── AgentsListPage.vue
├── router/            # Routing
│   ├── index.ts
│   └── routes/
│       ├── index.ts
│       └── guards.ts
├── styles/            # Global styles
│   ├── main.css
│   ├── variables.css
│   └── utilities.css
├── utils/             # Utility functions
├── App.vue            # Root component
└── main.ts            # Application entry point
```

---

# Common Development Tasks

## Backend Tasks

### Adding a New Event Type

1. Define event model in `backend/src/domain/models/`
2. Create mapper in `backend/src/adapters/db/mappers/`
3. Update repository in `backend/src/adapters/db/repositories/`
4. Add use case in `backend/src/domain/use_cases/`
5. Create entrypoint handler in `backend/src/entrypoints/functions/`
6. Update Serverless config in `infra/functions/`

### Adding a New Notifier

1. Create notifier class in `backend/src/adapters/notifiers/`
2. Implement `INotifier` port from `backend/src/domain/ports/notifier.py`
3. Add Jinja2 template in `backend/statics/templates/`
4. Update use case to inject notifier

### Modifying DynamoDB Schema

1. Update domain model in `backend/src/domain/models/`
2. Update persistence model in `backend/src/adapters/db/models/`
3. Update mapper in `backend/src/adapters/db/mappers/`
4. Update CloudFormation in `infra/resources/dynamodb.yml`
5. Write migration script if needed

## Frontend Tasks

### Adding a New Page

1. Create page component in `frontend/src/pages/`
2. Add route in `frontend/src/router/routes/index.ts`
3. Create necessary API service in `frontend/src/api/`
4. Add Pinia store if needed in `frontend/src/store/modules/`
5. Write tests in `frontend/src/__tests__/`

### Adding a New Component

1. Create component in `frontend/src/components/`
2. Define TypeScript interfaces/props
3. Follow composition API with `<script setup>`
4. Use Tailwind CSS for styling
5. Write component tests

### Adding API Integration

1. Define types in `frontend/src/core/types/`
2. Create API service in `frontend/src/api/`
3. Update Axios client if needed
4. Create composable in `frontend/src/composables/`
5. Update store if needed

---

# Security Guidelines

## Backend Security

- ✅ No hardcoded credentials in source code
- ✅ Webhook URLs loaded from environment variables
- ✅ AWS credentials managed by IAM roles
- ✅ All API inputs validated with Pydantic models
- ✅ DynamoDB encryption at rest (AWS KMS)
- ✅ TLS 1.2+ for all API calls

## Frontend Security

- ✅ No sensitive data in localStorage (use secure cookies for auth)
- ✅ Sanitize user input to prevent XSS
- ✅ Use environment variables for API endpoints
- ✅ Implement CSRF protection
- ✅ Content Security Policy headers
- ✅ API key/token rotation strategy

---

# Performance Considerations

## Backend Performance

- CloudWatch queries: Chunked to 10 log groups per query
- EventBridge publishing: Batched messages
- DynamoDB: Single-table design with optimized access patterns
- Lambda cold starts: Minimize dependencies in handlers

## Frontend Performance

- Code splitting with dynamic imports
- Lazy loading for routes
- Virtual scrolling for large lists
- Debounce search inputs
- Cache API responses when appropriate
- Optimize bundle size with tree-shaking

---

# Documentation References

## Backend Documentation
- Project structure: `docs/project_structure.md`
- Database schema: `docs/db.md`
- Architecture overview: `docs/overview.md`
- Development guide: `docs/development.md`
- Deployment guide: `docs/deployment.md`

## Frontend Documentation
- Frontend overview: `docs/frontend-overview.md`
- Quick start: `docs/frontend-quick-start.md`
- Design documentation: `docs/frontend-design.md`
- Implementation guide: `docs/frontend-implementation-guide.md`
- Types reference: `docs/frontend-types-reference.md`
- API specification: `docs/api-specification.yaml`

---

# Environment Setup

## Backend Environment Variables

Located in `backend/.env.local`:
```bash
POWERTOOLS_LOG_LEVEL=DEBUG
MONITORING_WEBHOOK_URL=https://hooks.slack.com/...
DYNAMODB_TABLE=monitoring-local
```

## Frontend Environment Variables

Located in `frontend/.env.development`:
```bash
VITE_API_BASE_URL=http://localhost:3001/api
VITE_APP_NAME=AWS Monitoring
```

---

# Git Workflow

## Branch Naming

- Feature: `feat/feature-name`
- Bug fix: `fix/bug-description`
- Refactor: `refactor/what-changed`
- Documentation: `docs/what-documented`
- Claude Code: `claude/task-description-{sessionId}`

## Commit Messages

Follow conventional commits:
```
feat: add event filtering by severity
fix: resolve timezone issue in event timestamps
refactor: reorganize backend structure
docs: update API documentation
test: add tests for event repository
chore: update dependencies
```

---

# Local Development Workflow

## Full Stack Development

1. **Start Backend**:
   ```bash
   make start        # Start LocalStack
   make deploy       # Deploy backend (stage=local)
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev       # http://localhost:3000
   ```

3. **Run Tests**:
   ```bash
   make test         # Backend tests
   cd frontend && npm run test  # Frontend tests
   ```

4. **Monitor Logs**:
   ```bash
   docker logs -f localstack  # Backend logs
   ```

## Backend-Only Development

```bash
make install      # Install dependencies
make start        # Start LocalStack
make deploy       # Deploy backend
make test         # Run tests
```

## Frontend-Only Development

```bash
cd frontend
npm install       # Install dependencies
npm run dev       # Start dev server
npm run test      # Run tests
npm run lint      # Lint code
```

---

# Troubleshooting

## Backend Issues

**Poetry issues**: Delete `.venv` and run `make install`
**LocalStack not starting**: Check Docker is running, restart with `docker compose restart localstack`
**Import errors**: Ensure virtual environment is activated
**Test failures**: Check LocalStack is running for integration tests

## Frontend Issues

**Dependency conflicts**: Delete `node_modules` and `package-lock.json`, run `npm install`
**Type errors**: Run `npm run type-check` to see all type issues
**Build failures**: Check for missing environment variables
**API connection issues**: Verify backend is running on expected port

---

# Quick Reference

## Most Common Commands

```bash
# Setup
make install                    # Install all dependencies

# Development
make start                      # Start backend (LocalStack)
cd frontend && npm run dev      # Start frontend

# Testing
make test                       # Backend tests
cd frontend && npm run test     # Frontend tests
make coverage                   # Backend coverage report

# Deployment
make deploy stage=local         # Deploy to local
make deploy stage=dev           # Deploy to dev
make package stage=prod         # Package for prod

# Code Quality
make mon                        # Monitoring profile manager
cd frontend && npm run lint     # Lint frontend
cd frontend && npm run format   # Format frontend
```

## Key File Locations

- Backend source: `backend/src/`
- Frontend source: `frontend/src/`
- Infrastructure: `infra/`
- Tests: `backend/tests/`, `frontend/src/__tests__/`
- Documentation: `docs/`
- Configuration: `backend/pyproject.toml`, `frontend/package.json`
- Environment: `backend/.env.local`, `frontend/.env.development`

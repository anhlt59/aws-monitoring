# API-First Design Summary

This document provides an overview of the comprehensive API-first design for the AWS Monitoring web application.

## 📚 Documentation Overview

### Frontend Architecture Design
1. **[frontend-overview.md](./frontend-overview.md)** - High-level architecture introduction
2. **[frontend-design.md](./frontend-design.md)** - Complete architectural design
3. **[frontend-types-reference.md](./frontend-types-reference.md)** - TypeScript type definitions
4. **[frontend-implementation-guide.md](./frontend-implementation-guide.md)** - Implementation examples
5. **[frontend-quick-start.md](./frontend-quick-start.md)** - Project setup guide
6. **[frontend-documentation-guide.md](./frontend-documentation-guide.md)** - Navigation guide

### API Design & Integration
7. **[frontend-screens-design.md](./frontend-screens-design.md)** - UI/UX screen designs
8. **[api-specification.yaml](./api-specification.yaml)** - OpenAPI 3.0 specification
9. **[screen-api-mapping.md](./screen-api-mapping.md)** - Screen-to-API integration guide

---

## 🎯 Design Principles

### API-First Approach
- Design APIs before implementation
- Use OpenAPI/Swagger specification
- Contract-first development
- Backend and frontend teams work in parallel

### RESTful Design
- Resource-based URLs
- Standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Proper status codes
- Stateless communication

### Type Safety
- TypeScript throughout frontend
- Pydantic validation on backend
- Shared type definitions
- No `any` types

### Hexagonal Architecture
- Clear separation of concerns
- Domain-driven design
- Ports and adapters pattern
- Testable components

---

## 🖥️ Screen Designs (8 Screens)

### 1. **Login Screen** (`/login`)
**Purpose:** User authentication

**Features:**
- Email/password authentication
- Remember me option
- JWT token management
- Rate limiting (5 attempts per 15 min)

**API Endpoints:**
- `POST /auth/login`
- `POST /auth/refresh`

---

### 2. **Dashboard** (`/` or `/dashboard`)
**Purpose:** High-level monitoring overview

**Components:**
- Statistics cards (Critical, High, Medium, Low events)
- Recent events widget (last 10 events)
- Agent health widget (all agents status)
- Events timeline chart (7-day trend)

**API Endpoints:**
- `GET /dashboard/stats`
- `GET /events?limit=10&sort=-published_at`
- `GET /agents`
- `GET /dashboard/timeline?days=7`

**Features:**
- Auto-refresh every 30 seconds
- Real-time statistics
- Interactive charts

---

### 3. **Events List** (`/events`)
**Purpose:** View and filter all monitoring events

**Components:**
- Advanced filter bar (account, region, severity, date range)
- Search functionality (full-text)
- Sortable table with pagination
- Export options (CSV, JSON, PDF)

**API Endpoints:**
- `GET /events` (with filters)
- `GET /events/accounts`
- `GET /events/regions`
- `GET /events/export?format={csv|json|pdf}`

**Features:**
- URL parameter sync (shareable links)
- Virtual scrolling for large datasets
- Debounced search
- Custom date ranges

---

### 4. **Event Detail** (`/events/:id`)
**Purpose:** Detailed view of a specific event

**Components:**
- Event header with severity badge
- Metadata card (account, region, timestamps)
- Event details card (parsed by event type)
- Affected resources list
- Raw event data (JSON viewer)
- Related events sidebar

**API Endpoints:**
- `GET /events/{id}`
- `GET /events/{id}/related`
- `PATCH /events/{id}` (acknowledge, add notes)

**Features:**
- Event-type-specific parsing
- Syntax-highlighted JSON
- Copy to clipboard
- Acknowledge functionality

---

### 5. **Agents List** (`/agents`)
**Purpose:** Manage monitoring agents across AWS accounts

**Components:**
- Status summary cards (Active, Deploying, Failed)
- Deploy new agent button (modal form)
- Agents table with status indicators
- Row actions (Update, Delete, Redeploy, View Logs)

**API Endpoints:**
- `GET /agents`
- `POST /agents`
- `DELETE /agents/{account}`
- `POST /agents/{account}/redeploy`

**Features:**
- Auto-refresh status every 60 seconds
- Deployment progress tracking
- Bulk operations
- Filter by status/region

---

### 6. **Agent Detail** (`/agents/:account`)
**Purpose:** Detailed view of a specific agent

**Components:**
- Agent status card with actions
- Metrics cards (events published, errors detected, query duration)
- Health check card (uptime, error rate)
- Recent events from agent
- Configuration card (editable)

**API Endpoints:**
- `GET /agents/{account}`
- `GET /agents/{account}/metrics`
- `GET /agents/{account}/health`
- `GET /events?agent_account={account}`
- `PUT /agents/{account}/config`

**Features:**
- Real-time health monitoring
- Performance metrics visualization
- Configuration management

---

### 7. **Reports** (`/reports`)
**Purpose:** View daily reports and generate custom reports

**Components:**
- Daily Reports tab
  - Date selector
  - Summary statistics
  - Charts (pie, bar, line)
  - Top errors table
  - Export options
- Custom Reports tab
  - Date range picker
  - Account/region filters
  - Report format selector
  - Generate button
- Previous reports list

**API Endpoints:**
- `GET /reports/daily?date={YYYY-MM-DD}`
- `POST /reports/custom`
- `GET /reports`
- `GET /reports/{id}/download?format={pdf|csv}`

**Features:**
- Daily automated reports
- Custom report generation
- Multiple export formats
- Historical report access

---

### 8. **Settings** (`/settings`)
**Purpose:** User preferences and system configuration

**Sections:**
- **Profile Tab**
  - Name, email (read-only)
  - Role display
  - Change password

- **Notifications Tab**
  - Email/Slack toggles
  - Severity-based preferences
  - Digest frequency

- **System Tab** (Admin only)
  - Master stack config
  - Agent deployment settings
  - Retention policies
  - Integration settings

**API Endpoints:**
- `GET /users/me`
- `PUT /users/me`
- `POST /users/me/change-password`
- `GET /settings/notifications`
- `PUT /settings/notifications`
- `GET /settings/system`
- `PUT /settings/system`

---

## 🔌 API Specification (40+ Endpoints)

### OpenAPI 3.0 Specification

**File:** `api-specification.yaml`

**Format:** Swagger/OpenAPI 3.0.3

### API Groups

| Group | Endpoints | Description |
|-------|-----------|-------------|
| **Authentication** | 3 | Login, token refresh, logout |
| **Dashboard** | 2 | Statistics, timeline data |
| **Events** | 7 | CRUD operations, filtering, export |
| **Agents** | 8 | CRUD, metrics, health, deployment |
| **Reports** | 4 | Daily, custom, list, download |
| **Users** | 3 | Profile management, password |
| **Settings** | 4 | Notifications, system config |

### Key Features

#### 1. **Authentication**
- JWT Bearer token authentication
- Refresh token mechanism
- Token expiration: 3600s (1 hour)
- Refresh token expiration: 2592000s (30 days)

#### 2. **Pagination**
- Cursor-based pagination for scalability
- Page-based pagination for simple lists
- Default page size: 20
- Maximum page size: 100

**Example:**
```
GET /events?page=1&page_size=20
```

Response:
```json
{
  "items": [...],
  "total": 419,
  "page": 1,
  "page_size": 20,
  "has_more": true
}
```

#### 3. **Filtering**
Multiple filter parameters supported:
```
GET /events?
  account=123456789012&
  region=us-east-1&
  severity=3&severity=4&
  start_date=1705276800&
  end_date=1705363200&
  search=lambda
```

#### 4. **Sorting**
Sort by any field, ascending or descending:
```
GET /events?sort=-published_at,severity
```
- Prefix with `-` for descending order
- Multiple sort fields supported

#### 5. **Rate Limiting**
- 100 requests per minute for authenticated users
- 10 requests per minute for authentication endpoints
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

#### 6. **Error Responses**
Standardized error format:
```json
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid request parameters",
  "details": {
    "field": "account",
    "error": "Must be a 12-digit number"
  },
  "timestamp": 1705327845
}
```

**Error Codes:**
- `BAD_REQUEST` (400)
- `UNAUTHORIZED` (401)
- `FORBIDDEN` (403)
- `NOT_FOUND` (404)
- `RATE_LIMIT_EXCEEDED` (429)
- `INTERNAL_SERVER_ERROR` (500)

---

## 🔄 Data Flow Patterns

### Pattern 1: Initial Page Load
```
User navigates to page
    ↓
Page component mounts
    ↓
Call API endpoints (parallel)
    ↓
Display data
    ↓
Set up auto-refresh (if applicable)
```

### Pattern 2: Filter & Search
```
User modifies filters
    ↓
Update URL query parameters
    ↓
Call API with new filters
    ↓
Update displayed data
    ↓
URL is shareable
```

### Pattern 3: Real-time Updates
```
Page loaded
    ↓
Set up interval timer (30s/60s)
    ↓
Fetch latest data
    ↓
Update UI if data changed
    ↓
Repeat
```

### Pattern 4: Long Operations
```
User initiates operation (e.g., deploy agent)
    ↓
Call API (returns 201 Created)
    ↓
Show "In Progress" status
    ↓
Poll API every 5s
    ↓
Update UI when complete
    ↓
Show success/failure
```

### Pattern 5: Optimistic Updates
```
User performs action (e.g., acknowledge event)
    ↓
Update UI immediately (optimistic)
    ↓
Call API
    ↓
If success: Keep UI state
If error: Rollback UI + show error
```

---

## 🎨 Frontend Technology Stack

### Core Framework
- **Vue 3.3+** - Progressive JavaScript framework
- **TypeScript 5.0+** - Type-safe development
- **Vite 5.0+** - Fast build tool

### State & Routing
- **Pinia** - State management
- **Vue Router 4** - Client-side routing

### UI & Styling
- **Tailwind CSS 3.4+** - Utility-first CSS
- **@tailwindcss/forms** - Form styling
- **@tailwindcss/typography** - Typography

### HTTP & Data
- **Axios** - HTTP client
- **date-fns** - Date manipulation

### Development Tools
- **Vitest** - Unit testing
- **@vue/test-utils** - Component testing
- **ESLint** - Code linting
- **Prettier** - Code formatting

---

## 📊 Type System

### Core Types (Aligned with Backend)

```typescript
// Event
interface Event {
  id: string;
  account: string;
  region: string;
  source: string;
  detail: Record<string, unknown>;
  detail_type: string;
  severity: Severity; // 0-4
  resources: string[];
  published_at: number; // Unix timestamp
  updated_at: number;
}

// Agent
interface Agent {
  account: string;
  region: string;
  status: AgentStatus;
  deployed_at: number;
  created_at: number;
}

// Severity Enum
enum Severity {
  Unknown = 0,
  Low = 1,
  Medium = 2,
  High = 3,
  Critical = 4
}

// Agent Status
enum AgentStatus {
  CreateComplete = 'CREATE_COMPLETE',
  CreateInProgress = 'CREATE_IN_PROGRESS',
  CreateFailed = 'CREATE_FAILED',
  // ... more statuses
}
```

---

## 🔐 Security Considerations

### Authentication
- JWT token-based authentication
- Automatic token refresh
- Secure token storage (localStorage with encryption recommended)
- Token expiration handling

### Authorization
- Role-based access control (Admin, Operator, Viewer)
- Permission-based features
- Route guards
- API-level authorization

### Data Protection
- XSS prevention (Vue's default escaping)
- CSRF protection (token-based)
- Input validation (client & server)
- Secure headers

### API Security
- HTTPS only in production
- Rate limiting
- CORS configuration
- Request validation

---

## 📈 Performance Optimizations

### Frontend
- **Code Splitting:** Route-based lazy loading
- **Virtual Scrolling:** For large lists (1000+ items)
- **Debouncing:** Search inputs (500ms delay)
- **Caching:** API responses (5-minute TTL)
- **Memoization:** Expensive computed properties
- **Image Optimization:** Lazy loading, WebP format

### Backend
- **Database Indexing:** Optimized queries
- **Pagination:** Cursor-based for scalability
- **Batch Processing:** Reduce API calls
- **CDN:** Static assets delivery
- **Compression:** Gzip/Brotli for responses

### Network
- **Request Cancellation:** Cancel pending on new request
- **Parallel Requests:** Fetch multiple endpoints simultaneously
- **HTTP/2:** Multiplexing support
- **Connection Pooling:** Reuse connections

---

## 🧪 Testing Strategy

### Frontend Tests

#### Unit Tests
- **Components:** Props, events, rendering
- **Composables:** Business logic isolation
- **Utils:** Pure functions

#### Integration Tests
- **Modules:** With mocked API
- **Pages:** Full feature flows

#### E2E Tests
- **Critical Paths:** Login, view events, deploy agent
- **User Journeys:** End-to-end workflows

### API Tests

#### Contract Tests
- Validate OpenAPI spec compliance
- Request/response schema validation

#### Integration Tests
- Test API endpoints with real backend
- Database integration

#### Load Tests
- Rate limiting validation
- Performance under load

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Set up Vite + Vue 3 + TypeScript project
- [ ] Configure Tailwind CSS
- [ ] Implement authentication (login/logout)
- [ ] Create base components library
- [ ] Set up API client with interceptors

### Phase 2: Core Features (Week 3-4)
- [ ] Dashboard screen
- [ ] Events list screen
- [ ] Event detail screen
- [ ] Agent list screen

### Phase 3: Advanced Features (Week 5-6)
- [ ] Agent detail screen
- [ ] Reports screen
- [ ] Settings screen
- [ ] Real-time updates

### Phase 4: Polish & Testing (Week 7-8)
- [ ] Responsive design
- [ ] Accessibility improvements
- [ ] Unit tests (>80% coverage)
- [ ] E2E tests
- [ ] Performance optimization

### Phase 5: Deployment (Week 9)
- [ ] Production build
- [ ] CI/CD pipeline
- [ ] Monitoring & logging
- [ ] Documentation

---

## 📝 Development Guidelines

### Code Style
- Use TypeScript strict mode
- No `any` types
- ESLint + Prettier for consistency
- Vue 3 Composition API with `<script setup>`

### Naming Conventions
- **Components:** PascalCase (`EventList.vue`)
- **Composables:** camelCase with `use` prefix (`useEvents.ts`)
- **API Services:** camelCase with `.api` suffix (`events.api.ts`)
- **Types:** PascalCase (`Event`, `Agent`)

### File Organization
```
src/
├── core/types/        # Type definitions
├── api/modules/       # API services
├── composables/       # Business logic
├── components/base/   # Reusable components
├── components/modules/# Feature components
├── pages/             # Route views
├── router/            # Routing
├── store/             # State management
└── utils/             # Utilities
```

### Git Workflow
- Feature branches from `main`
- Conventional commits
- Pull requests for review
- Automated tests in CI

---

## 📚 Additional Resources

### Documentation Files
1. Frontend architecture and design documents
2. API specification (OpenAPI 3.0)
3. Screen designs and wireframes
4. Screen-to-API mapping
5. Implementation guide with examples
6. Quick start setup guide

### External Resources
- [Vue 3 Documentation](https://vuejs.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/)
- [OpenAPI Specification](https://swagger.io/specification/)

---

## 🎯 Success Metrics

### Technical Metrics
- **Code Coverage:** >80% (target: 90%)
- **Type Safety:** 100% (no `any` types)
- **Performance:** <2s page load time
- **Accessibility:** WCAG 2.1 AA compliance
- **API Response Time:** <500ms (p95)

### User Experience Metrics
- **Time to Interactive:** <3s
- **First Contentful Paint:** <1.5s
- **Error Rate:** <1%
- **User Satisfaction:** >4.5/5

---

## 📞 Support & Contact

For questions or issues:
- Review relevant documentation in `/docs`
- Check implementation examples in guides
- Consult API specification for endpoint details
- Refer to screen designs for UI/UX guidance

---

**This comprehensive design provides everything needed to build a production-ready AWS Monitoring web application with a clean, type-safe, and maintainable architecture.**

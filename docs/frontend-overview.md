# Frontend Overview

## Introduction

This frontend application is built for the AWS Monitoring system using Vue 3, TypeScript, and Tailwind CSS. It provides a modern, type-safe, and maintainable user interface for monitoring AWS resources across multiple accounts.

## Architecture Summary

The frontend follows a **hexagonal architecture** pattern that mirrors the backend structure, making it intuitive for backend developers to understand and work with.

### Core Principles

1. **Separation of Concerns**: Each layer has a single, well-defined responsibility
2. **Type Safety**: TypeScript throughout with strict type checking
3. **Dependency Inversion**: Business logic depends on abstractions, not implementations
4. **Testability**: All layers designed for easy testing with clear boundaries
5. **Reusability**: Components and logic designed for maximum reuse

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Entry Points (Pages)                      │
│                  Vue Router Configuration                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Presentation (Components)                   │
│  ┌────────────────────┐  ┌──────────────────────────────┐  │
│  │  Base Components   │  │   Module Components          │  │
│  │  (Dumb/Reusable)   │  │   (Smart/Feature-specific)   │  │
│  └────────────────────┘  └──────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              Application Logic (Composables)                 │
│         Business logic, data fetching, state management     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│            Infrastructure (API Services)                     │
│           HTTP client, request/response handling            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                Domain (Core Types)                           │
│        TypeScript interfaces and type definitions           │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### Type Safety
- All domain entities defined as TypeScript interfaces
- API responses strongly typed
- Component props and emits typed
- No `any` types in production code

### Modern Stack
- **Vue 3**: Composition API for better logic reuse
- **TypeScript**: Full type safety and IntelliSense
- **Tailwind CSS**: Utility-first styling
- **Vite**: Fast development and optimized builds
- **Pinia**: Modern state management
- **Vue Router**: Client-side routing

### Developer Experience
- Hot Module Replacement (HMR)
- Path aliases (`@/` for `src/`)
- Auto-imports for common utilities
- ESLint + Prettier for code quality
- Vitest for fast unit testing

## Project Structure

```
frontend/
├── src/
│   ├── core/              # Domain layer (types, enums, constants)
│   ├── api/               # Infrastructure layer (HTTP client, API services)
│   ├── composables/       # Application logic (business rules, data fetching)
│   ├── store/             # Global state management (Pinia)
│   ├── components/        # Presentation layer
│   │   ├── base/          # Reusable UI components
│   │   └── modules/       # Feature-specific components
│   ├── pages/             # Route entry points
│   ├── router/            # Routing configuration
│   ├── styles/            # Global styles and Tailwind config
│   └── utils/             # Utility functions
├── tests/                 # Test files
└── public/                # Static assets
```

## Data Flow

### Read Flow (Displaying Data)
```
User opens page
    ↓
Page component mounts
    ↓
Composable fetches data
    ↓
API service makes HTTP request
    ↓
Backend returns data
    ↓
Data transforms to domain types
    ↓
Reactive state updates
    ↓
Components re-render
```

### Write Flow (Modifying Data)
```
User submits form
    ↓
Component validates input
    ↓
Composable processes submission
    ↓
API service sends request
    ↓
Backend processes and responds
    ↓
Success/error handling
    ↓
State updates (optimistic or confirmed)
    ↓
UI reflects changes
```

## Backend Integration

The frontend integrates with the AWS Monitoring backend through RESTful APIs:

| Frontend Feature | Backend Endpoint | Method | Purpose |
|-----------------|------------------|--------|---------|
| Events List | `/events` | GET | Fetch paginated events |
| Event Details | `/events/{id}` | GET | Fetch single event |
| Agents List | `/agents` | GET | Fetch all agents |
| Agent Deploy | `/agents` | POST | Deploy new agent |
| Agent Update | `/agents/{id}` | PUT | Update agent status |
| Daily Report | `/reports/daily` | GET | Fetch daily report |

## Key Technologies

### Core Framework
- **Vue 3.3+**: Progressive JavaScript framework
- **TypeScript 5.0+**: Type-safe JavaScript
- **Vite 5.0+**: Next-generation frontend tooling

### State & Routing
- **Pinia**: Official Vue state management
- **Vue Router 4**: Official Vue routing

### UI & Styling
- **Tailwind CSS 3.4+**: Utility-first CSS framework
- **@tailwindcss/forms**: Form styling plugin
- **@tailwindcss/typography**: Typography plugin

### HTTP & Data
- **Axios**: HTTP client for API calls
- **date-fns**: Date manipulation and formatting

### Development Tools
- **Vitest**: Unit testing framework
- **@vue/test-utils**: Vue component testing
- **ESLint**: Code linting
- **Prettier**: Code formatting

## Development Workflow

### 1. Feature Development
```bash
# 1. Define types in core/types/
# 2. Create API service in api/modules/
# 3. Build composable in composables/features/
# 4. Create components
# 5. Build page
# 6. Add route
# 7. Write tests
```

### 2. Daily Development
```bash
# Start dev server
npm run dev

# Run tests in watch mode
npm run test

# Lint and fix
npm run lint:fix

# Type check
npm run type-check
```

### 3. Production Build
```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Design Patterns

### Composable Pattern (Business Logic)
- Encapsulates reusable logic
- Returns reactive state and methods
- Can be used across multiple components
- Testable in isolation

### Repository Pattern (API Services)
- Single responsibility: communicate with backend
- Type-safe request/response
- Error handling and transformation
- Retry logic and caching

### Component Composition
- Small, focused components
- Props down, events up
- Slots for flexibility
- Type-safe props and emits

## Performance Optimizations

### Code Splitting
- Route-based lazy loading
- Dynamic imports for heavy components
- Vendor chunk separation

### Caching
- API response caching in composables
- LocalStorage for user preferences
- Stale-while-revalidate pattern

### Rendering
- Virtual scrolling for large lists
- Debounced search inputs
- Throttled scroll handlers
- Memoized computed properties

## Testing Strategy

### Unit Tests
- **Components**: Props, events, rendering
- **Composables**: Business logic, state management
- **Utils**: Pure functions

### Integration Tests
- **Module Components**: With mocked API
- **Pages**: Full feature flows

### E2E Tests
- Critical user journeys
- Login flow
- Event filtering and viewing

## Security Considerations

### Authentication
- JWT token-based authentication
- Automatic token refresh
- Secure token storage

### Authorization
- Route-level guards
- Component-level permission checks
- API-level authorization headers

### Data Protection
- XSS prevention (Vue's default escaping)
- CSRF protection (token-based)
- Input validation and sanitization

## Documentation Structure

1. **[frontend-design.md](./frontend-design.md)** - Complete architecture and design
2. **[frontend-types-reference.md](./frontend-types-reference.md)** - TypeScript type definitions
3. **[frontend-implementation-guide.md](./frontend-implementation-guide.md)** - Implementation examples
4. **[frontend-quick-start.md](./frontend-quick-start.md)** - Project setup guide

## Getting Started

### For Backend Developers

If you're coming from backend development:

1. **Types = Domain Models**: `core/types/` is like `src/domain/models/`
2. **API Services = Adapters**: `api/modules/` is like `src/adapters/aws/`
3. **Composables = Use Cases**: `composables/features/` is like `src/domain/use_cases/`
4. **Components = Views**: `components/` is the presentation layer
5. **Pages = Entrypoints**: `pages/` is like `src/entrypoints/`

### Quick Start

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev

# 4. Open browser
# http://localhost:3000
```

See [frontend-quick-start.md](./frontend-quick-start.md) for detailed setup instructions.

## Best Practices

### TypeScript
- Use interfaces for object shapes
- Use types for unions/intersections
- Enable strict mode
- Avoid `any` - use `unknown` if needed

### Components
- Keep components small and focused
- Use TypeScript for props/emits
- Prefer Composition API over Options API
- Use `<script setup>` for cleaner code

### Styling
- Use Tailwind utilities first
- Create components for repeated patterns
- Avoid inline styles
- Use CSS variables for themes

### State Management
- Local state: `ref`/`reactive` in components
- Shared logic: Composables
- Global state: Pinia stores
- URL state: Vue Router query params

### Testing
- Test behavior, not implementation
- Mock external dependencies
- Use data-testid for test selectors
- Aim for >80% coverage

## Common Patterns

### Async Data Fetching
```typescript
const { data, isLoading, error, execute } = useAsyncData(
  () => eventsApi.getEvents(filters)
);
```

### Form Handling
```typescript
const { formData, errors, validate, submit } = useForm({
  onSubmit: async (data) => {
    await agentsApi.createAgent(data);
  }
});
```

### Pagination
```typescript
const { items, page, totalPages, nextPage, previousPage } = usePagination(
  fetchEvents
);
```

## Troubleshooting

### Common Issues

1. **Build errors**: Run `npm run type-check` to identify TypeScript issues
2. **Styles not applying**: Check Tailwind config and CSS imports
3. **API errors**: Verify backend is running and proxy config is correct
4. **Type errors**: Ensure types are up-to-date with backend models

### Debugging

- Use Vue DevTools browser extension
- Enable source maps in build
- Use `console.log` or debugger in composables
- Check Network tab for API calls

## Resources

- **Vue 3 Docs**: https://vuejs.org/
- **TypeScript Docs**: https://www.typescriptlang.org/
- **Tailwind Docs**: https://tailwindcss.com/
- **Vite Docs**: https://vitejs.dev/

## Next Steps

1. **Setup Project**: Follow [frontend-quick-start.md](./frontend-quick-start.md)
2. **Understand Architecture**: Read [frontend-design.md](./frontend-design.md)
3. **Learn Types**: Review [frontend-types-reference.md](./frontend-types-reference.md)
4. **Start Building**: Use [frontend-implementation-guide.md](./frontend-implementation-guide.md)

---

**Happy coding!** The frontend architecture is designed to be intuitive for backend developers while following modern frontend best practices.

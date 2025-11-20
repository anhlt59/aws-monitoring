# AWS Monitoring Frontend

Vue 3 + TypeScript frontend for AWS Resources Monitoring CMS.

## Tech Stack

- **Vue 3.4+** - Progressive JavaScript framework
- **TypeScript 5.0+** - Type-safe JavaScript
- **Vite 5.0+** - Next-generation frontend tooling
- **Vue Router 4** - Official Vue routing
- **Pinia** - Official Vue state management
- **Tailwind CSS 3.4+** - Utility-first CSS framework
- **Axios** - HTTP client for API calls

## Project Structure

```
frontend/
├── src/
│   ├── core/              # Domain layer (types, enums, constants)
│   ├── api/               # Infrastructure layer (HTTP client, API services)
│   ├── composables/       # Application logic (business rules, data fetching)
│   ├── components/        # Presentation layer
│   │   ├── base/          # Reusable UI components
│   │   ├── modules/       # Feature-specific components
│   │   └── layout/        # Layout components
│   ├── pages/             # Route entry points
│   ├── router/            # Routing configuration
│   ├── styles/            # Global styles and Tailwind config
│   └── utils/             # Utility functions
├── tests/                 # Test files
└── public/                # Static assets
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server (http://localhost:3000)
npm run dev

# Type check
npm run type-check

# Lint code
npm run lint
```

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Testing

```bash
# Run tests
npm run test

# Run tests with coverage
npm run test:coverage
```

## Features

### Pages

- **Login** - User authentication
- **Dashboard** - Overview with key metrics and statistics
- **Events** - AWS monitoring events list with filtering
- **Tasks** - Task management with CRUD operations
- **Users** - User management (admin only)
- **Configuration** - AWS accounts and monitoring settings

### Key Components

#### Base Components
- `BaseButton` - Reusable button with variants
- `BaseInput` - Form input with validation
- `BaseSelect` - Select dropdown with options
- `BaseTable` - Data table with pagination
- `BaseBadge` - Status badge with variants
- `BaseCard` - Content card container
- `BaseAlert` - Alert/notification component
- `BaseModal` - Modal dialog
- `BasePagination` - Pagination controls

#### Module Components
- `SeverityBadge` - Event severity indicator
- `TaskStatusBadge` - Task status indicator
- `TaskPriorityBadge` - Task priority indicator
- `AppLayout` - Main application layout with sidebar

### Composables

- `useAuth` - Authentication logic
- `useEvents` - Event management
- `useTasks` - Task management
- `useUsers` - User management
- `useDashboard` - Dashboard data
- `useDebounce` - Debounce utility
- `useFormatDate` - Date formatting utilities

## Architecture

### Layered Architecture

The frontend follows a clean layered architecture:

1. **Domain Layer** (`core/`)
   - Types, enums, constants
   - Pure TypeScript, no Vue dependencies

2. **Infrastructure Layer** (`api/`)
   - HTTP client configuration
   - API service modules
   - External service integration

3. **Application Layer** (`composables/`, `store/`)
   - Business logic
   - State management
   - Data fetching and transformation

4. **Presentation Layer** (`components/`, `pages/`)
   - Vue components
   - User interface
   - User interactions

### Data Flow

```
User Interaction
    ↓
Component (emit event)
    ↓
Composable (business logic)
    ↓
API Service (HTTP request)
    ↓
Backend API
    ↓
Response → Transform → Update State
    ↓
Vue Reactivity → Re-render
```

## Configuration

### Environment Variables

Create `.env.local` for local development:

```env
VITE_API_BASE_URL=http://localhost:4566
VITE_APP_TITLE=AWS Monitoring CMS
```

### API Proxy

The dev server proxies `/api` requests to the backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:4566',
      changeOrigin: true
    }
  }
}
```

## Development Guidelines

### Adding a New Feature

1. **Define Types** → `core/types/`
2. **Create API Service** → `api/modules/`
3. **Build Composable** → `composables/features/`
4. **Create Components** → `components/modules/`
5. **Create Page** → `pages/`
6. **Add Route** → `router/index.ts`

### Code Style

- Use TypeScript for all files
- Follow Vue 3 Composition API
- Use `<script setup>` syntax
- Prefer composables over mixins
- Use Tailwind CSS for styling
- Component names in PascalCase
- Composables start with `use`

### Best Practices

- Keep components small and focused
- Use computed properties for derived state
- Avoid direct DOM manipulation
- Use proper TypeScript types
- Write meaningful commit messages
- Test critical functionality

## Troubleshooting

### Common Issues

**Dependency conflicts:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Type errors:**
```bash
npm run type-check
```

**Build failures:**
- Check environment variables
- Verify backend API is accessible

**API connection issues:**
- Verify backend is running on expected port
- Check CORS configuration
- Review proxy settings in vite.config.ts

## License

This project is proprietary and confidential.

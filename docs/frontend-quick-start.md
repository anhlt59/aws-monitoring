# Frontend Quick Start Guide

This guide provides step-by-step instructions to set up and start developing the frontend application.

## Prerequisites

- **Node.js**: 18.x or higher
- **npm/yarn/pnpm**: Latest stable version
- **Git**: For version control

## Project Initialization

### 1. Create Vite Project with Vue 3 + TypeScript

```bash
# Navigate to project root
cd /home/user/aws-monitoring

# Create frontend directory
npm create vite@latest frontend -- --template vue-ts

# Navigate to frontend directory
cd frontend
```

### 2. Install Dependencies

```bash
# Core dependencies
npm install vue@latest vue-router@latest pinia@latest

# HTTP client
npm install axios

# UI and styling
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest
npm install -D @tailwindcss/forms @tailwindcss/typography

# Utilities
npm install date-fns
npm install @vueuse/core

# Development dependencies
npm install -D @types/node
npm install -D @vitejs/plugin-vue
npm install -D typescript

# Testing
npm install -D vitest @vue/test-utils happy-dom
npm install -D @vitest/ui

# Linting and formatting
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install -D prettier eslint-config-prettier eslint-plugin-vue
```

## Configuration Files

### 1. Tailwind CSS Configuration

```bash
# Initialize Tailwind
npx tailwindcss init -p
```

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Custom colors for severity levels
        severity: {
          critical: '#DC2626',
          high: '#F59E0B',
          medium: '#3B82F6',
          low: '#10B981',
          unknown: '#6B7280'
        },
        // Custom colors for agent status
        status: {
          active: '#10B981',
          inactive: '#EF4444',
          deploying: '#3B82F6',
          failed: '#DC2626'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace']
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ],
}
```

### 2. TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path Aliases */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

```json
// tsconfig.node.json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

### 3. Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      // Proxy API requests to backend during development
      '/api': {
        target: 'http://localhost:3001', // LocalStack API Gateway
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'ui': ['@vueuse/core']
        }
      }
    }
  }
})
```

### 4. Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  test: {
    globals: true,
    environment: 'happy-dom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/**/*.d.ts',
        'src/**/*.spec.ts',
        'src/**/*.test.ts'
      ]
    }
  }
})
```

### 5. ESLint Configuration

```javascript
// eslint.config.js
import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import * as parserVue from 'vue-eslint-parser'
import * as parserTypeScript from '@typescript-eslint/parser'

export default [
  js.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['*.vue', '**/*.vue'],
    languageOptions: {
      parser: parserVue,
      parserOptions: {
        parser: parserTypeScript,
        ecmaVersion: 'latest',
        sourceType: 'module'
      }
    }
  },
  {
    files: ['*.ts', '**/*.ts'],
    languageOptions: {
      parser: parserTypeScript,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module'
      }
    }
  },
  {
    rules: {
      'vue/multi-word-component-names': 'off',
      'vue/require-default-prop': 'off',
      '@typescript-eslint/no-unused-vars': ['error', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_'
      }]
    }
  }
]
```

### 6. Environment Variables

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:3001/api
VITE_APP_TITLE=AWS Monitoring (Dev)
VITE_ENABLE_DEBUG=true
VITE_POLLING_INTERVAL=30000
```

```bash
# .env.production
VITE_API_BASE_URL=https://api.your-domain.com
VITE_APP_TITLE=AWS Monitoring
VITE_ENABLE_DEBUG=false
VITE_POLLING_INTERVAL=60000
```

### 7. Package.json Scripts

```json
// package.json
{
  "name": "aws-monitoring-frontend",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts",
    "lint:fix": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix",
    "format": "prettier --write src/",
    "type-check": "vue-tsc --noEmit"
  }
}
```

## Initial Project Structure

Create the directory structure:

```bash
# Navigate to frontend/src
cd src

# Create directories
mkdir -p assets/{images,fonts}
mkdir -p core/{types,enums}
mkdir -p api/modules
mkdir -p composables/{features,ui,utils}
mkdir -p store/modules
mkdir -p components/{base/{buttons,inputs,layout,feedback,navigation,data-display},modules/{events,agents,reports,dashboard,auth},layout}
mkdir -p pages/{Events,Agents,Reports,Auth,ErrorPages}
mkdir -p router/routes
mkdir -p styles
mkdir -p utils
```

## Core Files Setup

### 1. Main Entry Point

```typescript
// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Import global styles
import './styles/main.css'

const app = createApp(App)

// Install plugins
app.use(createPinia())
app.use(router)

// Mount app
app.mount('#app')
```

### 2. Global Styles

```css
/* src/styles/main.css */
@import './variables.css';

@tailwind base;
@tailwind components;
@tailwind utilities;

@import './utilities.css';

/* Global base styles */
@layer base {
  body {
    @apply bg-gray-50 text-gray-900;
  }

  h1 {
    @apply text-3xl font-bold;
  }

  h2 {
    @apply text-2xl font-semibold;
  }

  h3 {
    @apply text-xl font-semibold;
  }
}
```

```css
/* src/styles/variables.css */
:root {
  /* Color palette */
  --color-primary: #3B82F6;
  --color-secondary: #6B7280;
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #DC2626;

  /* Spacing */
  --spacing-unit: 0.25rem;

  /* Border radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Dark mode variables */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #1F2937;
    --color-text: #F9FAFB;
  }
}
```

```css
/* src/styles/utilities.css */
@layer utilities {
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }

  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }

  .text-balance {
    text-wrap: balance;
  }
}
```

### 3. Root Component

```vue
<!-- src/App.vue -->
<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<style scoped>
#app {
  min-height: 100vh;
}
</style>
```

### 4. Router Setup

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { routes } from './routes'
import { setupGuards } from './routes/guards'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Setup navigation guards
setupGuards(router)

export default router
```

```typescript
// src/router/routes/index.ts
import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
    meta: {
      requiresAuth: true,
      title: 'Dashboard'
    }
  },
  {
    path: '/events',
    name: 'Events',
    component: () => import('@/pages/Events/EventsListPage.vue'),
    meta: {
      requiresAuth: true,
      title: 'Events'
    }
  },
  {
    path: '/agents',
    name: 'Agents',
    component: () => import('@/pages/Agents/AgentsListPage.vue'),
    meta: {
      requiresAuth: true,
      title: 'Agents'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Auth/LoginPage.vue'),
    meta: {
      requiresAuth: false,
      title: 'Login'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/ErrorPages/NotFound.vue')
  }
]
```

```typescript
// src/router/routes/guards.ts
import type { Router } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth.store'

export function setupGuards(router: Router) {
  // Authentication guard
  router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
    } else {
      next()
    }
  })

  // Set page title
  router.afterEach((to) => {
    document.title = to.meta.title
      ? `${to.meta.title} - AWS Monitoring`
      : 'AWS Monitoring'
  })
}
```

### 5. API Client Setup

```typescript
// src/api/client.ts
import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios'
import { useAuthStore } from '@/store/modules/auth.store'
import { API_CONFIG } from '@/core/constants'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore()
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Unauthorized - redirect to login
          const authStore = useAuthStore()
          authStore.logout()
        }
        return Promise.reject(error)
      }
    )
  }

  public get<T>(url: string, config?: AxiosRequestConfig) {
    return this.client.get<T>(url, config)
  }

  public post<T>(url: string, data?: unknown, config?: AxiosRequestConfig) {
    return this.client.post<T>(url, data, config)
  }

  public put<T>(url: string, data?: unknown, config?: AxiosRequestConfig) {
    return this.client.put<T>(url, data, config)
  }

  public delete<T>(url: string, config?: AxiosRequestConfig) {
    return this.client.delete<T>(url, config)
  }
}

export const apiClient = new ApiClient()
export default apiClient
```

### 6. Constants

```typescript
// src/core/constants.ts
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001/api',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3
}

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100
}

export const POLLING = {
  EVENTS_REFRESH_INTERVAL: Number(import.meta.env.VITE_POLLING_INTERVAL) || 30000,
  AGENTS_REFRESH_INTERVAL: 60000
}

export const APP = {
  TITLE: import.meta.env.VITE_APP_TITLE || 'AWS Monitoring',
  DEBUG: import.meta.env.VITE_ENABLE_DEBUG === 'true'
}
```

### 7. Store Setup

```typescript
// src/store/index.ts
import { createPinia } from 'pinia'

export const pinia = createPinia()
```

```typescript
// src/store/modules/auth.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, AuthToken } from '@/core/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  const login = async (credentials: { email: string; password: string }) => {
    // TODO: Implement actual login logic
    console.log('Login:', credentials)
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    logout
  }
})
```

## Development Workflow

### 1. Start Development Server

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

The application will be available at `http://localhost:3000`

### 2. Development Commands

```bash
# Run tests
npm run test

# Run tests with UI
npm run test:ui

# Generate coverage report
npm run test:coverage

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format

# Type check
npm run type-check
```

### 3. Build for Production

```bash
# Build
npm run build

# Preview production build
npm run preview
```

## Integration with Backend

### Local Development with LocalStack

1. **Start backend services**:
   ```bash
   cd /home/user/aws-monitoring
   make start          # Start LocalStack
   make deploy-local   # Deploy backend stacks
   ```

2. **Configure proxy** (already set in `vite.config.ts`):
   - Frontend runs on `http://localhost:3000`
   - Backend API Gateway on `http://localhost:3001`
   - Vite proxy forwards `/api/*` to backend

3. **Test integration**:
   ```bash
   # Terminal 1: Backend
   make start

   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

## Git Integration

Add to `.gitignore`:

```gitignore
# Frontend specific
frontend/node_modules/
frontend/dist/
frontend/.vite/
frontend/coverage/

# Environment files
frontend/.env.local
frontend/.env.*.local

# Editor
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

## Next Steps

1. **Implement Core Types** - Define all types in `src/core/types/`
2. **Build API Services** - Create API modules in `src/api/modules/`
3. **Create Base Components** - Build UI component library
4. **Implement Features** - Build feature modules (events, agents, reports)
5. **Add Tests** - Write unit and integration tests
6. **Setup CI/CD** - Configure deployment pipeline

## Common Issues and Solutions

### Issue: Path alias `@/` not resolving

**Solution**: Ensure `tsconfig.json` has correct paths configuration and Vite config has alias setup.

### Issue: Tailwind styles not applying

**Solution**:
1. Check `tailwind.config.js` content paths
2. Ensure `main.css` is imported in `main.ts`
3. Run `npx tailwindcss -i ./src/styles/main.css -o ./dist/output.css --watch`

### Issue: Type errors in `.vue` files

**Solution**:
1. Install `vue-tsc`: `npm install -D vue-tsc`
2. Ensure `tsconfig.json` includes `.vue` files
3. Add `/// <reference types="vite/client" />` to `vite-env.d.ts`

### Issue: API calls failing in development

**Solution**:
1. Check Vite proxy configuration
2. Verify backend is running on correct port
3. Check CORS settings on backend API Gateway

## Resources

- [Vue 3 Documentation](https://vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vue Router Documentation](https://router.vuejs.org/)

## Support

For issues or questions:
- Check existing documentation in `docs/` directory
- Review backend integration patterns
- Consult Vue 3 Composition API guide

---

**Ready to start building!** Follow the implementation guide (`frontend-implementation-guide.md`) for detailed examples of building features.

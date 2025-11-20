import { createRouter, createWebHistory } from 'vue-router'
import { ROUTE_NAMES, ROUTE_PATHS } from '@/core/constants'
import { useAuth } from '@/composables/features'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: ROUTE_PATHS.LOGIN,
      name: ROUTE_NAMES.LOGIN,
      component: () => import('@/pages/LoginPage.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: ROUTE_NAMES.DASHBOARD,
          component: () => import('@/pages/DashboardPage.vue')
        },
        {
          path: 'events',
          name: ROUTE_NAMES.EVENTS,
          component: () => import('@/pages/EventsPage.vue')
        },
        {
          path: 'tasks',
          name: ROUTE_NAMES.TASKS,
          component: () => import('@/pages/TasksPage.vue')
        },
        {
          path: 'users',
          name: ROUTE_NAMES.USERS,
          component: () => import('@/pages/UsersPage.vue')
        },
        {
          path: 'configuration',
          name: ROUTE_NAMES.CONFIG,
          component: () => import('@/pages/ConfigurationPage.vue')
        }
      ]
    }
  ]
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const { isAuthenticated } = useAuth()

  if (to.meta.requiresAuth && !isAuthenticated.value) {
    // Redirect to login if route requires auth and user is not authenticated
    next({ name: ROUTE_NAMES.LOGIN })
  } else if (to.name === ROUTE_NAMES.LOGIN && isAuthenticated.value) {
    // Redirect to dashboard if user is authenticated and trying to access login
    next({ name: ROUTE_NAMES.DASHBOARD })
  } else {
    next()
  }
})

export default router

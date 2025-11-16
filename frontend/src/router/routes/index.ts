import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
    meta: {
      requiresAuth: false,
      title: 'Dashboard'
    }
  },
  {
    path: '/events',
    name: 'Events',
    component: () => import('@/pages/Events/EventsListPage.vue'),
    meta: {
      requiresAuth: false,
      title: 'Events'
    }
  },
  {
    path: '/agents',
    name: 'Agents',
    component: () => import('@/pages/Agents/AgentsListPage.vue'),
    meta: {
      requiresAuth: false,
      title: 'Agents'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/ErrorPages/NotFound.vue')
  }
]

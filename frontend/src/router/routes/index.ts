import type { RouteRecordRaw } from 'vue-router';

export const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Auth/LoginPage.vue'),
    meta: {
      requiresAuth: false,
      title: 'Login - AWS Monitoring'
    }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
    meta: {
      requiresAuth: true,
      title: 'Dashboard - AWS Monitoring'
    }
  },
  {
    path: '/events',
    name: 'Events',
    component: () => import('@/pages/Events/EventsListPage.vue'),
    meta: {
      requiresAuth: true,
      title: 'Events - AWS Monitoring'
    }
  },
  {
    path: '/events/:id',
    name: 'EventDetail',
    component: () => import('@/pages/Events/EventDetailPage.vue'),
    meta: {
      requiresAuth: true,
      title: 'Event Details - AWS Monitoring'
    }
  },
  {
    path: '/agents',
    name: 'Agents',
    component: () => import('@/pages/Agents/AgentsListPage.vue'),
    meta: {
      requiresAuth: true,
      title: 'Agents - AWS Monitoring'
    }
  },
  {
    path: '/agents/:account',
    name: 'AgentDetail',
    component: () => import('@/pages/Agents/AgentDetailPage.vue'),
    meta: {
      requiresAuth: true,
      title: 'Agent Details - AWS Monitoring'
    }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/pages/Reports/ReportsPage.vue'),
    meta: {
      requiresAuth: true,
      title: 'Reports - AWS Monitoring'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/ErrorPages/NotFound.vue'),
    meta: {
      title: '404 - Page Not Found'
    }
  }
];

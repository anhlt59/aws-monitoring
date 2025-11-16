import type { Router } from 'vue-router';
import { useAuthStore } from '@/store/modules/auth.store';

export function setupGuards(router: Router) {
  // Authentication guard
  router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();
    const requiresAuth = to.meta.requiresAuth ?? true; // Default to requiring auth

    if (requiresAuth && !authStore.isAuthenticated) {
      // Not authenticated, redirect to login
      next({
        name: 'Login',
        query: { redirect: to.fullPath }
      });
    } else if (to.name === 'Login' && authStore.isAuthenticated) {
      // Already authenticated, redirect to dashboard
      next({ name: 'Dashboard' });
    } else {
      // Proceed
      next();
    }
  });

  // Set page title
  router.afterEach((to) => {
    const title = (to.meta.title as string) || 'AWS Monitoring';
    document.title = title;
  });
}

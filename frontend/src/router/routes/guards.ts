import type { Router } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth.store'

export function setupGuards(router: Router) {
  // Authentication guard
  router.beforeEach((to, _from, next) => {
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

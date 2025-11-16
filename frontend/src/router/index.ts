import { createRouter, createWebHistory } from 'vue-router';
import { routes } from './routes';
import { setupGuards } from './routes/guards';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// Setup navigation guards
setupGuards(router);

export default router;

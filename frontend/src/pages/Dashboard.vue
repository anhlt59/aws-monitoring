<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/modules/auth.store';

const router = useRouter();
const authStore = useAuthStore();

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Navigation Header -->
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16 items-center">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900">
              AWS Monitoring
            </h1>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">
              {{ authStore.user?.email || 'User' }}
            </span>
            <button
              @click="handleLogout"
              class="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Page Header -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900">
          Dashboard
        </h2>
        <p class="mt-1 text-sm text-gray-600">
          Welcome to AWS Monitoring System
        </p>
      </div>

      <!-- Placeholder Content -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Stat Card 1 -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-sm font-medium text-gray-600 mb-1">Critical Events</div>
          <div class="text-3xl font-bold text-red-600">12</div>
        </div>

        <!-- Stat Card 2 -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-sm font-medium text-gray-600 mb-1">High Events</div>
          <div class="text-3xl font-bold text-orange-600">45</div>
        </div>

        <!-- Stat Card 3 -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-sm font-medium text-gray-600 mb-1">Medium Events</div>
          <div class="text-3xl font-bold text-blue-600">128</div>
        </div>

        <!-- Stat Card 4 -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-sm font-medium text-gray-600 mb-1">Low Events</div>
          <div class="text-3xl font-bold text-green-600">234</div>
        </div>
      </div>

      <!-- Navigation Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Events Card -->
        <router-link
          to="/events"
          class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow cursor-pointer"
        >
          <h3 class="text-lg font-semibold text-gray-900 mb-2">
            Events
          </h3>
          <p class="text-sm text-gray-600">
            View and manage monitoring events from all accounts
          </p>
        </router-link>

        <!-- Agents Card -->
        <router-link
          to="/agents"
          class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow cursor-pointer"
        >
          <h3 class="text-lg font-semibold text-gray-900 mb-2">
            Agents
          </h3>
          <p class="text-sm text-gray-600">
            Deploy and manage monitoring agents across AWS accounts
          </p>
        </router-link>

        <!-- Reports Card -->
        <router-link
          to="/reports"
          class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow cursor-pointer"
        >
          <h3 class="text-lg font-semibold text-gray-900 mb-2">
            Reports
          </h3>
          <p class="text-sm text-gray-600">
            Generate and view daily and custom reports
          </p>
        </router-link>
      </div>

      <!-- Status Message -->
      <div class="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p class="text-sm text-blue-800">
          ✅ Frontend application initialized successfully!
          <br />
          <span class="text-xs text-blue-600 mt-1 block">
            This is a placeholder dashboard. Implement the full dashboard as per the design in docs/frontend-screens-design.md
          </span>
        </p>
      </div>
    </main>
  </div>
</template>

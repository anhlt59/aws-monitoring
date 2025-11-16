<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const goHome = () => {
  router.push('/');
};

const goBack = () => {
  router.back();
};
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center px-4">
    <div class="max-w-md w-full text-center">
      <!-- 404 Illustration -->
      <div class="mb-8">
        <svg
          class="mx-auto h-48 w-48 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>

      <!-- Error Message -->
      <h1 class="text-6xl font-bold text-gray-900 mb-4">
        404
      </h1>
      <h2 class="text-2xl font-semibold text-gray-800 mb-2">
        Page Not Found
      </h2>
      <p class="text-gray-600 mb-8">
        Sorry, we couldn't find the page you're looking for. The page might have been moved or deleted.
      </p>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          @click="goHome"
          class="px-6 py-3 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Go to Dashboard
        </button>
        <button
          @click="goBack"
          class="px-6 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Go Back
        </button>
      </div>

      <!-- Quick Links -->
      <div class="mt-12 pt-8 border-t border-gray-200">
        <p class="text-sm text-gray-600 mb-4">
          You might be looking for:
        </p>
        <div class="flex flex-wrap justify-center gap-3">
          <router-link
            to="/"
            class="text-sm text-blue-600 hover:text-blue-700 hover:underline"
          >
            Dashboard
          </router-link>
          <span class="text-gray-400">•</span>
          <router-link
            to="/events"
            class="text-sm text-blue-600 hover:text-blue-700 hover:underline"
          >
            Events
          </router-link>
          <span class="text-gray-400">•</span>
          <router-link
            to="/agents"
            class="text-sm text-blue-600 hover:text-blue-700 hover:underline"
          >
            Agents
          </router-link>
          <span class="text-gray-400">•</span>
          <router-link
            to="/reports"
            class="text-sm text-blue-600 hover:text-blue-700 hover:underline"
          >
            Reports
          </router-link>
        </div>
      </div>

      <!-- Footer -->
      <div class="mt-8">
        <p class="text-xs text-gray-500">
          If you believe this is an error, please contact your administrator.
        </p>
      </div>
    </div>
  </div>
</template>

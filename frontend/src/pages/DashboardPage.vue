<script setup lang="ts">
import { onMounted } from 'vue'
import { useDashboard } from '@/composables/features'
import BaseCard from '@/components/base/BaseCard.vue'
import BaseAlert from '@/components/base/BaseAlert.vue'

const { overview, isLoading, error, fetchOverview } = useDashboard()

onMounted(() => {
  fetchOverview()
})
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
      <p class="mt-2 text-sm text-gray-600">Overview of your AWS monitoring system</p>
    </div>

    <BaseAlert v-if="error" variant="error" dismissible>
      {{ error.message }}
    </BaseAlert>

    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <svg class="animate-spin h-8 w-8 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <div v-else-if="overview" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Events Stats -->
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-primary-100 rounded-lg p-3">
            <span class="text-3xl">⚡</span>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Total Events</dt>
              <dd class="text-3xl font-semibold text-gray-900">{{ overview.events.total }}</dd>
            </dl>
          </div>
        </div>
      </BaseCard>

      <!-- Tasks Stats -->
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-green-100 rounded-lg p-3">
            <span class="text-3xl">✓</span>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Total Tasks</dt>
              <dd class="text-3xl font-semibold text-gray-900">{{ overview.tasks.total }}</dd>
            </dl>
          </div>
        </div>
      </BaseCard>

      <!-- Users Stats -->
      <BaseCard>
        <div class="flex items-center">
          <div class="flex-shrink-0 bg-blue-100 rounded-lg p-3">
            <span class="text-3xl">👥</span>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Active Users</dt>
              <dd class="text-3xl font-semibold text-gray-900">{{ overview.users.active }}</dd>
            </dl>
          </div>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

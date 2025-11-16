<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { computed } from 'vue';

const route = useRoute();
const router = useRouter();

const eventId = computed(() => route.params.id as string);

// Placeholder event data
const event = {
  id: eventId.value,
  account: '123456789012',
  region: 'us-east-1',
  source: 'aws.cloudwatch',
  detail_type: 'CloudWatch Alarm State Change',
  severity: 'Critical',
  resources: [
    'arn:aws:cloudwatch:us-east-1:123456789012:alarm:ServerCpuTooHigh'
  ],
  published_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  detail: {
    alarmName: 'ServerCpuTooHigh',
    state: {
      value: 'ALARM',
      reason: 'Threshold Crossed: CPU utilization exceeded 80%',
      timestamp: new Date().toISOString()
    },
    previousState: {
      value: 'OK',
      reason: 'CPU utilization below threshold',
      timestamp: new Date(Date.now() - 3600000).toISOString()
    }
  }
};

const goBack = () => {
  router.push({ name: 'EventsList' });
};

const getSeverityColor = (severity: string) => {
  const colors: Record<string, string> = {
    'Critical': 'text-red-600 bg-red-100 border-red-200',
    'High': 'text-orange-600 bg-orange-100 border-orange-200',
    'Medium': 'text-blue-600 bg-blue-100 border-blue-200',
    'Low': 'text-green-600 bg-green-100 border-green-200'
  };
  return colors[severity] || 'text-gray-600 bg-gray-100 border-gray-200';
};
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Navigation Header -->
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16 items-center">
          <div class="flex items-center">
            <router-link to="/" class="text-xl font-bold text-gray-900 hover:text-gray-700">
              AWS Monitoring
            </router-link>
          </div>
          <div class="flex items-center space-x-4">
            <router-link to="/events" class="text-sm text-gray-600 hover:text-gray-900">
              Events
            </router-link>
            <router-link to="/" class="text-sm text-gray-600 hover:text-gray-900">
              Dashboard
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Back Button -->
      <button
        @click="goBack"
        class="mb-4 flex items-center text-sm text-gray-600 hover:text-gray-900"
      >
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Back to Events
      </button>

      <!-- Page Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">
              Event Details
            </h1>
            <p class="mt-2 text-sm text-gray-600">
              Event ID: {{ eventId }}
            </p>
          </div>
          <div>
            <span
              :class="[
                'px-4 py-2 text-sm font-medium rounded-full border',
                getSeverityColor(event.severity)
              ]"
            >
              {{ event.severity }}
            </span>
          </div>
        </div>
      </div>

      <!-- Event Information Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main Details -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Overview Card -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              Overview
            </h2>
            <dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <dt class="text-sm font-medium text-gray-500">Event Type</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ event.detail_type }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Source</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ event.source }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Account</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ event.account }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Region</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ event.region }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Published At</dt>
                <dd class="mt-1 text-sm text-gray-900">
                  {{ new Date(event.published_at).toLocaleString() }}
                </dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Updated At</dt>
                <dd class="mt-1 text-sm text-gray-900">
                  {{ new Date(event.updated_at).toLocaleString() }}
                </dd>
              </div>
            </dl>
          </div>

          <!-- Event Detail Card -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              Event Detail
            </h2>
            <div class="space-y-4">
              <div>
                <h3 class="text-sm font-medium text-gray-700 mb-2">Alarm Name</h3>
                <p class="text-sm text-gray-900">{{ event.detail.alarmName }}</p>
              </div>
              <div>
                <h3 class="text-sm font-medium text-gray-700 mb-2">Current State</h3>
                <div class="bg-red-50 border border-red-200 rounded p-3">
                  <p class="text-sm font-medium text-red-900">{{ event.detail.state.value }}</p>
                  <p class="text-sm text-red-700 mt-1">{{ event.detail.state.reason }}</p>
                  <p class="text-xs text-red-600 mt-1">
                    {{ new Date(event.detail.state.timestamp).toLocaleString() }}
                  </p>
                </div>
              </div>
              <div>
                <h3 class="text-sm font-medium text-gray-700 mb-2">Previous State</h3>
                <div class="bg-green-50 border border-green-200 rounded p-3">
                  <p class="text-sm font-medium text-green-900">{{ event.detail.previousState.value }}</p>
                  <p class="text-sm text-green-700 mt-1">{{ event.detail.previousState.reason }}</p>
                  <p class="text-xs text-green-600 mt-1">
                    {{ new Date(event.detail.previousState.timestamp).toLocaleString() }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Raw JSON Card -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              Raw Event Data
            </h2>
            <pre class="bg-gray-50 rounded p-4 text-xs overflow-x-auto">{{ JSON.stringify(event.detail, null, 2) }}</pre>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="lg:col-span-1 space-y-6">
          <!-- Resources Card -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              Affected Resources
            </h2>
            <ul class="space-y-2">
              <li
                v-for="(resource, index) in event.resources"
                :key="index"
                class="text-sm text-gray-900 bg-gray-50 rounded p-2 break-all"
              >
                {{ resource }}
              </li>
            </ul>
          </div>

          <!-- Actions Card -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              Actions
            </h2>
            <div class="space-y-2">
              <button
                class="w-full px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                View in CloudWatch
              </button>
              <button
                class="w-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Export Event
              </button>
              <button
                class="w-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Create Incident
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Message -->
      <div class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p class="text-sm text-blue-800">
          📝 This is a placeholder Event Detail page with mock data.
          <br />
          <span class="text-xs text-blue-600 mt-1 block">
            Implement full functionality as per docs/frontend-screens-design.md
          </span>
        </p>
      </div>
    </main>
  </div>
</template>

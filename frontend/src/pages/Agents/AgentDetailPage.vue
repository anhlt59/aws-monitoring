<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { computed, ref } from 'vue';

const route = useRoute();
const router = useRouter();

const accountId = computed(() => route.params.account as string);

// Placeholder agent data
const agent = ref({
  account: accountId.value,
  region: 'us-east-1',
  status: 'CREATE_COMPLETE',
  deployed_at: new Date(Date.now() - 86400000).toISOString(),
  created_at: new Date(Date.now() - 172800000).toISOString(),
  stack_id: 'arn:aws:cloudformation:us-east-1:123456789012:stack/monitoring-agent/12345678',
  last_heartbeat: new Date(Date.now() - 300000).toISOString()
});

// Placeholder metrics
const metrics = ref({
  eventsPublished: 1234,
  errorsDetected: 45,
  lastQueryTime: new Date(Date.now() - 300000).toISOString(),
  averageQueryDuration: 2.5
});

// Placeholder recent events
const recentEvents = ref([
  {
    id: '1',
    severity: 'High',
    detail_type: 'Lambda Error',
    published_at: new Date(Date.now() - 1800000).toISOString()
  },
  {
    id: '2',
    severity: 'Medium',
    detail_type: 'ECS Task Failure',
    published_at: new Date(Date.now() - 3600000).toISOString()
  },
  {
    id: '3',
    severity: 'Critical',
    detail_type: 'CloudWatch Alarm',
    published_at: new Date(Date.now() - 7200000).toISOString()
  }
]);

const goBack = () => {
  router.push({ name: 'Agents' });
};

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    'CREATE_COMPLETE': 'text-green-600 bg-green-100 border-green-200',
    'UPDATE_COMPLETE': 'text-green-600 bg-green-100 border-green-200',
    'CREATE_IN_PROGRESS': 'text-blue-600 bg-blue-100 border-blue-200',
    'UPDATE_IN_PROGRESS': 'text-blue-600 bg-blue-100 border-blue-200',
    'CREATE_FAILED': 'text-red-600 bg-red-100 border-red-200',
    'UPDATE_FAILED': 'text-red-600 bg-red-100 border-red-200'
  };
  return colors[status] || 'text-gray-600 bg-gray-100 border-gray-200';
};

const getSeverityColor = (severity: string) => {
  const colors: Record<string, string> = {
    'Critical': 'text-red-600 bg-red-100',
    'High': 'text-orange-600 bg-orange-100',
    'Medium': 'text-blue-600 bg-blue-100',
    'Low': 'text-green-600 bg-green-100'
  };
  return colors[severity] || 'text-gray-600 bg-gray-100';
};

const updateAgent = () => {
  // TODO: Implement update logic
  console.log('Updating agent:', accountId.value);
};

const deleteAgent = () => {
  // TODO: Implement delete logic
  console.log('Deleting agent:', accountId.value);
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
            <router-link to="/agents" class="text-sm text-gray-600 hover:text-gray-900">
              Agents
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
        Back to Agents
      </button>

      <!-- Page Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">
              Agent Details
            </h1>
            <p class="mt-2 text-sm text-gray-600">
              Account: {{ accountId }}
            </p>
          </div>
          <div>
            <span
              :class="[
                'px-4 py-2 text-sm font-medium rounded-full border',
                getStatusColor(agent.status)
              ]"
            >
              {{ agent.status.replace(/_/g, ' ') }}
            </span>
          </div>
        </div>
      </div>

      <!-- Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Overview Card -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              Overview
            </h2>
            <dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <dt class="text-sm font-medium text-gray-500">Account ID</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ agent.account }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Region</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ agent.region }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Status</dt>
                <dd class="mt-1 text-sm text-gray-900">{{ agent.status.replace(/_/g, ' ') }}</dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Last Heartbeat</dt>
                <dd class="mt-1 text-sm text-gray-900">
                  {{ new Date(agent.last_heartbeat).toLocaleString() }}
                </dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Deployed At</dt>
                <dd class="mt-1 text-sm text-gray-900">
                  {{ new Date(agent.deployed_at).toLocaleString() }}
                </dd>
              </div>
              <div>
                <dt class="text-sm font-medium text-gray-500">Created At</dt>
                <dd class="mt-1 text-sm text-gray-900">
                  {{ new Date(agent.created_at).toLocaleString() }}
                </dd>
              </div>
              <div class="md:col-span-2">
                <dt class="text-sm font-medium text-gray-500">Stack ID</dt>
                <dd class="mt-1 text-sm text-gray-900 break-all">{{ agent.stack_id }}</dd>
              </div>
            </dl>
          </div>

          <!-- Metrics Card -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              Metrics
            </h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div class="text-center">
                <div class="text-3xl font-bold text-blue-600">
                  {{ metrics.eventsPublished }}
                </div>
                <div class="text-sm text-gray-500 mt-1">
                  Events Published
                </div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-orange-600">
                  {{ metrics.errorsDetected }}
                </div>
                <div class="text-sm text-gray-500 mt-1">
                  Errors Detected
                </div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-green-600">
                  {{ metrics.averageQueryDuration.toFixed(1) }}s
                </div>
                <div class="text-sm text-gray-500 mt-1">
                  Avg Query Time
                </div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-purple-600">
                  5m
                </div>
                <div class="text-sm text-gray-500 mt-1">
                  Last Query
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Events Card -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              Recent Events
            </h2>
            <div class="space-y-3">
              <div
                v-for="event in recentEvents"
                :key="event.id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded hover:bg-gray-100 cursor-pointer"
                @click="router.push({ name: 'EventDetail', params: { id: event.id } })"
              >
                <div class="flex items-center space-x-3">
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-medium rounded-full',
                      getSeverityColor(event.severity)
                    ]"
                  >
                    {{ event.severity }}
                  </span>
                  <span class="text-sm text-gray-900">{{ event.detail_type }}</span>
                </div>
                <span class="text-xs text-gray-500">
                  {{ new Date(event.published_at).toLocaleString() }}
                </span>
              </div>
            </div>
            <div class="mt-4 text-center">
              <router-link
                to="/events"
                class="text-sm text-blue-600 hover:text-blue-700"
              >
                View all events →
              </router-link>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="lg:col-span-1 space-y-6">
          <!-- Health Status Card -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              Health Status
            </h2>
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Agent Running</span>
                <span class="flex items-center text-sm text-green-600">
                  <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  Healthy
                </span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Query Execution</span>
                <span class="flex items-center text-sm text-green-600">
                  <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  OK
                </span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">Event Publishing</span>
                <span class="flex items-center text-sm text-green-600">
                  <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  OK
                </span>
              </div>
            </div>
          </div>

          <!-- Actions Card -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              Actions
            </h2>
            <div class="space-y-2">
              <button
                @click="updateAgent"
                class="w-full px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                Update Agent
              </button>
              <button
                class="w-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                View CloudWatch Logs
              </button>
              <button
                class="w-full px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                View CloudFormation Stack
              </button>
              <button
                @click="deleteAgent"
                class="w-full px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
              >
                Delete Agent
              </button>
            </div>
          </div>

          <!-- Configuration Card -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
              Configuration
            </h2>
            <dl class="space-y-2">
              <div>
                <dt class="text-xs text-gray-500">Query Interval</dt>
                <dd class="text-sm text-gray-900">5 minutes</dd>
              </div>
              <div>
                <dt class="text-xs text-gray-500">Query Duration</dt>
                <dd class="text-sm text-gray-900">5 minutes</dd>
              </div>
              <div>
                <dt class="text-xs text-gray-500">Chunk Size</dt>
                <dd class="text-sm text-gray-900">10 log groups</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      <!-- Status Message -->
      <div class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p class="text-sm text-blue-800">
          📝 This is a placeholder Agent Detail page with mock data.
          <br />
          <span class="text-xs text-blue-600 mt-1 block">
            Implement full functionality as per docs/frontend-screens-design.md
          </span>
        </p>
      </div>
    </main>
  </div>
</template>

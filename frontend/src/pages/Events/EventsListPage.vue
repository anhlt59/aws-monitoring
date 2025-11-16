<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

// Placeholder data
const mockEvents = [
  {
    id: '1',
    account: '123456789012',
    region: 'us-east-1',
    severity: 'Critical',
    detail_type: 'CloudWatch Alarm State Change',
    source: 'aws.cloudwatch',
    published_at: new Date().toISOString()
  },
  {
    id: '2',
    account: '123456789012',
    region: 'us-west-2',
    severity: 'High',
    detail_type: 'Lambda Error',
    source: 'aws.lambda',
    published_at: new Date().toISOString()
  },
  {
    id: '3',
    account: '987654321098',
    region: 'us-east-1',
    severity: 'Medium',
    detail_type: 'ECS Task Failure',
    source: 'aws.ecs',
    published_at: new Date().toISOString()
  }
];

const viewEventDetail = (eventId: string) => {
  router.push({ name: 'EventDetail', params: { id: eventId } });
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
            <router-link to="/" class="text-sm text-gray-600 hover:text-gray-900">
              Dashboard
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">
          Monitoring Events
        </h1>
        <p class="mt-2 text-sm text-gray-600">
          View and filter events from all monitored accounts
        </p>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-lg shadow mb-6 p-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Account
            </label>
            <select class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
              <option>All Accounts</option>
              <option>123456789012</option>
              <option>987654321098</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Region
            </label>
            <select class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
              <option>All Regions</option>
              <option>us-east-1</option>
              <option>us-west-2</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Severity
            </label>
            <select class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
              <option>All Severities</option>
              <option>Critical</option>
              <option>High</option>
              <option>Medium</option>
              <option>Low</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Source
            </label>
            <select class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
              <option>All Sources</option>
              <option>aws.cloudwatch</option>
              <option>aws.lambda</option>
              <option>aws.ecs</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Events Table -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Severity
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Account
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Region
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Source
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Time
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="event in mockEvents"
              :key="event.id"
              class="hover:bg-gray-50 cursor-pointer"
              @click="viewEventDetail(event.id)"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded-full',
                    getSeverityColor(event.severity)
                  ]"
                >
                  {{ event.severity }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ event.account }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ event.region }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-900">
                {{ event.detail_type }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ event.source }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ new Date(event.published_at).toLocaleString() }}
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Pagination -->
        <div class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-700">
              Showing <span class="font-medium">1</span> to <span class="font-medium">3</span> of{' '}
              <span class="font-medium">3</span> events
            </div>
            <div class="flex space-x-2">
              <button
                disabled
                class="px-3 py-1 text-sm border rounded-md text-gray-400 bg-gray-100 cursor-not-allowed"
              >
                Previous
              </button>
              <button
                disabled
                class="px-3 py-1 text-sm border rounded-md text-gray-400 bg-gray-100 cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Message -->
      <div class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p class="text-sm text-blue-800">
          📝 This is a placeholder Events List page with mock data.
          <br />
          <span class="text-xs text-blue-600 mt-1 block">
            Implement full functionality as per docs/frontend-screens-design.md
          </span>
        </p>
      </div>
    </main>
  </div>
</template>

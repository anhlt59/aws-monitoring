<script setup lang="ts">
import { ref } from 'vue';

// Placeholder report data
const reportSummary = ref({
  date: new Date().toISOString().split('T')[0],
  totalEvents: 419,
  criticalEvents: 12,
  highEvents: 45,
  mediumEvents: 128,
  lowEvents: 234,
  affectedAccounts: 3,
  activeAgents: 3
});

const eventsByAccount = ref([
  { account: '123456789012', region: 'us-east-1', eventCount: 215, criticalCount: 8 },
  { account: '987654321098', region: 'us-west-2', eventCount: 142, criticalCount: 3 },
  { account: '555555555555', region: 'us-east-1', eventCount: 62, criticalCount: 1 }
]);

const eventsBySeverity = ref([
  { severity: 'Critical', count: 12, percentage: 2.9 },
  { severity: 'High', count: 45, percentage: 10.7 },
  { severity: 'Medium', count: 128, percentage: 30.5 },
  { severity: 'Low', count: 234, percentage: 55.9 }
]);

const topErrors = ref([
  {
    errorType: 'Lambda Timeout',
    count: 23,
    affectedResources: ['function-1', 'function-2'],
    firstOccurrence: new Date(Date.now() - 86400000).toISOString()
  },
  {
    errorType: 'ECS Task Failed',
    count: 15,
    affectedResources: ['service-a', 'service-b'],
    firstOccurrence: new Date(Date.now() - 172800000).toISOString()
  },
  {
    errorType: 'CloudWatch Alarm',
    count: 12,
    affectedResources: ['ServerCpuHigh', 'DatabaseMemory'],
    firstOccurrence: new Date(Date.now() - 259200000).toISOString()
  }
]);

const dateRange = ref({
  start: new Date(Date.now() - 86400000).toISOString().split('T')[0],
  end: new Date().toISOString().split('T')[0]
});

const generateReport = () => {
  // TODO: Implement report generation logic
  console.log('Generating report for:', dateRange.value);
};

const exportReport = (format: string) => {
  // TODO: Implement export logic
  console.log('Exporting report as:', format);
};

const getSeverityColor = (severity: string) => {
  const colors: Record<string, string> = {
    'Critical': 'bg-red-500',
    'High': 'bg-orange-500',
    'Medium': 'bg-blue-500',
    'Low': 'bg-green-500'
  };
  return colors[severity] || 'bg-gray-500';
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
          Monitoring Reports
        </h1>
        <p class="mt-2 text-sm text-gray-600">
          Generate and view daily and custom reports
        </p>
      </div>

      <!-- Date Range Selector -->
      <div class="bg-white rounded-lg shadow p-4 mb-6">
        <div class="flex flex-wrap items-end gap-4">
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Start Date
            </label>
            <input
              v-model="dateRange.start"
              type="date"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div class="flex-1 min-w-[200px]">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              End Date
            </label>
            <input
              v-model="dateRange.end"
              type="date"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div>
            <button
              @click="generateReport"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              Generate Report
            </button>
          </div>
          <div>
            <button
              @click="exportReport('pdf')"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Export PDF
            </button>
          </div>
        </div>
      </div>

      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-sm font-medium text-gray-600 mb-1">Total Events</div>
          <div class="text-3xl font-bold text-gray-900">{{ reportSummary.totalEvents }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-sm font-medium text-gray-600 mb-1">Critical Events</div>
          <div class="text-3xl font-bold text-red-600">{{ reportSummary.criticalEvents }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-sm font-medium text-gray-600 mb-1">Affected Accounts</div>
          <div class="text-3xl font-bold text-blue-600">{{ reportSummary.affectedAccounts }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
          <div class="text-sm font-medium text-gray-600 mb-1">Active Agents</div>
          <div class="text-3xl font-bold text-green-600">{{ reportSummary.activeAgents }}</div>
        </div>
      </div>

      <!-- Report Content Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Events by Account -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">
            Events by Account
          </h2>
          <div class="space-y-3">
            <div
              v-for="item in eventsByAccount"
              :key="`${item.account}-${item.region}`"
              class="flex items-center justify-between p-3 bg-gray-50 rounded"
            >
              <div>
                <div class="text-sm font-medium text-gray-900">{{ item.account }}</div>
                <div class="text-xs text-gray-500">{{ item.region }}</div>
              </div>
              <div class="text-right">
                <div class="text-sm font-semibold text-gray-900">{{ item.eventCount }} events</div>
                <div class="text-xs text-red-600">{{ item.criticalCount }} critical</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Events by Severity -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">
            Events by Severity
          </h2>
          <div class="space-y-4">
            <div
              v-for="item in eventsBySeverity"
              :key="item.severity"
            >
              <div class="flex items-center justify-between mb-1">
                <span class="text-sm font-medium text-gray-900">{{ item.severity }}</span>
                <span class="text-sm text-gray-600">{{ item.count }} ({{ item.percentage }}%)</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  :class="['h-2 rounded-full', getSeverityColor(item.severity)]"
                  :style="{ width: `${item.percentage}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Errors -->
        <div class="bg-white rounded-lg shadow p-6 lg:col-span-2">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">
            Top Error Types
          </h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Error Type
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Count
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Affected Resources
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    First Occurrence
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="error in topErrors" :key="error.errorType">
                  <td class="px-4 py-3 text-sm text-gray-900">
                    {{ error.errorType }}
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-900">
                    {{ error.count }}
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">
                    {{ error.affectedResources.join(', ') }}
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-500">
                    {{ new Date(error.firstOccurrence).toLocaleDateString() }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Chart Placeholder -->
        <div class="bg-white rounded-lg shadow p-6 lg:col-span-2">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">
            Events Over Time
          </h2>
          <div class="h-64 flex items-center justify-center bg-gray-50 rounded border-2 border-dashed border-gray-300">
            <div class="text-center">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <p class="mt-2 text-sm text-gray-500">
                Chart visualization will be implemented here
              </p>
              <p class="text-xs text-gray-400 mt-1">
                Consider using Chart.js or ApexCharts
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Message -->
      <div class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p class="text-sm text-blue-800">
          📝 This is a placeholder Reports page with mock data.
          <br />
          <span class="text-xs text-blue-600 mt-1 block">
            Implement full functionality as per docs/frontend-screens-design.md
          </span>
        </p>
      </div>
    </main>
  </div>
</template>

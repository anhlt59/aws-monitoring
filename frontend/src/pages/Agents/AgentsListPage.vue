<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Placeholder data
const agents = ref([
  {
    account: '123456789012',
    region: 'us-east-1',
    status: 'CREATE_COMPLETE',
    deployed_at: new Date(Date.now() - 86400000).toISOString(),
    created_at: new Date(Date.now() - 172800000).toISOString()
  },
  {
    account: '987654321098',
    region: 'us-west-2',
    status: 'CREATE_COMPLETE',
    deployed_at: new Date(Date.now() - 172800000).toISOString(),
    created_at: new Date(Date.now() - 259200000).toISOString()
  },
  {
    account: '555555555555',
    region: 'us-east-1',
    status: 'UPDATE_IN_PROGRESS',
    deployed_at: new Date(Date.now() - 3600000).toISOString(),
    created_at: new Date(Date.now() - 345600000).toISOString()
  }
]);

const showDeployModal = ref(false);
const deployForm = ref({
  account: '',
  region: ''
});

const viewAgentDetail = (account: string) => {
  router.push({ name: 'AgentDetail', params: { account } });
};

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    'CREATE_COMPLETE': 'text-green-600 bg-green-100',
    'UPDATE_COMPLETE': 'text-green-600 bg-green-100',
    'CREATE_IN_PROGRESS': 'text-blue-600 bg-blue-100',
    'UPDATE_IN_PROGRESS': 'text-blue-600 bg-blue-100',
    'CREATE_FAILED': 'text-red-600 bg-red-100',
    'UPDATE_FAILED': 'text-red-600 bg-red-100',
    'DELETE_IN_PROGRESS': 'text-orange-600 bg-orange-100'
  };
  return colors[status] || 'text-gray-600 bg-gray-100';
};

const openDeployModal = () => {
  showDeployModal.value = true;
};

const closeDeployModal = () => {
  showDeployModal.value = false;
  deployForm.value = { account: '', region: '' };
};

const deployAgent = () => {
  // TODO: Implement actual deployment logic
  console.log('Deploying agent:', deployForm.value);
  closeDeployModal();
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
      <div class="mb-8 flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">
            Monitoring Agents
          </h1>
          <p class="mt-2 text-sm text-gray-600">
            Deploy and manage monitoring agents across AWS accounts
          </p>
        </div>
        <button
          @click="openDeployModal"
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
        >
          Deploy New Agent
        </button>
      </div>

      <!-- Agents Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="agent in agents"
          :key="`${agent.account}-${agent.region}`"
          class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
          @click="viewAgentDetail(agent.account)"
        >
          <div class="p-6">
            <!-- Status Badge -->
            <div class="flex justify-between items-start mb-4">
              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900">
                  {{ agent.account }}
                </h3>
                <p class="text-sm text-gray-500 mt-1">
                  {{ agent.region }}
                </p>
              </div>
              <span
                :class="[
                  'px-2 py-1 text-xs font-medium rounded-full',
                  getStatusColor(agent.status)
                ]"
              >
                {{ agent.status.replace(/_/g, ' ') }}
              </span>
            </div>

            <!-- Agent Info -->
            <dl class="space-y-2">
              <div>
                <dt class="text-xs text-gray-500">Deployed At</dt>
                <dd class="text-sm text-gray-900">
                  {{ new Date(agent.deployed_at).toLocaleString() }}
                </dd>
              </div>
              <div>
                <dt class="text-xs text-gray-500">Created At</dt>
                <dd class="text-sm text-gray-900">
                  {{ new Date(agent.created_at).toLocaleString() }}
                </dd>
              </div>
            </dl>

            <!-- Quick Actions -->
            <div class="mt-4 pt-4 border-t border-gray-200 flex space-x-2">
              <button
                class="flex-1 px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-50 rounded hover:bg-gray-100"
                @click.stop
              >
                View Logs
              </button>
              <button
                class="flex-1 px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-50 rounded hover:bg-gray-100"
                @click.stop
              >
                Update
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State (hidden when agents exist) -->
      <div v-if="agents.length === 0" class="text-center py-12">
        <svg
          class="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">No agents deployed</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by deploying a new monitoring agent.</p>
        <div class="mt-6">
          <button
            @click="openDeployModal"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Deploy Agent
          </button>
        </div>
      </div>

      <!-- Status Message -->
      <div class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p class="text-sm text-blue-800">
          📝 This is a placeholder Agents List page with mock data.
          <br />
          <span class="text-xs text-blue-600 mt-1 block">
            Implement full functionality as per docs/frontend-screens-design.md
          </span>
        </p>
      </div>
    </main>

    <!-- Deploy Modal -->
    <div
      v-if="showDeployModal"
      class="fixed inset-0 z-50 overflow-y-auto"
      aria-labelledby="modal-title"
      role="dialog"
      aria-modal="true"
    >
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div
          class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          @click="closeDeployModal"
        ></div>

        <!-- Modal panel -->
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg font-medium text-gray-900 mb-4">
              Deploy New Agent
            </h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  AWS Account ID
                </label>
                <input
                  v-model="deployForm.account"
                  type="text"
                  placeholder="123456789012"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Region
                </label>
                <select
                  v-model="deployForm.region"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="">Select a region</option>
                  <option value="us-east-1">US East (N. Virginia)</option>
                  <option value="us-east-2">US East (Ohio)</option>
                  <option value="us-west-1">US West (N. California)</option>
                  <option value="us-west-2">US West (Oregon)</option>
                  <option value="eu-west-1">EU (Ireland)</option>
                  <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                </select>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="button"
              @click="deployAgent"
              :disabled="!deployForm.account || !deployForm.region"
              class="w-full sm:w-auto sm:ml-3 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Deploy
            </button>
            <button
              type="button"
              @click="closeDeployModal"
              class="mt-3 w-full sm:mt-0 sm:w-auto px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

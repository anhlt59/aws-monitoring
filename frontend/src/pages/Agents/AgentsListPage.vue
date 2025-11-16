<script setup lang="ts">
import { ref } from 'vue'

const agents = ref([])
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-6">Agents</h1>

      <div class="bg-white rounded-lg shadow-md p-6">
        <p class="text-gray-600">
          {{ agents.length === 0 ? 'No agents found' : `${agents.length} agents` }}
        </p>
        <p class="text-sm text-gray-500 mt-2">
          Agent list will be implemented here
        </p>
      </div>

      <div class="mt-4">
        <router-link
          to="/"
          class="text-blue-600 hover:text-blue-800 underline"
        >
          Back to Dashboard
        </router-link>
      </div>
    </div>
  </div>
</template>

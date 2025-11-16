<script setup lang="ts">
import { ref } from 'vue'

const message = ref('Welcome to AWS Monitoring Dashboard')
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">{{ message }}</h1>
      <p class="text-lg text-gray-600 mb-8">
        Monitor your AWS resources across multiple accounts
      </p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <router-link
          to="/events"
          class="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow"
        >
          <h2 class="text-2xl font-semibold text-gray-900 mb-2">Events</h2>
          <p class="text-gray-600">View and manage monitoring events</p>
        </router-link>

        <router-link
          to="/agents"
          class="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow"
        >
          <h2 class="text-2xl font-semibold text-gray-900 mb-2">Agents</h2>
          <p class="text-gray-600">Manage monitoring agents</p>
        </router-link>
      </div>
    </div>
  </div>
</template>

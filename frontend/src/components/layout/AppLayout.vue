<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/features'
import { ROUTE_NAMES } from '@/core/constants'

const router = useRouter()
const { user, logout } = useAuth()

const isSidebarOpen = ref(true)

const navigation = [
  { name: 'Dashboard', icon: '📊', route: ROUTE_NAMES.DASHBOARD },
  { name: 'Events', icon: '⚡', route: ROUTE_NAMES.EVENTS },
  { name: 'Tasks', icon: '✓', route: ROUTE_NAMES.TASKS },
  { name: 'Users', icon: '👥', route: ROUTE_NAMES.USERS },
  { name: 'Configuration', icon: '⚙️', route: ROUTE_NAMES.CONFIG }
]

const handleLogout = async () => {
  await logout()
  router.push({ name: ROUTE_NAMES.LOGIN })
}
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-200 ease-in-out',
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <div class="flex flex-col h-full">
        <!-- Logo -->
        <div class="flex items-center justify-between h-16 px-6 border-b">
          <h1 class="text-xl font-bold text-primary-600">AWS Monitoring</h1>
          <button @click="isSidebarOpen = false" class="lg:hidden">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          <router-link
            v-for="item in navigation"
            :key="item.name"
            :to="{ name: item.route }"
            class="flex items-center px-4 py-3 text-gray-700 rounded-lg hover:bg-primary-50 hover:text-primary-700 transition-colors"
            active-class="bg-primary-100 text-primary-700 font-medium"
          >
            <span class="text-xl mr-3">{{ item.icon }}</span>
            {{ item.name }}
          </router-link>
        </nav>

        <!-- User menu -->
        <div class="p-4 border-t">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center">
              <div class="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white font-medium">
                {{ user?.full_name?.charAt(0) || 'U' }}
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-900">{{ user?.full_name }}</p>
                <p class="text-xs text-gray-500">{{ user?.role }}</p>
              </div>
            </div>
          </div>
          <button
            @click="handleLogout"
            class="w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <div :class="['transition-all duration-200', isSidebarOpen ? 'lg:ml-64' : '']">
      <!-- Top header -->
      <header class="h-16 bg-white shadow-sm">
        <div class="flex items-center justify-between h-full px-6">
          <button
            @click="isSidebarOpen = !isSidebarOpen"
            class="text-gray-500 hover:text-gray-700 focus:outline-none"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-600">{{ new Date().toLocaleDateString() }}</span>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

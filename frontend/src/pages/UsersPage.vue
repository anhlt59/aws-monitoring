<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUsers } from '@/composables/features'
import { useFormatDate } from '@/composables/utils/useFormatDate'
import { ROUTE_NAMES } from '@/core/constants'
import BaseCard from '@/components/base/BaseCard.vue'
import BaseTable from '@/components/base/BaseTable.vue'
import BaseAlert from '@/components/base/BaseAlert.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseBadge from '@/components/base/BaseBadge.vue'
import BasePagination from '@/components/base/BasePagination.vue'
import type { User } from '@/core/types'

const router = useRouter()
const { users, isLoading, error, fetchUsers, totalUsers, currentPage, pageSize, hasMore, nextPage, previousPage } = useUsers()
const { formatDate } = useFormatDate()

const columns = [
  { key: 'full_name', label: 'Name', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
  { key: 'role', label: 'Role', width: '120px' },
  { key: 'is_active', label: 'Status', width: '100px' },
  { key: 'created_at', label: 'Created', width: '180px', sortable: true }
]

const handleRowClick = (user: User) => {
  // Navigate to user detail page when implemented
  console.log('User clicked:', user)
}

const handleCreateUser = () => {
  router.push({ name: ROUTE_NAMES.USER_CREATE })
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Users</h1>
        <p class="mt-2 text-sm text-gray-600">Manage user accounts and permissions</p>
      </div>
      <BaseButton @click="handleCreateUser">
        Create User
      </BaseButton>
    </div>

    <BaseAlert v-if="error" variant="error" dismissible>
      {{ error.message }}
    </BaseAlert>

    <BaseCard :padding="false">
      <BaseTable
        :columns="columns"
        :data="users"
        :is-loading="isLoading"
        empty-message="No users found"
        @row-click="handleRowClick"
      >
        <!-- Custom cell: Role -->
        <template #cell-role="{ value }">
          <BaseBadge variant="info">{{ value }}</BaseBadge>
        </template>

        <!-- Custom cell: Status -->
        <template #cell-is_active="{ value }">
          <BaseBadge :variant="value ? 'success' : 'neutral'">
            {{ value ? 'Active' : 'Inactive' }}
          </BaseBadge>
        </template>

        <!-- Custom cell: Created At -->
        <template #cell-created_at="{ value }">
          {{ formatDate(value) }}
        </template>
      </BaseTable>

      <BasePagination
        :current-page="currentPage"
        :total-items="totalUsers"
        :page-size="pageSize"
        :has-more="hasMore"
        @previous="previousPage"
        @next="nextPage"
      />
    </BaseCard>
  </div>
</template>

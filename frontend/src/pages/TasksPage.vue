<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTasks } from '@/composables/features'
import { useFormatDate } from '@/composables/utils/useFormatDate'
import { ROUTE_NAMES } from '@/core/constants'
import BaseCard from '@/components/base/BaseCard.vue'
import BaseTable from '@/components/base/BaseTable.vue'
import BaseAlert from '@/components/base/BaseAlert.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import BasePagination from '@/components/base/BasePagination.vue'
import TaskStatusBadge from '@/components/modules/TaskStatusBadge.vue'
import TaskPriorityBadge from '@/components/modules/TaskPriorityBadge.vue'
import type { Task } from '@/core/types'

const router = useRouter()
const { tasks, isLoading, error, fetchTasks, totalTasks, currentPage, pageSize, hasMore, nextPage, previousPage } = useTasks()
const { formatDate } = useFormatDate()

const columns = [
  { key: 'title', label: 'Title', sortable: true },
  { key: 'status', label: 'Status', width: '120px' },
  { key: 'priority', label: 'Priority', width: '120px' },
  { key: 'assigned_user_name', label: 'Assigned To', width: '150px' },
  { key: 'created_at', label: 'Created', width: '180px', sortable: true }
]

const handleRowClick = (task: Task) => {
  // Navigate to task detail page when implemented
  console.log('Task clicked:', task)
}

const handleCreateTask = () => {
  router.push({ name: ROUTE_NAMES.TASK_CREATE })
}

onMounted(() => {
  fetchTasks()
})
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Tasks</h1>
        <p class="mt-2 text-sm text-gray-600">Manage tasks and assignments</p>
      </div>
      <BaseButton @click="handleCreateTask">
        Create Task
      </BaseButton>
    </div>

    <BaseAlert v-if="error" variant="error" dismissible>
      {{ error.message }}
    </BaseAlert>

    <BaseCard :padding="false">
      <BaseTable
        :columns="columns"
        :data="tasks"
        :is-loading="isLoading"
        empty-message="No tasks found"
        @row-click="handleRowClick"
      >
        <!-- Custom cell: Status -->
        <template #cell-status="{ row }">
          <TaskStatusBadge :status="row.status" />
        </template>

        <!-- Custom cell: Priority -->
        <template #cell-priority="{ row }">
          <TaskPriorityBadge :priority="row.priority" />
        </template>

        <!-- Custom cell: Created At -->
        <template #cell-created_at="{ value }">
          {{ formatDate(value) }}
        </template>
      </BaseTable>

      <BasePagination
        :current-page="currentPage"
        :total-items="totalTasks"
        :page-size="pageSize"
        :has-more="hasMore"
        @previous="previousPage"
        @next="nextPage"
      />
    </BaseCard>
  </div>
</template>

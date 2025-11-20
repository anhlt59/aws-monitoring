<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useEvents } from '@/composables/features'
import { useFormatDate } from '@/composables/utils/useFormatDate'
import BaseCard from '@/components/base/BaseCard.vue'
import BaseTable from '@/components/base/BaseTable.vue'
import BaseAlert from '@/components/base/BaseAlert.vue'
import BasePagination from '@/components/base/BasePagination.vue'
import SeverityBadge from '@/components/modules/SeverityBadge.vue'
import type { Event } from '@/core/types'

const router = useRouter()
const { events, isLoading, error, fetchEvents, totalEvents, currentPage, pageSize, hasMore, nextPage, previousPage } = useEvents()
const { formatDate } = useFormatDate()

const columns = [
  { key: 'severity', label: 'Severity', width: '120px' },
  { key: 'account', label: 'Account', width: '150px' },
  { key: 'region', label: 'Region', width: '120px' },
  { key: 'detail_type', label: 'Type', sortable: true },
  { key: 'source', label: 'Source', sortable: true },
  { key: 'published_at', label: 'Time', width: '180px', sortable: true }
]

const handleRowClick = (event: Event) => {
  // Navigate to event detail page when implemented
  console.log('Event clicked:', event)
}

onMounted(() => {
  fetchEvents()
})
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Monitoring Events</h1>
      <p class="mt-2 text-sm text-gray-600">View and filter events from all monitored accounts</p>
    </div>

    <BaseAlert v-if="error" variant="error" dismissible>
      {{ error.message }}
    </BaseAlert>

    <BaseCard :padding="false">
      <BaseTable
        :columns="columns"
        :data="events"
        :is-loading="isLoading"
        empty-message="No events found"
        @row-click="handleRowClick"
      >
        <!-- Custom cell: Severity -->
        <template #cell-severity="{ row }">
          <SeverityBadge :severity="row.severity" />
        </template>

        <!-- Custom cell: Published At -->
        <template #cell-published_at="{ value }">
          {{ formatDate(value) }}
        </template>
      </BaseTable>

      <BasePagination
        :current-page="currentPage"
        :total-items="totalEvents"
        :page-size="pageSize"
        :has-more="hasMore"
        @previous="previousPage"
        @next="nextPage"
      />
    </BaseCard>
  </div>
</template>

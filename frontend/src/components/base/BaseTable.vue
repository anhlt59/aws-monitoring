<script setup lang="ts" generic="T extends Record<string, any>">
interface Column {
  key: string
  label: string
  sortable?: boolean
  width?: string
}

interface Props {
  columns: Column[]
  data: T[]
  isLoading?: boolean
  emptyMessage?: string
}

interface Emits {
  (e: 'row-click', row: T): void
  (e: 'sort', column: string): void
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  emptyMessage: 'No data available'
})

const emit = defineEmits<Emits>()

const handleRowClick = (row: T) => {
  emit('row-click', row)
}

const handleSort = (column: Column) => {
  if (column.sortable) {
    emit('sort', column.key)
  }
}
</script>

<template>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            :class="[
              'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
              column.sortable ? 'cursor-pointer hover:bg-gray-100' : ''
            ]"
            :style="{ width: column.width }"
            @click="handleSort(column)"
          >
            {{ column.label }}
          </th>
        </tr>
      </thead>

      <tbody class="bg-white divide-y divide-gray-200">
        <!-- Loading state -->
        <tr v-if="isLoading">
          <td :colspan="columns.length" class="px-6 py-4 text-center">
            <div class="flex items-center justify-center">
              <svg
                class="animate-spin h-5 w-5 text-primary-600"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <span class="ml-2 text-gray-500">Loading...</span>
            </div>
          </td>
        </tr>

        <!-- Empty state -->
        <tr v-else-if="data.length === 0">
          <td :colspan="columns.length" class="px-6 py-4 text-center text-gray-500">
            {{ emptyMessage }}
          </td>
        </tr>

        <!-- Data rows -->
        <tr
          v-else
          v-for="(row, index) in data"
          :key="index"
          class="hover:bg-gray-50 cursor-pointer transition-colors"
          @click="handleRowClick(row)"
        >
          <td
            v-for="column in columns"
            :key="column.key"
            class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
          >
            <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
              {{ row[column.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

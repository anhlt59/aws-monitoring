<script setup lang="ts">
interface Props {
  currentPage: number
  totalItems: number
  pageSize: number
  hasMore: boolean
}

interface Emits {
  (e: 'previous'): void
  (e: 'next'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const startItem = (props.currentPage - 1) * props.pageSize + 1
const endItem = Math.min(props.currentPage * props.pageSize, props.totalItems)
</script>

<template>
  <div class="flex items-center justify-between px-6 py-4 border-t border-gray-200">
    <div class="text-sm text-gray-700">
      Showing {{ startItem }} to {{ endItem }} of {{ totalItems }} results
    </div>
    <div class="flex gap-2">
      <BaseButton
        size="sm"
        variant="secondary"
        :disabled="currentPage === 1"
        @click="emit('previous')"
      >
        Previous
      </BaseButton>
      <BaseButton
        size="sm"
        variant="secondary"
        :disabled="!hasMore"
        @click="emit('next')"
      >
        Next
      </BaseButton>
    </div>
  </div>
</template>

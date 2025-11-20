<script setup lang="ts">
import { computed } from 'vue'
import { TaskPriority, TaskPriorityLabels } from '@/core/enums'
import BaseBadge from '@/components/base/BaseBadge.vue'

interface Props {
  priority: TaskPriority
}

const props = defineProps<Props>()

const label = computed(() => TaskPriorityLabels[props.priority])

const badgeVariant = computed(() => {
  switch (props.priority) {
    case TaskPriority.Critical:
      return 'error'
    case TaskPriority.High:
      return 'warning'
    case TaskPriority.Medium:
      return 'info'
    case TaskPriority.Low:
      return 'success'
    default:
      return 'neutral'
  }
})
</script>

<template>
  <BaseBadge :variant="badgeVariant">
    {{ label }}
  </BaseBadge>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { TaskStatus, TaskStatusLabels } from '@/core/enums'
import BaseBadge from '@/components/base/BaseBadge.vue'

interface Props {
  status: TaskStatus
}

const props = defineProps<Props>()

const label = computed(() => TaskStatusLabels[props.status])

const badgeVariant = computed(() => {
  switch (props.status) {
    case TaskStatus.Open:
      return 'warning'
    case TaskStatus.InProgress:
      return 'info'
    case TaskStatus.Closed:
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

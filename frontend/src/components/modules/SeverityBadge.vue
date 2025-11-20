<script setup lang="ts">
import { computed } from 'vue'
import { Severity, SeverityLabels, SeverityColors } from '@/core/enums'
import BaseBadge from '@/components/base/BaseBadge.vue'

interface Props {
  severity: Severity
}

const props = defineProps<Props>()

const config = computed(() => ({
  label: SeverityLabels[props.severity],
  icon: SeverityColors[props.severity].icon,
  classes: `${SeverityColors[props.severity].bg} ${SeverityColors[props.severity].text}`
}))

const badgeVariant = computed(() => {
  switch (props.severity) {
    case Severity.Critical:
      return 'error'
    case Severity.High:
      return 'warning'
    case Severity.Medium:
      return 'info'
    case Severity.Low:
      return 'success'
    default:
      return 'neutral'
  }
})
</script>

<template>
  <BaseBadge :variant="badgeVariant">
    <span class="mr-1">{{ config.icon }}</span>
    {{ config.label }}
  </BaseBadge>
</template>

<script setup lang="ts">
type BadgeVariant = 'success' | 'error' | 'warning' | 'info' | 'neutral'
type BadgeSize = 'sm' | 'md' | 'lg'

interface Props {
  variant?: BadgeVariant
  size?: BadgeSize
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'neutral',
  size: 'md'
})

const variantClasses = {
  success: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800',
  warning: 'bg-yellow-100 text-yellow-800',
  info: 'bg-blue-100 text-blue-800',
  neutral: 'bg-gray-100 text-gray-800'
}

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base'
}
</script>

<template>
  <span
    :class="[
      'inline-flex items-center font-medium rounded-full',
      variantClasses[variant],
      sizeClasses[size]
    ]"
  >
    <slot />
  </span>
</template>

<script setup lang="ts">
type AlertVariant = 'success' | 'error' | 'warning' | 'info'

interface Props {
  variant?: AlertVariant
  dismissible?: boolean
}

interface Emits {
  (e: 'dismiss'): void
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'info',
  dismissible: false
})

const emit = defineEmits<Emits>()

const variantClasses = {
  success: 'bg-green-50 border-green-200 text-green-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800'
}

const handleDismiss = () => {
  emit('dismiss')
}
</script>

<template>
  <div :class="['border rounded-md p-4', variantClasses[variant]]" role="alert">
    <div class="flex items-start">
      <div class="flex-1">
        <slot />
      </div>
      <button
        v-if="dismissible"
        type="button"
        class="ml-3 inline-flex text-gray-400 hover:text-gray-500 focus:outline-none"
        @click="handleDismiss"
      >
        <span class="sr-only">Dismiss</span>
        <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path
            fill-rule="evenodd"
            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
            clip-rule="evenodd"
          />
        </svg>
      </button>
    </div>
  </div>
</template>

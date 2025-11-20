<script setup lang="ts">
interface Props {
  padding?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  padding: true
})
</script>

<template>
  <div :class="['bg-white rounded-lg shadow', padding ? 'p-6' : '']">
    <slot />
  </div>
</template>

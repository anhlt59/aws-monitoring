<script setup lang="ts">
interface Option {
  value: string | number
  label: string
}

interface Props {
  modelValue: string | number | (string | number)[]
  options: Option[]
  label?: string
  placeholder?: string
  disabled?: boolean
  error?: string
  required?: boolean
  multiple?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string | number | (string | number)[]): void
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  required: false,
  multiple: false
})

const emit = defineEmits<Emits>()

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  if (props.multiple) {
    const selected = Array.from(target.selectedOptions).map((option) => option.value)
    emit('update:modelValue', selected)
  } else {
    emit('update:modelValue', target.value)
  }
}
</script>

<template>
  <div class="w-full">
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <select
      :value="modelValue"
      :disabled="disabled"
      :required="required"
      :multiple="multiple"
      :class="[
        'block w-full rounded-md shadow-sm',
        'focus:ring-primary-500 focus:border-primary-500',
        'disabled:bg-gray-100 disabled:cursor-not-allowed',
        error
          ? 'border-red-300 text-red-900 focus:ring-red-500 focus:border-red-500'
          : 'border-gray-300'
      ]"
      @change="handleChange"
    >
      <option v-if="placeholder && !multiple" value="">{{ placeholder }}</option>
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
  </div>
</template>

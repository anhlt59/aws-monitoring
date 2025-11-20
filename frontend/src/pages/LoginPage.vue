<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/features'
import { ROUTE_NAMES } from '@/core/constants'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseAlert from '@/components/base/BaseAlert.vue'

const router = useRouter()
const { login, isLoading, error } = useAuth()

const email = ref('')
const password = ref('')

const handleSubmit = async () => {
  const success = await login({ email: email.value, password: password.value })

  if (success) {
    router.push({ name: ROUTE_NAMES.DASHBOARD })
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h1 class="text-center text-4xl font-bold text-primary-600">AWS Monitoring</h1>
        <h2 class="mt-6 text-center text-3xl font-bold text-gray-900">Sign in to your account</h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Content Management System for AWS Resources Monitoring
        </p>
      </div>

      <BaseAlert v-if="error" variant="error" dismissible>
        {{ error.message }}
      </BaseAlert>

      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="space-y-4">
          <BaseInput
            v-model="email"
            type="email"
            label="Email address"
            placeholder="you@example.com"
            required
          />

          <BaseInput
            v-model="password"
            type="password"
            label="Password"
            placeholder="••••••••"
            required
          />
        </div>

        <div>
          <BaseButton
            type="submit"
            class="w-full"
            :loading="isLoading"
            :disabled="!email || !password"
          >
            Sign in
          </BaseButton>
        </div>
      </form>
    </div>
  </div>
</template>

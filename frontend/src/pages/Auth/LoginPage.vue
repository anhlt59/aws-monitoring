<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/modules/auth.store';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const rememberMe = ref(false);
const error = ref('');

const handleLogin = async () => {
  error.value = '';

  if (!email.value || !password.value) {
    error.value = 'Please enter both email and password';
    return;
  }

  const success = await authStore.login({
    email: email.value,
    password: password.value,
    remember_me: rememberMe.value
  });

  if (success) {
    // Redirect to dashboard or the page user was trying to access
    const redirect = router.currentRoute.value.query.redirect as string || '/';
    router.push(redirect);
  } else {
    error.value = authStore.error || 'Login failed. Please try again.';
  }
};
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 px-4">
    <div class="max-w-md w-full">
      <!-- Logo/Title -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900">
          AWS Monitoring
        </h1>
        <p class="mt-2 text-sm text-gray-600">
          Sign in to your account
        </p>
      </div>

      <!-- Login Form -->
      <div class="bg-white py-8 px-6 shadow-lg rounded-lg">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {{ error }}
          </div>

          <!-- Email Field -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              v-model="email"
              type="email"
              autocomplete="email"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="user@example.com"
            />
          </div>

          <!-- Password Field -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              v-model="password"
              type="password"
              autocomplete="current-password"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="••••••••"
            />
          </div>

          <!-- Remember Me -->
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="rememberMe"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="remember-me" class="ml-2 block text-sm text-gray-700">
              Remember me
            </label>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="authStore.isLoading"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="authStore.isLoading">Signing in...</span>
            <span v-else>Sign in</span>
          </button>
        </form>

        <!-- Forgot Password Link -->
        <div class="mt-6 text-center">
          <a href="#" class="text-sm text-blue-600 hover:text-blue-500">
            Forgot your password?
          </a>
        </div>
      </div>

      <!-- Footer -->
      <p class="mt-8 text-center text-xs text-gray-500">
        AWS Monitoring System v1.0.0
      </p>
    </div>
  </div>
</template>

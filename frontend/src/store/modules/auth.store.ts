import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User, LoginCredentials, LoginResponse } from '@/core/types';
import { authApi } from '@/api';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value);

  // Actions
  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    isLoading.value = true;
    error.value = null;

    try {
      const response: LoginResponse = await authApi.login(credentials);

      // Store tokens
      token.value = response.access_token;
      user.value = response.user;

      // Persist to localStorage
      localStorage.setItem('access_token', response.access_token);
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token);
      }

      return true;
    } catch (err: any) {
      error.value = err.message || 'Login failed';
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  const logout = () => {
    // Clear state
    user.value = null;
    token.value = null;
    error.value = null;

    // Clear localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    // Call logout API (fire and forget)
    authApi.logout().catch(() => {
      // Ignore errors on logout
    });
  };

  const loadFromStorage = () => {
    const storedToken = localStorage.getItem('access_token');
    if (storedToken) {
      token.value = storedToken;
      // User data will be loaded when needed
    }
  };

  const setUser = (userData: User) => {
    user.value = userData;
  };

  // Initialize from storage
  loadFromStorage();

  return {
    // State
    user,
    token,
    isLoading,
    error,

    // Getters
    isAuthenticated,

    // Actions
    login,
    logout,
    setUser,
    loadFromStorage
  };
});

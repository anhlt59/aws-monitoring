import { ref, computed } from 'vue'
import { usersApi } from '@/api'
import type {
  User,
  UserFilters,
  CreateUserRequest,
  UpdateUserRequest,
  ApiError
} from '@/core/types'

/**
 * Users management composable
 */
export function useUsers() {
  // State
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<ApiError | null>(null)
  const totalUsers = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const hasMore = ref(false)

  // Filters
  const filters = ref<UserFilters>({
    page: 1,
    page_size: 20
  })

  // Computed
  const activeUsers = computed(() => users.value.filter((u) => u.is_active))
  const hasUsers = computed(() => users.value.length > 0)

  // Methods
  const fetchUsers = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await usersApi.getUsers(filters.value)
      users.value = response.items
      totalUsers.value = response.total
      currentPage.value = response.page
      pageSize.value = response.page_size
      hasMore.value = response.has_more
    } catch (err) {
      error.value = err as ApiError
      users.value = []
    } finally {
      isLoading.value = false
    }
  }

  const fetchUserById = async (id: string) => {
    isLoading.value = true
    error.value = null

    try {
      currentUser.value = await usersApi.getUserById(id)
      return currentUser.value
    } catch (err) {
      error.value = err as ApiError
      return null
    } finally {
      isLoading.value = false
    }
  }

  const createUser = async (data: CreateUserRequest): Promise<User | null> => {
    isLoading.value = true
    error.value = null

    try {
      const user = await usersApi.createUser(data)
      await fetchUsers()
      return user
    } catch (err) {
      error.value = err as ApiError
      return null
    } finally {
      isLoading.value = false
    }
  }

  const updateUser = async (id: string, data: UpdateUserRequest): Promise<boolean> => {
    isLoading.value = true
    error.value = null

    try {
      const updatedUser = await usersApi.updateUser(id, data)

      // Update in list if exists
      const index = users.value.findIndex((u) => u.id === id)
      if (index !== -1) {
        users.value[index] = updatedUser
      }

      // Update current user if it's the same
      if (currentUser.value?.id === id) {
        currentUser.value = updatedUser
      }

      return true
    } catch (err) {
      error.value = err as ApiError
      return false
    } finally {
      isLoading.value = false
    }
  }

  const deleteUser = async (id: string): Promise<boolean> => {
    try {
      await usersApi.deleteUser(id)
      await fetchUsers()
      return true
    } catch (err) {
      error.value = err as ApiError
      return false
    }
  }

  const setFilters = (newFilters: Partial<UserFilters>) => {
    filters.value = { ...filters.value, ...newFilters, page: 1 }
    fetchUsers()
  }

  const nextPage = () => {
    if (hasMore.value) {
      filters.value.page = (filters.value.page || 1) + 1
      fetchUsers()
    }
  }

  const previousPage = () => {
    if ((filters.value.page || 1) > 1) {
      filters.value.page = (filters.value.page || 1) - 1
      fetchUsers()
    }
  }

  const clearFilters = () => {
    filters.value = { page: 1, page_size: 20 }
    fetchUsers()
  }

  return {
    // State
    users,
    currentUser,
    isLoading,
    error,
    filters,
    totalUsers,
    currentPage,
    pageSize,
    hasMore,

    // Computed
    activeUsers,
    hasUsers,

    // Methods
    fetchUsers,
    fetchUserById,
    createUser,
    updateUser,
    deleteUser,
    setFilters,
    nextPage,
    previousPage,
    clearFilters
  }
}

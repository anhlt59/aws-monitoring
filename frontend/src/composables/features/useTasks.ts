import { ref, computed } from 'vue'
import { tasksApi } from '@/api'
import type {
  Task,
  TaskFilters,
  CreateTaskRequest,
  UpdateTaskRequest,
  AddCommentRequest,
  ApiError,
  TaskStatus
} from '@/core/types'

/**
 * Tasks management composable
 */
export function useTasks() {
  // State
  const tasks = ref<Task[]>([])
  const currentTask = ref<Task | null>(null)
  const isLoading = ref(false)
  const error = ref<ApiError | null>(null)
  const totalTasks = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const hasMore = ref(false)

  // Filters
  const filters = ref<TaskFilters>({
    page: 1,
    page_size: 20
  })

  // Computed
  const openTasks = computed(() =>
    tasks.value.filter((t) => t.status === 'open' as TaskStatus)
  )

  const inProgressTasks = computed(() =>
    tasks.value.filter((t) => t.status === 'in_progress' as TaskStatus)
  )

  const hasTasks = computed(() => tasks.value.length > 0)

  // Methods
  const fetchTasks = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await tasksApi.getTasks(filters.value)
      tasks.value = response.items
      totalTasks.value = response.total
      currentPage.value = response.page
      pageSize.value = response.page_size
      hasMore.value = response.has_more
    } catch (err) {
      error.value = err as ApiError
      tasks.value = []
    } finally {
      isLoading.value = false
    }
  }

  const fetchTaskById = async (id: string) => {
    isLoading.value = true
    error.value = null

    try {
      currentTask.value = await tasksApi.getTaskById(id)
      return currentTask.value
    } catch (err) {
      error.value = err as ApiError
      return null
    } finally {
      isLoading.value = false
    }
  }

  const createTask = async (data: CreateTaskRequest): Promise<Task | null> => {
    isLoading.value = true
    error.value = null

    try {
      const task = await tasksApi.createTask(data)
      await fetchTasks()
      return task
    } catch (err) {
      error.value = err as ApiError
      return null
    } finally {
      isLoading.value = false
    }
  }

  const updateTask = async (id: string, data: UpdateTaskRequest): Promise<boolean> => {
    isLoading.value = true
    error.value = null

    try {
      const updatedTask = await tasksApi.updateTask(id, data)

      // Update in list if exists
      const index = tasks.value.findIndex((t) => t.id === id)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }

      // Update current task if it's the same
      if (currentTask.value?.id === id) {
        currentTask.value = updatedTask
      }

      return true
    } catch (err) {
      error.value = err as ApiError
      return false
    } finally {
      isLoading.value = false
    }
  }

  const deleteTask = async (id: string): Promise<boolean> => {
    try {
      await tasksApi.deleteTask(id)
      await fetchTasks()
      return true
    } catch (err) {
      error.value = err as ApiError
      return false
    }
  }

  const addComment = async (taskId: string, data: AddCommentRequest): Promise<boolean> => {
    try {
      await tasksApi.addComment(taskId, data)
      await fetchTaskById(taskId)
      return true
    } catch (err) {
      error.value = err as ApiError
      return false
    }
  }

  const updateTaskStatus = async (taskId: string, status: TaskStatus): Promise<boolean> => {
    try {
      await tasksApi.updateTaskStatus(taskId, status)
      await fetchTaskById(taskId)
      return true
    } catch (err) {
      error.value = err as ApiError
      return false
    }
  }

  const setFilters = (newFilters: Partial<TaskFilters>) => {
    filters.value = { ...filters.value, ...newFilters, page: 1 }
    fetchTasks()
  }

  const nextPage = () => {
    if (hasMore.value) {
      filters.value.page = (filters.value.page || 1) + 1
      fetchTasks()
    }
  }

  const previousPage = () => {
    if ((filters.value.page || 1) > 1) {
      filters.value.page = (filters.value.page || 1) - 1
      fetchTasks()
    }
  }

  const clearFilters = () => {
    filters.value = { page: 1, page_size: 20 }
    fetchTasks()
  }

  return {
    // State
    tasks,
    currentTask,
    isLoading,
    error,
    filters,
    totalTasks,
    currentPage,
    pageSize,
    hasMore,

    // Computed
    openTasks,
    inProgressTasks,
    hasTasks,

    // Methods
    fetchTasks,
    fetchTaskById,
    createTask,
    updateTask,
    deleteTask,
    addComment,
    updateTaskStatus,
    setFilters,
    nextPage,
    previousPage,
    clearFilters
  }
}

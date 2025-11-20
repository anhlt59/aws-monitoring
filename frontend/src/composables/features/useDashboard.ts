import { ref } from 'vue'
import { dashboardApi } from '@/api'
import type { DashboardOverview, ApiError } from '@/core/types'

/**
 * Dashboard composable
 */
export function useDashboard() {
  const overview = ref<DashboardOverview | null>(null)
  const isLoading = ref(false)
  const error = ref<ApiError | null>(null)

  const fetchOverview = async () => {
    isLoading.value = true
    error.value = null

    try {
      overview.value = await dashboardApi.getOverview()
    } catch (err) {
      error.value = err as ApiError
    } finally {
      isLoading.value = false
    }
  }

  return {
    overview,
    isLoading,
    error,
    fetchOverview
  }
}

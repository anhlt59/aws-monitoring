import { ref, computed } from 'vue'
import { eventsApi } from '@/api'
import type { Event, EventFilters, ApiError, Severity } from '@/core/types'

/**
 * Events management composable
 */
export function useEvents() {
  // State
  const events = ref<Event[]>([])
  const isLoading = ref(false)
  const error = ref<ApiError | null>(null)
  const totalEvents = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const hasMore = ref(false)

  // Filters
  const filters = ref<EventFilters>({
    page: 1,
    page_size: 20
  })

  // Computed
  const criticalEvents = computed(() =>
    events.value.filter((e) => e.severity === 'critical' as Severity)
  )

  const hasEvents = computed(() => events.value.length > 0)

  // Methods
  const fetchEvents = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await eventsApi.getEvents(filters.value)
      events.value = response.items
      totalEvents.value = response.total
      currentPage.value = response.page
      pageSize.value = response.page_size
      hasMore.value = response.has_more
    } catch (err) {
      error.value = err as ApiError
      events.value = []
    } finally {
      isLoading.value = false
    }
  }

  const refreshEvents = async () => {
    await fetchEvents()
  }

  const setFilters = (newFilters: Partial<EventFilters>) => {
    filters.value = { ...filters.value, ...newFilters, page: 1 }
    fetchEvents()
  }

  const nextPage = () => {
    if (hasMore.value) {
      filters.value.page = (filters.value.page || 1) + 1
      fetchEvents()
    }
  }

  const previousPage = () => {
    if ((filters.value.page || 1) > 1) {
      filters.value.page = (filters.value.page || 1) - 1
      fetchEvents()
    }
  }

  const clearFilters = () => {
    filters.value = { page: 1, page_size: 20 }
    fetchEvents()
  }

  const deleteEvent = async (id: string) => {
    try {
      await eventsApi.deleteEvent(id)
      await refreshEvents()
      return true
    } catch (err) {
      error.value = err as ApiError
      return false
    }
  }

  return {
    // State
    events,
    isLoading,
    error,
    filters,
    totalEvents,
    currentPage,
    pageSize,
    hasMore,

    // Computed
    criticalEvents,
    hasEvents,

    // Methods
    fetchEvents,
    refreshEvents,
    setFilters,
    nextPage,
    previousPage,
    clearFilters,
    deleteEvent
  }
}

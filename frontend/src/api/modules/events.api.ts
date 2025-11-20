import { apiClient } from '../client'
import type { Event, EventFilters, PaginatedResponse } from '@/core/types'

/**
 * Events API service
 */
export const eventsApi = {
  /**
   * Fetch paginated events with filters
   */
  async getEvents(filters: EventFilters = {}): Promise<PaginatedResponse<Event>> {
    const response = await apiClient.get<PaginatedResponse<Event>>('/api/events', {
      params: filters
    })
    return response.data
  },

  /**
   * Fetch single event by ID
   */
  async getEventById(id: string): Promise<Event> {
    const response = await apiClient.get<Event>(`/api/events/${id}`)
    return response.data
  },

  /**
   * Delete event
   */
  async deleteEvent(id: string): Promise<void> {
    await apiClient.delete(`/api/events/${id}`)
  }
}

import { apiClient } from '../client';
import type { Event, EventFilters, PaginatedResponse } from '@/core/types';

export const eventsApi = {
  /**
   * Fetch paginated events with filters
   */
  async getEvents(filters?: EventFilters): Promise<PaginatedResponse<Event>> {
    const response = await apiClient.get<PaginatedResponse<Event>>('/events', {
      params: filters
    });
    return response.data;
  },

  /**
   * Fetch single event by ID
   */
  async getEventById(id: string): Promise<Event> {
    const response = await apiClient.get<Event>(`/events/${id}`);
    return response.data;
  },

  /**
   * Update event (acknowledge, add notes)
   */
  async updateEvent(id: string, updates: Partial<Event>): Promise<Event> {
    const response = await apiClient.patch<Event>(`/events/${id}`, updates);
    return response.data;
  },

  /**
   * Get related events
   */
  async getRelatedEvents(id: string, params?: { limit?: number }): Promise<PaginatedResponse<Event>> {
    const response = await apiClient.get<PaginatedResponse<Event>>(`/events/${id}/related`, {
      params
    });
    return response.data;
  },

  /**
   * Export events
   */
  async exportEvents(format: 'csv' | 'json' | 'pdf', filters?: EventFilters): Promise<Blob> {
    const response = await apiClient.get('/events/export', {
      params: { format, ...filters },
      responseType: 'blob'
    });
    return response.data;
  },

  /**
   * Get unique accounts
   */
  async getAccounts(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/events/accounts');
    return response.data;
  },

  /**
   * Get unique regions
   */
  async getRegions(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/events/regions');
    return response.data;
  }
};

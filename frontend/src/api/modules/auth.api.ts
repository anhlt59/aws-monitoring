import { apiClient } from '../client';
import type { LoginCredentials, LoginResponse, AuthToken } from '@/core/types';

export const authApi = {
  /**
   * User login
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', credentials);
    return response.data;
  },

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<AuthToken> {
    const response = await apiClient.post<AuthToken>('/auth/refresh', {
      refresh_token: refreshToken
    });
    return response.data;
  },

  /**
   * User logout
   */
  async logout(): Promise<void> {
    await apiClient.post('/auth/logout');
  }
};

import { apiClient } from '../client'
import type {
  AwsAccount,
  CreateAwsAccountRequest,
  UpdateAwsAccountRequest,
  MonitoringConfig
} from '@/core/types'

/**
 * Configuration API service
 */
export const configApi = {
  /**
   * Fetch all AWS accounts
   */
  async getAwsAccounts(): Promise<AwsAccount[]> {
    const response = await apiClient.get<AwsAccount[]>('/api/config/aws-accounts')
    return response.data
  },

  /**
   * Fetch single AWS account by ID
   */
  async getAwsAccountById(id: string): Promise<AwsAccount> {
    const response = await apiClient.get<AwsAccount>(`/api/config/aws-accounts/${id}`)
    return response.data
  },

  /**
   * Create new AWS account
   */
  async createAwsAccount(data: CreateAwsAccountRequest): Promise<AwsAccount> {
    const response = await apiClient.post<AwsAccount>('/api/config/aws-accounts', data)
    return response.data
  },

  /**
   * Update AWS account
   */
  async updateAwsAccount(id: string, data: UpdateAwsAccountRequest): Promise<AwsAccount> {
    const response = await apiClient.put<AwsAccount>(`/api/config/aws-accounts/${id}`, data)
    return response.data
  },

  /**
   * Delete AWS account
   */
  async deleteAwsAccount(id: string): Promise<void> {
    await apiClient.delete(`/api/config/aws-accounts/${id}`)
  },

  /**
   * Test AWS account connection
   */
  async testAwsAccountConnection(id: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post<{ success: boolean; message: string }>(
      `/api/config/aws-accounts/${id}/test`
    )
    return response.data
  },

  /**
   * Get monitoring configuration
   */
  async getMonitoringConfig(): Promise<MonitoringConfig> {
    const response = await apiClient.get<MonitoringConfig>('/api/config/monitoring')
    return response.data
  },

  /**
   * Update monitoring configuration
   */
  async updateMonitoringConfig(data: MonitoringConfig): Promise<MonitoringConfig> {
    const response = await apiClient.put<MonitoringConfig>('/api/config/monitoring', data)
    return response.data
  }
}

import { AgentStatus } from '../enums/status';

/**
 * Agent entity
 */
export interface Agent {
  account: string;        // AWS Account ID
  region: string;         // AWS Region
  status: AgentStatus;
  deployed_at: number;    // Unix timestamp
  created_at: number;     // Unix timestamp
}

/**
 * Agent detail with configuration
 */
export interface AgentDetail extends Agent {
  config?: AgentConfig;
  last_execution?: number;
  events_published?: number;
}

/**
 * Agent configuration
 */
export interface AgentConfig {
  query_string?: string;
  query_duration?: number;
  chunk_size?: number;
}

/**
 * Agent deployment request
 */
export interface AgentDeploymentRequest {
  account: string;
  region: string;
  config?: AgentConfig;
}

/**
 * Agent health information
 */
export interface AgentHealth {
  account: string;
  region: string;
  is_healthy: boolean;
  last_heartbeat?: number;
  uptime_percentage?: number;
  error_rate?: number;
  last_error?: string;
}

/**
 * Agent metrics
 */
export interface AgentMetrics {
  account: string;
  period: string;
  events_published: number;
  errors_detected: number;
  average_query_duration?: number;
  log_groups_monitored?: number;
}

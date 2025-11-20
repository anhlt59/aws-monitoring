/**
 * AWS Account configuration
 */
export interface AwsAccount {
  id: string
  account_id: string
  account_name: string
  region: string
  access_key_id?: string
  secret_access_key?: string
  role_arn?: string
  is_active: boolean
  created_at: number
  updated_at: number
}

/**
 * Create AWS account request
 */
export interface CreateAwsAccountRequest {
  account_id: string
  account_name: string
  region: string
  access_key_id?: string
  secret_access_key?: string
  role_arn?: string
}

/**
 * Update AWS account request
 */
export interface UpdateAwsAccountRequest {
  account_name?: string
  region?: string
  access_key_id?: string
  secret_access_key?: string
  role_arn?: string
  is_active?: boolean
}

/**
 * AWS Service configuration
 */
export interface AwsServiceConfig {
  service_name: string
  enabled: boolean
  polling_interval?: number
  thresholds?: Record<string, any>
  resource_filters?: {
    resource_ids?: string[]
    tags?: Record<string, string>
    resource_types?: string[]
  }
  severity_rules?: {
    conditions: Array<{
      metric: string
      operator: string
      value: number
      severity: string
    }>
  }
}

/**
 * Monitoring configuration
 */
export interface MonitoringConfig {
  services: AwsServiceConfig[]
  global_settings: {
    default_polling_interval: number
    alert_email_enabled: boolean
    alert_email_recipients: string[]
  }
}

/**
 * Available AWS services
 */
export const AWS_SERVICES = [
  { value: 'cloudwatch', label: 'AWS CloudWatch Logs' },
  { value: 'guardduty', label: 'AWS GuardDuty' },
  { value: 'health', label: 'AWS Health Dashboard' },
  { value: 'config', label: 'AWS Config' },
  { value: 'cloudtrail', label: 'AWS CloudTrail' },
  { value: 'ec2', label: 'Amazon EC2' },
  { value: 'lambda', label: 'AWS Lambda' },
  { value: 'rds', label: 'Amazon RDS' },
  { value: 's3', label: 'Amazon S3' }
] as const

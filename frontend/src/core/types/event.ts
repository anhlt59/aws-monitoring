import { Severity } from '../enums/severity';

/**
 * Monitoring event entity
 * Maps to backend: Event domain model
 */
export interface Event {
  id: string;
  account: string;
  region: string;
  source: string;
  detail: Record<string, unknown>;
  detail_type: string;
  severity: Severity;
  resources: string[];
  published_at: number;  // Unix timestamp
  updated_at: number;    // Unix timestamp
  acknowledged?: boolean;
  notes?: string;
  tags?: string[];
}

/**
 * Event filters for querying
 */
export interface EventFilters {
  account?: string;
  region?: string;
  source?: string;
  severity?: Severity | Severity[];
  detail_type?: string;
  start_date?: number;   // Unix timestamp
  end_date?: number;     // Unix timestamp
  search?: string;
  page?: number;
  page_size?: number;
  sort?: string;
}

/**
 * CloudWatch Alarm event detail
 */
export interface CloudWatchAlarmDetail {
  alarmName: string;
  configuration: {
    description?: string;
    metrics: AlarmMetric[];
  };
  previousState: AlarmState;
  state: AlarmState;
}

export interface AlarmState {
  reason: string;
  reasonData: string;
  timestamp: string;
  value: 'OK' | 'ALARM' | 'INSUFFICIENT_DATA';
}

export interface AlarmMetric {
  id: string;
  metricStat: {
    metric: {
      dimensions: Record<string, string>;
      name: string;
      namespace: string;
    };
    period: number;
    stat: string;
  };
  returnData: boolean;
}

/**
 * Lambda error event detail
 */
export interface LambdaErrorDetail {
  functionName: string;
  errorMessage: string;
  errorType: string;
  stackTrace?: string[];
  requestId: string;
}

/**
 * ECS task failure detail
 */
export interface ECSTaskFailureDetail {
  clusterArn: string;
  taskArn: string;
  taskDefinitionArn: string;
  desiredStatus: string;
  lastStatus: string;
  stoppedReason?: string;
  containers: ECSContainer[];
}

export interface ECSContainer {
  containerArn: string;
  name: string;
  exitCode?: number;
  reason?: string;
}

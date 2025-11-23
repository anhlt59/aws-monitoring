# Monitoring Configuration Model Documentation

The Monitoring Configuration model represents the global configuration for the monitoring system. This is a singleton configuration that controls how the system monitors AWS resources and processes alerts.

## Entity Model

| Field            | Type                 | Description                                                    |
|------------------|----------------------|----------------------------------------------------------------|
| `services`       | Array<ServiceConfig> | Configuration for each monitored AWS service                   |
| `global_settings`| Object               | Global monitoring settings                                     |
| `updated_at`     | Integer              | Unix timestamp of when config was last updated                 |
| `updated_by`     | String               | User ID who last updated the configuration (optional)          |

### ServiceConfig Structure

| Field              | Type          | Description                                                  |
|--------------------|---------------|--------------------------------------------------------------|
| `service_name`     | String        | AWS service name (e.g., `cloudwatch`, `guardduty`)           |
| `enabled`          | Boolean       | Service monitoring enabled/disabled, defaults to `true`      |
| `polling_interval` | Integer       | Polling interval in seconds, defaults to 300 (5 minutes)     |
| `thresholds`       | Object        | Service-specific alert thresholds                            |
| `resource_filters` | Object        | Resource filtering rules                                     |
| `severity_rules`   | Array<Object> | Rules for determining event severity                         |

### Global Settings Structure

| Setting                      | Type          | Default Value | Description                                    |
|------------------------------|---------------|---------------|------------------------------------------------|
| `default_polling_interval`   | Integer       | 300           | Default polling interval in seconds (5 min)    |
| `alert_email_enabled`        | Boolean       | true          | Enable email alerts                            |
| `alert_email_recipients`     | Array<String> | []            | List of email addresses for alerts             |
| `alert_slack_enabled`        | Boolean       | true          | Enable Slack notifications                     |
| `alert_slack_webhook`        | String        | ""            | Slack webhook URL                              |
| `data_retention_days`        | Integer       | 90            | Number of days to retain event data            |
| `event_batch_size`           | Integer       | 100           | Batch size for event processing                |

## Example

```json
{
  "services": [
    {
      "service_name": "cloudwatch",
      "enabled": true,
      "polling_interval": 300,
      "thresholds": {
        "cpu_threshold": 80,
        "memory_threshold": 90,
        "error_rate_threshold": 5
      },
      "resource_filters": {
        "resource_types": ["AWS::EC2::Instance", "AWS::RDS::DBInstance"],
        "tags": {
          "Environment": "production",
          "Team": "platform"
        }
      },
      "severity_rules": [
        {
          "metric": "cpu_utilization",
          "operator": ">=",
          "value": 90,
          "severity": "critical"
        },
        {
          "metric": "cpu_utilization",
          "operator": ">=",
          "value": 70,
          "severity": "high"
        }
      ]
    },
    {
      "service_name": "guardduty",
      "enabled": true,
      "polling_interval": 180,
      "thresholds": {
        "min_severity": 5
      },
      "resource_filters": {},
      "severity_rules": [
        {
          "metric": "finding_severity",
          "operator": ">=",
          "value": 8,
          "severity": "critical"
        },
        {
          "metric": "finding_severity",
          "operator": ">=",
          "value": 5,
          "severity": "high"
        }
      ]
    }
  ],
  "global_settings": {
    "default_polling_interval": 300,
    "alert_email_enabled": true,
    "alert_email_recipients": [
      "ops-team@example.com",
      "platform-alerts@example.com"
    ],
    "alert_slack_enabled": true,
    "alert_slack_webhook": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX",
    "data_retention_days": 90,
    "event_batch_size": 100
  },
  "updated_at": 1735776000,
  "updated_by": "550e8400-e29b-41d4-a716-446655440000"
}
```

## DynamoDB Schema

| Field            | Type      | Description                                                    |
|------------------|-----------|----------------------------------------------------------------|
| `pk`             | String    | Partition key: `CONFIG` (singleton)                            |
| `sk`             | String    | Sort key: `MONITORING_CONFIG` (singleton)                      |
| `services`       | String    | JSON string of service configurations array                    |
| `global_settings`| String    | JSON string of global settings object                          |
| `updated_at`     | Number    | Unix timestamp                                                 |
| `updated_by`     | String    | User ID (optional)                                             |

**Note:** This is a singleton record - there is only one monitoring configuration per system.

## Example DynamoDB Record

```json
{
  "pk": "CONFIG",
  "sk": "MONITORING_CONFIG",
  "services": "[{\"service_name\":\"cloudwatch\",\"enabled\":true,\"polling_interval\":300,\"thresholds\":{\"cpu_threshold\":80,\"memory_threshold\":90,\"error_rate_threshold\":5},\"resource_filters\":{\"resource_types\":[\"AWS::EC2::Instance\",\"AWS::RDS::DBInstance\"],\"tags\":{\"Environment\":\"production\",\"Team\":\"platform\"}},\"severity_rules\":[{\"metric\":\"cpu_utilization\",\"operator\":\">=\",\"value\":90,\"severity\":\"critical\"},{\"metric\":\"cpu_utilization\",\"operator\":\">=\",\"value\":70,\"severity\":\"high\"}]},{\"service_name\":\"guardduty\",\"enabled\":true,\"polling_interval\":180,\"thresholds\":{\"min_severity\":5},\"resource_filters\":{},\"severity_rules\":[{\"metric\":\"finding_severity\",\"operator\":\">=\",\"value\":8,\"severity\":\"critical\"},{\"metric\":\"finding_severity\",\"operator\":\">=\",\"value\":5,\"severity\":\"high\"}]}]",
  "global_settings": "{\"default_polling_interval\":300,\"alert_email_enabled\":true,\"alert_email_recipients\":[\"ops-team@example.com\",\"platform-alerts@example.com\"],\"alert_slack_enabled\":true,\"alert_slack_webhook\":\"https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX\",\"data_retention_days\":90,\"event_batch_size\":100}",
  "updated_at": 1735776000,
  "updated_by": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Access Patterns

|   | Access Pattern                      | Table/Index | Key Condition                                    | Notes                          |
|:--|:------------------------------------|:------------|--------------------------------------------------|:-------------------------------|
| 1 | Get monitoring configuration        | Table       | pk=`CONFIG` AND sk=`MONITORING_CONFIG`           | Singleton - always returns one |
| 2 | Update monitoring configuration     | Table       | pk=`CONFIG` AND sk=`MONITORING_CONFIG`           | Update singleton record        |

## Validation Rules

### Services Validation
- No duplicate service names allowed
- At least one service must be enabled
- Service name must not be empty
- Polling interval must be > 0

### Global Settings Validation
- `default_polling_interval` must be > 0
- `data_retention_days` must be > 0
- `event_batch_size` must be > 0
- Email recipients must be valid email addresses
- Slack webhook must be valid URL if provided

## Business Logic Methods

### Service Management
- `get_service_config(service_name)` - Get configuration for a specific service
- `is_service_enabled(service_name)` - Check if a service is enabled
- `update_service_config(service_name, config)` - Update or add service configuration
- `get_enabled_services()` - Get list of all enabled services

### Configuration Updates
- When updating configuration, `updated_at` is automatically set to current timestamp
- `updated_by` should be set to the authenticated user's ID

## Related Use Cases

- **GetConfig** - Fetch the singleton monitoring configuration
- **UpdateConfig** - Update global settings or service configurations
- **EnableService** - Enable monitoring for a specific service
- **DisableService** - Disable monitoring for a specific service
- **UpdateServiceThresholds** - Update alert thresholds for a service
- **UpdateResourceFilters** - Update resource filtering rules

## Service-Specific Threshold Examples

### CloudWatch Service

```json
{
  "service_name": "cloudwatch",
  "enabled": true,
  "polling_interval": 300,
  "thresholds": {
    "cpu_threshold": 80,
    "memory_threshold": 90,
    "disk_threshold": 85,
    "error_rate_threshold": 5,
    "latency_threshold": 1000
  },
  "resource_filters": {
    "resource_ids": ["i-1234567890abcdef0", "db-instance-1"],
    "resource_types": ["AWS::EC2::Instance", "AWS::RDS::DBInstance"],
    "tags": {
      "Environment": "production",
      "Team": "platform",
      "Critical": "true"
    }
  },
  "severity_rules": [
    {
      "metric": "cpu_utilization",
      "operator": ">=",
      "value": 90,
      "severity": "critical"
    },
    {
      "metric": "cpu_utilization",
      "operator": ">=",
      "value": 70,
      "severity": "high"
    },
    {
      "metric": "cpu_utilization",
      "operator": ">=",
      "value": 50,
      "severity": "medium"
    }
  ]
}
```

### GuardDuty Service

```json
{
  "service_name": "guardduty",
  "enabled": true,
  "polling_interval": 180,
  "thresholds": {
    "min_severity": 4,
    "max_findings_per_poll": 100
  },
  "resource_filters": {
    "finding_types": [
      "UnauthorizedAccess:*",
      "Backdoor:*",
      "CryptoCurrency:*"
    ]
  },
  "severity_rules": [
    {
      "metric": "finding_severity",
      "operator": ">=",
      "value": 8,
      "severity": "critical"
    },
    {
      "metric": "finding_severity",
      "operator": ">=",
      "value": 5,
      "severity": "high"
    },
    {
      "metric": "finding_severity",
      "operator": ">=",
      "value": 4,
      "severity": "medium"
    }
  ]
}
```

### Lambda Service

```json
{
  "service_name": "lambda",
  "enabled": true,
  "polling_interval": 300,
  "thresholds": {
    "error_rate_threshold": 5,
    "duration_threshold": 3000,
    "throttle_threshold": 10,
    "concurrent_executions_threshold": 900
  },
  "resource_filters": {
    "function_names": ["production-*", "api-*"],
    "tags": {
      "Environment": "production"
    }
  },
  "severity_rules": [
    {
      "metric": "error_rate",
      "operator": ">=",
      "value": 10,
      "severity": "critical"
    },
    {
      "metric": "error_rate",
      "operator": ">=",
      "value": 5,
      "severity": "high"
    },
    {
      "metric": "throttle_count",
      "operator": ">=",
      "value": 100,
      "severity": "critical"
    }
  ]
}
```

## Resource Filter Patterns

### Filter by Resource IDs
```json
{
  "resource_ids": [
    "i-1234567890abcdef0",
    "vol-0123456789abcdef0",
    "db-instance-1"
  ]
}
```

### Filter by Resource Types
```json
{
  "resource_types": [
    "AWS::EC2::Instance",
    "AWS::RDS::DBInstance",
    "AWS::Lambda::Function",
    "AWS::DynamoDB::Table"
  ]
}
```

### Filter by Tags
```json
{
  "tags": {
    "Environment": "production",
    "Team": "platform",
    "Critical": "true",
    "CostCenter": "engineering"
  }
}
```

### Combined Filters
```json
{
  "resource_types": ["AWS::EC2::Instance"],
  "tags": {
    "Environment": "production",
    "Team": "platform"
  },
  "resource_ids": ["i-prod-web-01", "i-prod-web-02"]
}
```

**Note:** When multiple filters are specified, they are combined with AND logic (all conditions must match).

## Severity Rule Operators

Supported operators for severity rules:
- `>=` - Greater than or equal to
- `>` - Greater than
- `<=` - Less than or equal to
- `<` - Less than
- `==` - Equal to
- `!=` - Not equal to

## Default Configuration

When the system is first initialized, a default configuration is created:

```json
{
  "services": [],
  "global_settings": {
    "default_polling_interval": 300,
    "alert_email_enabled": true,
    "alert_email_recipients": [],
    "alert_slack_enabled": true,
    "alert_slack_webhook": "",
    "data_retention_days": 90,
    "event_batch_size": 100
  },
  "updated_at": 1735689600,
  "updated_by": null
}
```

## Configuration Update Best Practices

1. **Validate before saving**: Ensure all thresholds and intervals are positive numbers
2. **Test alert channels**: Verify email/Slack settings work before saving
3. **Gradual rollout**: When changing polling intervals, test with one service first
4. **Backup current config**: Keep track of previous configurations for rollback
5. **Audit changes**: Always set `updated_by` to track who made changes
6. **Service-specific validation**: Each service may have its own validation requirements

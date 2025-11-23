# Event Model Documentation

The Event model stores monitoring events from AWS services for each account, sorted by event timestamp. This model is optimized for querying events within specific time ranges and filtering by various criteria.

## Entity Model

| Field          | Type          | Description                                                                  |
|----------------|---------------|------------------------------------------------------------------------------|
| `id`           | String        | Event UUID (generated on creation)                                           |
| `account`      | String        | AWS Account ID (e.g., `123456789012`)                                        |
| `region`       | String        | AWS Region (e.g., `us-east-1`)                                               |
| `source`       | String        | Source of the event (e.g., `aws.cloudwatch`, `aws.guardduty`)                |
| `detail_type`  | String        | Type of the event detail (e.g., `CloudWatch Alarm State Change`)             |
| `detail`       | Object        | JSON payload with raw event data (stored as JSON string in DB)               |
| `severity`     | Integer       | Event severity level (0-5, where 5 is most severe)                           |
| `resources`    | Array<String> | List of AWS resource ARNs affected by the event (stored as JSON string in DB)|
| `published_at` | Integer       | Unix timestamp of when the event was published                               |
| `updated_at`   | Integer       | Unix timestamp of when the event was last updated                            |
| `expired_at`   | Integer       | Unix timestamp of when the event expires (defaults to 90 days after creation)|

### Severity Levels

Event severity is represented as an integer from 0 to 5:

- `0` - Informational
- `1` - Low
- `2` - Medium
- `3` - High
- `4` - Critical
- `5` - Emergency

## Example

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "account": "123456789012",
  "region": "us-east-1",
  "source": "aws.cloudwatch",
  "detail_type": "CloudWatch Alarm State Change",
  "detail": {
    "alarmName": "ServerCpuTooHigh",
    "configuration": {
      "description": "Goes into alarm when server CPU utilization is too high!",
      "metrics": [
        {
          "id": "30b6c6b2-a864-43a2-4877-c09a1afc3b87",
          "metricStat": {
            "metric": {
              "dimensions": {
                "InstanceId": "i-12345678901234567"
              },
              "name": "CPUUtilization",
              "namespace": "AWS/EC2"
            },
            "period": 300,
            "stat": "Average"
          },
          "returnData": true
        }
      ]
    },
    "state": {
      "reason": "Threshold Crossed",
      "value": "ALARM"
    }
  },
  "severity": 3,
  "resources": [
    "arn:aws:cloudwatch:us-east-1:123456789012:alarm:ServerCpuTooHigh"
  ],
  "published_at": 1735689600,
  "updated_at": 1735689600,
  "expired_at": 1743465600
}
```

## DynamoDB Schema

| Field          | Type   | Description                                                                  |
|----------------|--------|------------------------------------------------------------------------------|
| `pk`           | String | Partition key: `EVENT`                                                       |
| `sk`           | String | Sort key: `EVENT#{published_at}-{event_id}`                                  |
| `id`           | String | Event UUID                                                                   |
| `account`      | String | AWS Account ID                                                               |
| `region`       | String | AWS Region                                                                   |
| `source`       | String | Event source                                                                 |
| `detail_type`  | String | Event detail type                                                            |
| `detail`       | String | JSON string of event payload                                                 |
| `severity`     | Number | Severity level (0-5)                                                         |
| `resources`    | String | JSON string of resource ARN array                                            |
| `published_at` | Number | Unix timestamp                                                               |
| `updated_at`   | Number | Unix timestamp                                                               |
| `expired_at`   | Number | Unix timestamp (for TTL)                                                     |
| `gsi1pk`       | String | GSI2 partition key: `SOURCE#{source}`                                        |
| `gsi1sk`       | String | GSI2 sort key: `EVENT#{published_at}-{event_id}`                             |

## Example DynamoDB Record

```json
{
  "pk": "EVENT",
  "sk": "EVENT#1735689600-00000000-0000-0000-0000-000000000000",
  "id": "00000000-0000-0000-0000-000000000000",
  "account": "123456789012",
  "region": "us-east-1",
  "source": "aws.cloudwatch",
  "detail_type": "CloudWatch Alarm State Change",
  "detail": "{\"alarmName\":\"ServerCpuTooHigh\",\"configuration\":{\"description\":\"Goes into alarm when server CPU utilization is too high!\",\"metrics\":[{\"id\":\"30b6c6b2-a864-43a2-4877-c09a1afc3b87\",\"metricStat\":{\"metric\":{\"dimensions\":{\"InstanceId\":\"i-12345678901234567\"},\"name\":\"CPUUtilization\",\"namespace\":\"AWS/EC2\"},\"period\":300,\"stat\":\"Average\"},\"returnData\":true}]},\"state\":{\"reason\":\"Threshold Crossed\",\"value\":\"ALARM\"}}",
  "severity": 3,
  "resources": "[\"arn:aws:cloudwatch:us-east-1:123456789012:alarm:ServerCpuTooHigh\"]",
  "published_at": 1735689600,
  "updated_at": 1735689600,
  "expired_at": 1743465600,
  "gsi1pk": "SOURCE#aws.cloudwatch",
  "gsi1sk": "EVENT#1735689600-00000000-0000-0000-0000-000000000000"
}
```

## Access Patterns

|   | Access Pattern                       | Table/Index | Key Condition                                                         | Notes                           |
|:--|:-------------------------------------|:------------|-----------------------------------------------------------------------|:--------------------------------|
| 1 | Get event by ID                      | Table       | pk=`EVENT` AND sk=`EVENT#{published_at}-{event_id}`                   | Direct lookup (requires timestamp) |
| 2 | List all events                      | Table       | pk=`EVENT`                                                            | All events, sorted by timestamp |
| 3 | List events by time range            | Table       | pk=`EVENT` AND sk BETWEEN `EVENT#{start_time}` AND `EVENT#{end_time}` | Filter by time range            |
| 4 | List events by source                | GSI2        | gsi1pk=`SOURCE#{source}`                                              | All events from source          |
| 5 | List events by source & time range   | GSI2        | gsi1pk=`SOURCE#{source}` AND gsi1sk BETWEEN ranges                    | Source events in time range     |

## Validation Rules

### Account Validation
- Must be exactly 12 digits
- Numeric only
- No spaces or special characters

### Region Validation
- Must be valid AWS region format
- Pattern: `[a-z]{2}-[a-z]+-\d{1}` (e.g., `us-east-1`, `eu-west-1`)

### Source Validation
- Must start with `aws.` prefix for AWS services
- Common sources: `aws.cloudwatch`, `aws.guardduty`, `aws.securityhub`, `aws.ec2`, etc.

### Severity Validation
- Must be integer between 0 and 5
- Default to 0 if not specified

### Detail Validation
- Must be valid JSON object
- Will be serialized to JSON string for storage

### Resources Validation
- Must be array of valid AWS ARN strings
- Can be empty array
- Will be serialized to JSON string for storage

### Timestamp Validation
- `published_at` must be valid Unix timestamp
- `expired_at` defaults to `published_at + 90 days` if not specified

## Business Logic Methods

### Severity Checks
- `is_critical()` - Returns true if severity >= 4
- `is_high_priority()` - Returns true if severity >= 3
- `get_severity_label()` - Returns string label for severity level

### Resource Methods
- `get_resources()` - Returns array of `{type, arn}` objects parsed from resources

### State Checks
- `days_until_expiry()` - Returns number of days until expiration

### Data Access
- `get_detail_field(field_path)` - Extract specific field from detail JSON

## Related Use Cases

- **CreateEvent** - Validate event data, generate UUID, set published_at, calculate expired_at, store event
- **GetEvent** - Fetch event by ID and timestamp
- **ListEvents** - Query events with filters (account, source, time range, severity), paginate results
- **GetEventDetail** - Fetch event and parse detail JSON for display
- **FilterEventsBySeverity** - Query events above certain severity threshold
- **CreateTaskFromEvent** - Create task linked to high-severity event

## TTL (Time To Live)

Events automatically expire after 90 days using DynamoDB TTL feature:

- TTL attribute: `expired_at`
- Default retention: 90 days from `published_at`
- Automatic cleanup by DynamoDB (within 48 hours of expiration)
- Can be customized via MonitoringConfig

## Event Sources

Common AWS event sources:

| Source                | Description                           | Typical Detail Type                    |
|-----------------------|---------------------------------------|----------------------------------------|
| `aws.cloudwatch`      | CloudWatch alarms and metrics         | CloudWatch Alarm State Change          |
| `aws.guardduty`       | GuardDuty security findings           | GuardDuty Finding                      |
| `aws.securityhub`     | Security Hub findings                 | Security Hub Findings - Imported       |
| `aws.ec2`             | EC2 instance state changes            | EC2 Instance State-change Notification |
| `aws.rds`             | RDS database events                   | RDS DB Instance Event                  |
| `aws.lambda`          | Lambda function errors                | Lambda Function Execution State Change |
| `aws.ecs`             | ECS task and service events           | ECS Task State Change                  |
| `aws.s3`              | S3 bucket events                      | Object Created, Object Deleted         |
| `monitoring.logs`     | Crawled logs from CloudWatch Logs     | Monitoring log                         |
| `monitoring.metrics`  | Crawled metrics from CloudWatch Metrics| Monitoring metric                      |
| `monitoring.alerts`   | Crawled alerts from CloudWatch Alarms | Monitoring alerts                      |

## Severity Mapping

Default severity mapping for common event types:

| Event Type                    | Default Severity |
|-------------------------------|------------------|
| CloudWatch ALARM state        | 3 (High)         |
| CloudWatch OK state           | 1 (Low)          |
| GuardDuty High severity       | 4 (Critical)     |
| GuardDuty Medium severity     | 3 (High)         |
| GuardDuty Low severity        | 2 (Medium)       |
| Security Hub Critical         | 5 (Emergency)    |
| EC2 instance terminated       | 2 (Medium)       |
| Lambda function error         | 3 (High)         |
| Monitoring log (ERROR level)  | 3 (High)         |
| Monitoring log (WARN level)   | 2 (Medium)       |
| Monitoring log (INFO level)   | 1 (Low)          |
| Monitoring metric threshold   | 2 (Medium)       |
| Monitoring alert triggered    | 3 (High)         |

**Note:** Severity can be customized via MonitoringConfig service-specific rules.

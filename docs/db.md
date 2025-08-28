# Database Schema Documentation

## 1. Events Table

### Description

The Events Table stores logs of events for each account, sorted by event timestamp. This
table is optimized for querying events within a specific time range.

### DB Schema

| Field          | Type   | Description                                                                  |
|----------------|--------|------------------------------------------------------------------------------|
| `pk`           | String | Partition key: `EVENT`                                                       |
| `sk`           | String | Sort key: `EVENT#{created_at}{event_id}`                                     |
| `account`      | String | AWS Account ID (e.g., `123456789012`)                                        |
| `region`       | String | AWS Region (e.g., `us-east-1`)                                               |
| `source`       | String | Source of the event (e.g., CloudWatch, Lambda)                               |
| `detail`       | String | JSON payload with raw event data                                             |
| `detail_type`  | String | Type of the event detail                                                     |
| `severity`     | Number | Severity level (0=Unknown, 1=Low, 2=Medium, 3=High, 4=Critical)              |
| `resources`    | String | List of resources affected by the event (e.g., ECS task ARN)                 |
| `published_at` | String | ISO timestamp of when the event was created                                  |
| `updated_at`   | String | ISO timestamp of when the event was last updated                             |
| `expired_at`   | String | ISO timestamp of when the event expires (defaults to 90 days after creation) |

### Example Item

#### DynamoDB Item

```json
{
  "severity": 0,
  "detail_type": "CloudWatch Alarm State Change",
  "resources": [
    "arn:aws:cloudwatch:us-east-1:000000000000:alarm:ServerCpuTooHigh"
  ],
  "expired_at": 1736294400,
  "source": "aws.cloudwatch",
  "updated_at": 1756346453,
  "sk": "EVENT#1735689600-00000000-0000-0000-0000-000000000000",
  "pk": "EVENT",
  "detail": "{\"alarmName\": \"ServerCpuTooHigh\", \"configuration\": {\"description\": \"Goes into alarm when server CPU utilization is too high!\", \"metrics\": [{\"id\": \"30b6c6b2-a864-43a2-4877-c09a1afc3b87\", \"metricStat\": {\"metric\": {\"dimensions\": {\"InstanceId\": \"i-12345678901234567\"}, \"name\": \"CPUUtilization\", \"namespace\": \"AWS/EC2\"}, \"period\": 300, \"stat\": \"Average\"}, \"returnData\": true}]}, \"previousState\": {\"reason\": \"Threshold Crossed: 1 out of the last 1 datapoints [0.0666851903306472 (01/10/19 13:46:00)] was not greater than the threshold (50.0) (minimum 1 datapoint for ALARM -> OK transition).\", \"reasonData\": \"{\\\"version\\\":\\\"1.0\\\",\\\"queryDate\\\":\\\"2019-10-01T13:56:40.985+0000\\\",\\\"startDate\\\":\\\"2019-10-01T13:46:00.000+0000\\\",\\\"statistic\\\":\\\"Average\\\",\\\"period\\\":300,\\\"recentDatapoints\\\":[0.0666851903306472],\\\"threshold\\\":50.0}\", \"timestamp\": \"2019-10-01T13:56:40.987+0000\", \"value\": \"OK\"}, \"state\": {\"reason\": \"Threshold Crossed: 1 out of the last 1 datapoints [99.50160229693434 (02/10/19 16:59:00)] was greater than the threshold (50.0) (minimum 1 datapoint for OK -> ALARM transition).\", \"reasonData\": \"{\\\"version\\\":\\\"1.0\\\",\\\"queryDate\\\":\\\"2019-10-02T17:04:40.985+0000\\\",\\\"startDate\\\":\\\"2019-10-02T16:59:00.000+0000\\\",\\\"statistic\\\":\\\"Average\\\",\\\"period\\\":300,\\\"recentDatapoints\\\":[99.50160229693434],\\\"threshold\\\":50.0}\", \"timestamp\": \"2019-10-02T17:04:40.989+0000\", \"value\": \"ALARM\"}}",
  "published_at": 1735689600,
  "region": "us-east-1",
  "account": "000000000000"
}
```

#### Data Model Item

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "account": "000000000000",
  "region": "us-east-1",
  "source": "aws.cloudwatch",
  "detail": {},
  "detail_type": "CloudWatch Alarm State Change",
  "severity": 0,
  "resources": [
    "arn:aws:cloudwatch:us-east-1:000000000000:alarm:ServerCpuTooHigh"
  ],
  "published_at": 1735689600,
  "updated_at": 1756346551
}
```

#### Access patterns

|   | Access Pattern                       | Table/Index | Key Condition                                                         | Notes               |
|:--|:-------------------------------------|:------------|-----------------------------------------------------------------------|:--------------------|
| 2 | List events                          | Table       | pk=`EVENT`                                                            | order by created_at |
| 3 | List events by a specific time range | Table       | pk=`EVENT` AND sk BETWEEN `EVENT#<start_time>` AND `EVENT#<end_time>` | order by created_at |

## 2. Agents Table

### Description

The Agents Table stores information about monitoring agents deployed in each account.

### DB Schema

| Field         | Type    | Description                                                                   |
|---------------|---------|-------------------------------------------------------------------------------|
| `pk`          | String  | Partition key: `AGENT`                                                        |
| `sk`          | String  | Sort key: `AGENT#{AWSAccountId}`                                              |
| `region`      | String  | AWS Region (e.g., `us-east-1`)                                                |
| `status`      | String  | Status of the agent's deployment (e.g., `CREATE_COMPLETE`, `UPDATE_COMPLETE`) |
| `deployed_at` | Integer | Unix timestamp of when the agent was deployed                                 |
| `created_at`  | Integer | Unix timestamp of when the agent was created                                  |

### Example Item

#### DynamoDB Item

```json
{
  "sk": "AGENT#123456789012",
  "pk": "AGENT",
  "region": "us-east-1",
  "status": "CREATE_COMPLETE",
  "deployed_at": 1735689600,
  "created_at": 1735689600
}
```

#### Data Model Item

```json
{
  "account": "123456789012",
  "region": "us-east-1",
  "status": "CREATE_COMPLETE",
  "deployed_at": 1735689600,
  "created_at": 1735689600
}
```

#### Access patterns

|   | Access Pattern       | Table/Index | Key Condition                            | Notes               |
|:--|:---------------------|:------------|------------------------------------------|:--------------------|
| 1 | Get agent by account | Table       | pk=`AGENT` AND sk=`AGENT#{AWSAccountId}` |                     |
| 2 | List all agents      | Table       | pk=`AGENT`                               | order by account id |

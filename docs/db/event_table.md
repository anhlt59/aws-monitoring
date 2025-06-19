# Events Table

## Description

The Events Table stores logs of events for each account, partitioned by account and sorted by event timestamp. This
table is optimized for querying events within a specific time range.

## Schema

| Field         | Type   | Description                                                |
| ------------- | ------ | ---------------------------------------------------------- |
| `pk`          | String | Partition key: `EVENT`                                     |
| `sk`          | String | Sort key: `EVENT#{uuid7}`                                  |
| `gsi1pk`      | String | Sort key: `PROJECT#{project_id}`                           |
| `gsi1sk`      | String | Sort key: `EVENT#{uuid7}`                                  |
| `source`      | String | Source of the event (e.g., CloudWatch, Lambda)             |
| `region`      | String | AWS region where the event occurred                        |
| `detail`      | String | JSON payload with raw event data                           |
| `time`        | String | ISO timestamp of when the event was created                |
| `status`      | String | Issue status (e.g., in_review, in_progress, ignored, done) |
| `assigned_to` | String | User or team assigned to the issue                         |

## Example Item

### DynamoDB Item

```json
{
  "PK": "ACCOUNT#123456789012",
  "SK": "EVENT#20250509T120000Z#evt001",
  "event_type": "ecs.cpu_high",
  "service": "ECS",
  "region": "us-east-1",
  "resource": "arn:aws:ecs:us-east-1:123456789012:service/my-service",
  "details": {
    "cpu_utilization": 95,
    "threshold": 85
  },
  "severity": "critical",
  "crawler": "ECS_Crawler",
  "ttl": 1750000000
}
```

### Data Model Item

```json
{
  "account_id": "123456789012",
  "event_id": "evt001",
  "event_type": "ecs.cpu_high",
  "source": "CloudWatch",
  "payload": {
    "cpu_utilization": 95,
    "threshold": 85
  },
  "created_at": "2025-05-09T12:00:00Z",
  "actor": "ECS_Crawler",
  "resource": {
    "id": "arn:aws:ecs:us-east-1:123456789012:service/my-service"
  },
  "status": "processed"
}
```

### Access patterns

|     | Access Pattern                                | Table/Index | Key Condition                                          | Notes               |
| :-- | :-------------------------------------------- | :---------- | ------------------------------------------------------ | :------------------ |
| 2   | List events for a specific account            | Table       | pk=`ACCOUNT#<account_id>` AND sk=begins_with(`EVENT#`) | order by created_at |
| 3   | List events for a specific account and source | GSI1        | gsi1pk=`ACCOUNT#<account_id>#<source>`                 | order by created_at |
| 4   | List events for a specific account and type   | GSI2        | gsi2pk=`ACCOUNT#<account_id>#<event_type>`             | order by created_at |

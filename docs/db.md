# Database Schema Documentation

## 1. Events Table

### Description

The Events Table stores logs of events for each account, sorted by event timestamp. This
table is optimized for querying events within a specific time range.

### Schema

| Field        | Type   | Description                                                                  |
|--------------|--------|------------------------------------------------------------------------------|
| `pk`         | String | Partition key: `EVENT`                                                       |
| `sk`         | String | Sort key: `EVENT#{created_at}{event_id}`                                     |
| `account`    | String | Account ID (e.g., `123456789012`)                                            |
| `source`     | String | Source of the event (e.g., CloudWatch, Lambda)                               |
| `detail`     | String | JSON payload with raw event data                                             |
| `assigned`   | String | User or team assigned to the issue                                           |
| `status`     | Number | Represents the issue status  (e.g., in_review, in_progress, ignored, done)   |
| `created_at` | String | ISO timestamp of when the event was created                                  |
| `updated_at` | String | ISO timestamp of when the event was last updated                             |
| `expired_at` | String | ISO timestamp of when the event expires (defaults to 90 days after creation) |

### Example Item

#### DynamoDB Item

```json
{
    "PK": "EVENT",
    "SK": "EVENT#1750870811111111111",
    "account": "123456789012",
    "source": "aws.ecs",
    "detail": "{\"event_type\": \"ECS_CPU_HIGH\", \"details\": {\"cpu_utilization\": 95, \"threshold\": 85}}",
    "assigned": "anhlt",
    "status": 1,
    "created_at": "1750870846",
    "updated_at": "1750870846",
    "expired_at": "1758646846"
}
```

#### Data Model Item

```json
{
    "id": "11111111111",
    "account": "123456789012",
    "source": "aws.ecs",
    "detail": "{\"event_type\": \"ECS_CPU_HIGH\", \"details\": {\"cpu_utilization\": 95, \"threshold\": 85}}",
    "assigned": "anhlt",
    "status": 1,
    "created_at": "1750870846",
    "updated_at": "1750870846"
}
```

#### Access patterns

|   | Access Pattern                       | Table/Index | Key Condition                                                         | Notes               |
|:--|:-------------------------------------|:------------|-----------------------------------------------------------------------|:--------------------|
| 2 | List events                          | Table       | pk=`EVENT`                                                            | order by created_at |
| 3 | List events in a specific time range | Table       | pk=`EVENT` AND sk BETWEEN `EVENT#<start_time>` AND `EVENT#<end_time>` | order by created_at |

# TaskComment Model Documentation

The TaskComment model represents comments on tasks, enabling discussion, updates, and collaboration around task resolution.

## Entity Model

| Field        | Type    | Description                                                         |
|--------------|---------|---------------------------------------------------------------------|
| `id`         | String  | Comment UUID (generated on creation)                                |
| `task_id`    | String  | Parent task ID                                                      |
| `user_id`    | String  | User ID who created the comment                                     |
| `user_name`  | String  | Denormalized user name for display                                  |
| `comment`    | String  | Comment text (1-2000 characters)                                    |
| `created_at` | Integer | Unix timestamp of when the comment was created                      |

## Example

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "task_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_name": "John Doe",
  "comment": "I've investigated the GuardDuty finding and confirmed it's a false positive. The access pattern is from our automated backup system.",
  "created_at": 1735693200
}
```

## DynamoDB Schema

| Field        | Type    | Description                                                         |
|--------------|---------|---------------------------------------------------------------------|
| `pk`         | String  | Partition key: `TASK#{task_id}` (groups comments by task)           |
| `sk`         | String  | Sort key: `COMMENT#{created_at}#{comment_id}`                       |
| `comment_id` | String  | Comment UUID                                                        |
| `user_id`    | String  | User ID                                                             |
| `user_name`  | String  | User name (denormalized)                                            |
| `comment`    | String  | Comment text                                                        |
| `created_at` | Number  | Unix timestamp                                                      |

**Note:** Comments are stored with the task_id as the partition key, enabling efficient querying of all comments for a specific task. The sort key uses timestamp to maintain chronological order.

## Example DynamoDB Record

```json
{
  "pk": "TASK#660e8400-e29b-41d4-a716-446655440001",
  "sk": "COMMENT#1735693200#770e8400-e29b-41d4-a716-446655440002",
  "comment_id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_name": "John Doe",
  "comment": "I've investigated the GuardDuty finding and confirmed it's a false positive. The access pattern is from our automated backup system.",
  "created_at": 1735693200
}
```

## Access Patterns

|   | Access Pattern                      | Table/Index | Key Condition                                                  | Notes                            |
|:--|:------------------------------------|:------------|----------------------------------------------------------------|:---------------------------------|
| 1 | Get all comments for a task         | Table       | pk=`TASK#{task_id}` AND sk begins with `COMMENT#`             | Sorted by creation time (oldest first) |
| 2 | Get comments for task in time range | Table       | pk=`TASK#{task_id}` AND sk BETWEEN `COMMENT#{start}` AND `COMMENT#{end}` | Filter by time range             |
| 3 | Get latest N comments for a task    | Table       | pk=`TASK#{task_id}` AND sk begins with `COMMENT#`             | Query in reverse order, limit N  |

## Validation Rules

### Comment Validation
- Strip whitespace
- Minimum 1 character
- Maximum 2000 characters
- Cannot be empty

## Business Logic

### Comment Creation Process
1. Validate comment text
2. Get user name from authenticated user context
3. Create comment with generated UUID
4. Increment parent task's `comment_count`
5. Update parent task's `updated_at` timestamp

### Denormalization Strategy
- User name is denormalized for display performance
- If a user changes their name, existing comments retain the old name (historical accuracy)
- To get current user info, query User table separately if needed

## Related Use Cases

- **AddComment** - Validate text, get user name, create comment, increment task.comment_count
- **GetTaskComments** - Query all comments for task_id, sort by created_at, paginate if needed
- **DeleteComment** (Optional) - Soft or hard delete, decrement task.comment_count, require author or admin permission

## Comment Display Order

Comments are stored and retrieved in chronological order (oldest first) using the sort key structure:

```
COMMENT#{created_at}#{comment_id}
```

Examples:
- `COMMENT#1735689600#770e8400-e29b-41d4-a716-446655440001`
- `COMMENT#1735693200#770e8400-e29b-41d4-a716-446655440002`
- `COMMENT#1735696800#770e8400-e29b-41d4-a716-446655440003`

This ensures that when querying comments for a task, they are automatically returned in the order they were created.

## Example Comment Thread

```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440001",
    "task_id": "660e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_name": "John Doe",
    "comment": "Starting investigation into this GuardDuty finding.",
    "created_at": 1735689600
  },
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "task_id": "660e8400-e29b-41d4-a716-446655440001",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_name": "John Doe",
    "comment": "I've investigated the GuardDuty finding and confirmed it's a false positive. The access pattern is from our automated backup system.",
    "created_at": 1735693200
  },
  {
    "id": "770e8400-e29b-41d4-a716-446655440003",
    "task_id": "660e8400-e29b-41d4-a716-446655440001",
    "user_id": "660e8400-e29b-41d4-a716-446655440005",
    "user_name": "Jane Smith",
    "comment": "Thanks for the update. I've added the backup system IP to the whitelist to prevent future false positives.",
    "created_at": 1735696800
  }
]
```

## Performance Considerations

- **Partition Design**: Comments are partitioned by task_id, preventing hot partitions as comments are distributed across different tasks
- **Sort Key Design**: Using timestamp in the sort key enables efficient range queries and automatic chronological sorting
- **Denormalization**: User names are denormalized to avoid joining with the User table for every comment display
- **Comment Count**: Maintained as a denormalized field on the Task model for efficient display without counting

# Task Model Documentation

The Task model represents work items created from monitoring events or manually created by users. Tasks track issues, incidents, and action items that need to be resolved.

## Entity Model

| Field                | Type         | Description                                                        |
|----------------------|--------------|-------------------------------------------------------------------|
| `id`                 | String       | Task UUID (generated on creation)                                  |
| `title`              | String       | Short description (3-200 characters)                               |
| `description`        | String       | Detailed description (10-5000 characters)                          |
| `status`             | TaskStatus   | Task status: `open`, `in_progress`, or `closed`                    |
| `priority`           | TaskPriority | Priority: `critical`, `high`, `medium`, or `low`                   |
| `assigned_user_id`   | String       | User ID of assignee                                                |
| `assigned_user_name` | String       | Denormalized user name for display (optional)                      |
| `event_id`           | String       | Source event ID if task was created from an event (optional)       |
| `event_details`      | Object       | Denormalized snapshot of event data (optional)                     |
| `due_date`           | Integer      | Unix timestamp for due date (optional)                             |
| `created_at`         | Integer      | Unix timestamp of when task was created                            |
| `updated_at`         | Integer      | Unix timestamp of when task was last updated                       |
| `created_by`         | String       | User ID who created the task                                       |
| `closed_at`          | Integer      | Unix timestamp of when task was closed (optional)                  |
| `comment_count`      | Integer      | Number of comments on this task (denormalized), defaults to 0      |

### TaskStatus Enum

- `open` - Task is open and not yet started
- `in_progress` - Task is being worked on
- `closed` - Task is completed

### TaskPriority Enum

- `critical` - Highest priority, requires immediate attention
- `high` - High priority
- `medium` - Medium priority
- `low` - Low priority

## Event Details Structure

When a task is linked to an event, the `event_details` field contains a snapshot of the event:

```json
{
  "account": "123456789012",
  "region": "us-east-1",
  "source": "aws.guardduty",
  "severity": "critical",
  "detail_type": "GuardDuty Finding"
}
```

## Example

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Investigate GuardDuty Critical Finding",
  "description": "A critical GuardDuty finding was detected indicating potential unauthorized access to an S3 bucket. Need to investigate the source IP and validate access patterns.",
  "status": "open",
  "priority": "critical",
  "assigned_user_id": "550e8400-e29b-41d4-a716-446655440000",
  "assigned_user_name": "John Doe",
  "event_id": "00000000-0000-0000-0000-000000000001",
  "event_details": {
    "account": "123456789012",
    "region": "us-east-1",
    "source": "aws.guardduty",
    "severity": "critical",
    "detail_type": "GuardDuty Finding"
  },
  "due_date": 1735862400,
  "created_at": 1735689600,
  "updated_at": 1735689600,
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "closed_at": null,
  "comment_count": 3
}
```

## DynamoDB Schema

| Field                | Type      | Description                                                    |
|----------------------|-----------|----------------------------------------------------------------|
| `pk`                 | String    | Partition key: `TASK`                                          |
| `sk`                 | String    | Sort key: `TASK#{task_id}`                                     |
| `title`              | String    | Task title                                                     |
| `description`        | String    | Task description                                               |
| `status`             | String    | Task status                                                    |
| `priority`           | String    | Task priority                                                  |
| `assigned_user_id`   | String    | Assigned user ID                                               |
| `assigned_user_name` | String    | Assigned user name (denormalized)                              |
| `event_id`           | String    | Source event ID (optional)                                     |
| `event_details`      | String    | JSON string of event snapshot (optional)                       |
| `due_date`           | Number    | Unix timestamp (optional)                                      |
| `created_at`         | Number    | Unix timestamp                                                 |
| `updated_at`         | Number    | Unix timestamp                                                 |
| `created_by`         | String    | Creator user ID                                                |
| `closed_at`          | Number    | Unix timestamp (optional)                                      |
| `comment_count`      | Number    | Comment count                                                  |
| `assigned_pk`        | String    | GSI1 partition key: `ASSIGNED#{user_id}`                       |
| `assigned_sk`        | String    | GSI1 sort key: `STATUS#{status}#PRIORITY#{priority}#TASK#{id}` |
| `status_pk`          | String    | GSI2 partition key: `STATUS#{status}`                          |
| `status_sk`          | String    | GSI2 sort key: `CREATED#{created_at}#TASK#{id}`                |
| `event_pk`           | String    | GSI3 partition key: `EVENT#{event_id}`                         |
| `event_sk`           | String    | GSI3 sort key: `TASK#{id}`                                     |

## Example DynamoDB Record

```json
{
  "pk": "TASK",
  "sk": "TASK#660e8400-e29b-41d4-a716-446655440001",
  "title": "Investigate GuardDuty Critical Finding",
  "description": "A critical GuardDuty finding was detected indicating potential unauthorized access to an S3 bucket. Need to investigate the source IP and validate access patterns.",
  "status": "open",
  "priority": "critical",
  "assigned_user_id": "550e8400-e29b-41d4-a716-446655440000",
  "assigned_user_name": "John Doe",
  "event_id": "00000000-0000-0000-0000-000000000001",
  "event_details": "{\"account\":\"123456789012\",\"region\":\"us-east-1\",\"source\":\"aws.guardduty\",\"severity\":\"critical\",\"detail_type\":\"GuardDuty Finding\"}",
  "due_date": 1735862400,
  "created_at": 1735689600,
  "updated_at": 1735689600,
  "created_by": "550e8400-e29b-41d4-a716-446655440000",
  "closed_at": null,
  "comment_count": 3,
  "assigned_pk": "ASSIGNED#550e8400-e29b-41d4-a716-446655440000",
  "assigned_sk": "STATUS#open#PRIORITY#critical#TASK#660e8400-e29b-41d4-a716-446655440001",
  "status_pk": "STATUS#open",
  "status_sk": "CREATED#1735689600#TASK#660e8400-e29b-41d4-a716-446655440001",
  "event_pk": "EVENT#00000000-0000-0000-0000-000000000001",
  "event_sk": "TASK#660e8400-e29b-41d4-a716-446655440001"
}
```

## Access Patterns

|   | Access Pattern                    | Table/Index | Key Condition                                                | Notes                           |
|:--|:----------------------------------|:------------|--------------------------------------------------------------|:--------------------------------|
| 1 | Get task by ID                    | Table       | pk=`TASK` AND sk=`TASK#{task_id}`                            | Direct lookup                   |
| 2 | List all tasks                    | Table       | pk=`TASK`                                                    | All tasks, sorted by ID         |
| 3 | Get my tasks (by assigned user)   | GSI1        | assigned_pk=`ASSIGNED#{user_id}`                             | Sorted by status & priority     |
| 4 | Get my tasks by status            | GSI1        | assigned_pk=`ASSIGNED#{user_id}` AND assigned_sk begins with `STATUS#{status}#` | User tasks filtered by status   |
| 5 | List tasks by status              | GSI2        | status_pk=`STATUS#{status}`                                  | Sorted by creation time         |
| 6 | List tasks by status & date range | GSI2        | status_pk=`STATUS#{status}` AND status_sk BETWEEN ranges     | Filter by status and time range |
| 7 | Get tasks for an event            | GSI3        | event_pk=`EVENT#{event_id}`                                  | All tasks linked to an event    |

## Validation Rules

### Title Validation
- Strip whitespace
- Minimum 3 characters
- Maximum 200 characters

### Description Validation
- Strip whitespace
- Minimum 10 characters
- Maximum 5000 characters

### Due Date Validation
- Must be in the future (or null)
- Cannot be before created_at

### Status Transition Rules
- When status changes to `closed`, set `closed_at` to current timestamp
- When reopening (status changes from `closed` to any other), clear `closed_at`

## Business Logic Methods

### Status Checks
- `is_open` - Returns true if status is `open`
- `is_closed` - Returns true if status is `closed`
- `is_overdue` - Returns true if task has a due_date in the past and is not closed

### State Mutations
- `update_status(new_status)` - Update status and manage closed_at timestamp
- `assign_to_user(user_id, user_name)` - Assign task to a user
- `increment_comment_count()` - Increment comment count (called when comment is added)
- `link_to_event(event_id, event_details)` - Link task to a source event

## Related Use Cases

- **CreateTask** - Validate fields, set status to OPEN, assign to user, generate UUID
- **GetTask** - Fetch task by ID, optionally include comments
- **UpdateTask** - Validate permissions, update fields, track status changes
- **DeleteTask** - Soft or hard delete, require admin permission
- **ListTasks** - Filter by status/priority/assigned_user/event_id/date range, paginate
- **CreateTaskFromEvent** - Fetch event, pre-fill description, link to event, set priority based on severity
- **UpdateTaskStatus** - Change status, track history, update timestamps
- **AssignTask** - Assign to user, update user name (denormalized)

## Priority Mapping from Event Severity

When creating a task from an event, priority can be mapped from event severity:

| Event Severity | Task Priority |
|----------------|---------------|
| critical       | critical      |
| high           | high          |
| medium         | medium        |
| low            | low           |
| info           | low           |

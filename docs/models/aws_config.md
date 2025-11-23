# AWS Config Model Documentation

The AWS Config model represents AWS accounts being monitored by the system. This model replaces the previous "Agent" model and includes deployment/monitoring status tracking.

**Note:** AWS credentials (access keys) are stored in the monitoring profile, not in this model.

## Entity Model

| Field          | Type            | Description                                                     |
|----------------|-----------------|-----------------------------------------------------------------|
| `id`           | String          | Configuration UUID (not AWS account ID)                         |
| `account_id`   | String          | AWS Account ID (12 digits)                                      |
| `account_name` | String          | Friendly name for the account                                   |
| `region`       | String          | Primary AWS region (e.g., `us-east-1`)                          |
| `role_arn`     | String          | IAM role ARN for cross-account access (optional)                |
| `status`       | AwsConfigStatus | Deployment/monitoring status                                    |
| `deployed_at`  | Integer         | Unix timestamp when monitoring was deployed (optional)          |
| `last_sync`    | Integer         | Unix timestamp of last successful connection test (optional)    |
| `is_active`    | Boolean         | Monitoring enabled/disabled, defaults to `true`                 |
| `created_at`   | Integer         | Unix timestamp of when config was registered                    |
| `updated_at`   | Integer         | Unix timestamp of when config was last updated                  |

### AwsConfigStatus Enum

- `pending` - Account registered, deployment not started
- `deploying` - Deployment in progress
- `active` - Deployed and actively monitoring
- `failed` - Deployment failed
- `disabled` - Monitoring disabled

## Example

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "account_id": "123456789012",
  "account_name": "Production AWS Account",
  "region": "us-east-1",
  "role_arn": "arn:aws:iam::123456789012:role/MonitoringRole",
  "status": "active",
  "deployed_at": 1735689600,
  "last_sync": 1735776000,
  "is_active": true,
  "created_at": 1735689600,
  "updated_at": 1735776000
}
```

## DynamoDB Schema

| Field          | Type    | Description                                   |
|----------------|---------|-----------------------------------------------|
| `pk`           | String  | Partition key: `CONFIG`                       |
| `sk`           | String  | Sort key: `AWS#{id}`                          |
| `account_id`   | String  | AWS Account ID                                |
| `account_name` | String  | Friendly name                                 |
| `region`       | String  | AWS region                                    |
| `role_arn`     | String  | IAM role ARN (optional)                       |
| `status`       | String  | Account status                                |
| `deployed_at`  | Number  | Unix timestamp (optional)                     |
| `last_sync`    | Number  | Unix timestamp (optional)                     |
| `is_active`    | Boolean | Monitoring enabled                            |
| `created_at`   | Number  | Unix timestamp                                |
| `updated_at`   | Number  | Unix timestamp                                |
| `gsi1pk`       | String  | GSI1 partition key: `ACCOUNT_ID#{account_id}` |
| `gsi1sk`       | String  | GSI1 sort key: `AWS#{id}`                     |

## Example DynamoDB Record

```json
{
  "pk": "CONFIG",
  "sk": "AWS#880e8400-e29b-41d4-a716-446655440003",
  "account_id": "123456789012",
  "account_name": "Production AWS Account",
  "region": "us-east-1",
  "role_arn": "arn:aws:iam::123456789012:role/MonitoringRole",
  "status": "active",
  "deployed_at": 1735689600,
  "last_sync": 1735776000,
  "is_active": true,
  "created_at": 1735689600,
  "updated_at": 1735776000,
  "gsi1pk": "ACCOUNT_ID#123456789012",
  "gsi1sk": "AWS#880e8400-e29b-41d4-a716-446655440003"
}
```

## Access Patterns

|   | Access Pattern                   | Table/Index | Key Condition                                                    | Notes                   |
|:--|:---------------------------------|:------------|------------------------------------------------------------------|:------------------------|
| 1 | Get AWS config by ID             | Table       | pk=`CONFIG` AND sk=`AWS#{id}`                                    | Direct lookup by ID     |
| 2 | List all AWS configs             | Table       | pk=`CONFIG` AND sk begins with `AWS#`                            | All registered accounts |
| 3 | Get AWS config by account ID     | GSI1        | gsi1pk=`ACCOUNT_ID#{account_id}`                                 | Lookup by AWS account ID|
| 4 | List active AWS configs          | Table       | pk=`CONFIG` AND sk begins with `AWS#` with filter is_active=true | Only active accounts |

## Validation Rules

### Account ID Validation
- Must be exactly 12 digits
- Numeric only
- No spaces or special characters

### Region Validation
- Must be valid AWS region format
- Pattern: `[a-z]{2}-[a-z]+-\d{1}` (e.g., `us-east-1`, `eu-west-1`)

### Role ARN Validation
- Must be valid IAM role ARN format if provided
- Pattern: `arn:aws:iam::{account_id}:role/{role_name}`
- Optional field

## Business Logic Methods

### Status Checks
- `is_deployed()` - Returns true if status is `active`
- `is_pending_deployment()` - Returns true if status is `pending` or `deploying`

### State Mutations
- `mark_deployed()` - Set status to `active`, update deployed_at timestamp
- `mark_deployment_failed()` - Set status to `failed`
- `disable_monitoring()` - Set status to `disabled`, set is_active to false
- `enable_monitoring()` - Set status to `active` (if previously deployed), set is_active to true
- `update_last_sync(success)` - Update last_sync timestamp if successful

## Related Use Cases

- **RegisterAwsConfig** - Validate account_id, validate region, create configuration, set status to `pending`
- **UpdateConfigStatus** - Update deployment status, track deployed_at timestamp
- **TestConnection** - Verify connection using monitoring profile credentials, update last_sync timestamp
- **UpdateAwsConfig** - Update config settings (account_name, region, role_arn)
- **EnableMonitoring** - Activate monitoring for the account
- **DisableMonitoring** - Deactivate monitoring (soft disable)
- **DeleteAwsConfig** - Remove config (hard delete or soft disable)

## Status Lifecycle

```
pending → deploying → active
                ↓
              failed

active ↔ disabled (manual toggle)
```

1. **pending**: Account is registered but monitoring is not deployed
2. **deploying**: Deployment process is in progress
3. **active**: Monitoring is successfully deployed and running
4. **failed**: Deployment failed, requires intervention
5. **disabled**: Monitoring is manually disabled (can be re-enabled)

## Authentication Strategy

AWS credentials are **not stored** in this model. Instead:

- **Monitoring Profile**: AWS credentials (access keys or session tokens) are stored securely in the AWS monitoring profile configuration
- **IAM Role** (Optional): If using cross-account access, the `role_arn` field specifies which IAM role to assume
- **Credential Management**: The monitoring service retrieves credentials from the profile when connecting to AWS

### Authentication Flow

1. System reads AWS config to get `account_id` and `role_arn`
2. System retrieves credentials from monitoring profile (stored separately)
3. If `role_arn` is provided, system assumes the role using the profile credentials
4. If no `role_arn`, system uses profile credentials directly

This approach:
- ✅ Keeps sensitive credentials out of the database
- ✅ Follows AWS best practices for credential management
- ✅ Allows centralized credential rotation via profile updates
- ✅ Supports both direct access and cross-account (role assumption) patterns

## Migration from Agent Model

This model replaces the previous "Agent" model. Key changes:

### Added Fields
- `status` - Tracks deployment/monitoring status (replaces agent status)
- `deployed_at` - Timestamp of deployment
- `account_name` - Friendly name for the account

### Removed Fields
- `access_key_id` - Moved to monitoring profile
- `secret_access_key` - Moved to monitoring profile

### Renamed/Restructured
- Agent's health/status tracking → `status` field with more granular states
- Agent deployment info → `deployed_at`, `last_sync` fields
- Model name: AwsAccount → AwsConfig

### Same Fields
- `account_id` - AWS Account ID
- `region` - Primary region
- `role_arn` - IAM role for cross-account access
- `is_active` - Enable/disable flag
- `created_at`, `updated_at` - Timestamps

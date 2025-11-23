# AWS Account Model Documentation

The AWS Account model represents AWS accounts being monitored by the system. This model replaces the previous "Agent" model and includes deployment/monitoring status tracking.

## Entity Model

| Field               | Type              | Description                                                     |
|---------------------|-------------------|-----------------------------------------------------------------|
| `id`                | String            | Configuration UUID (not AWS account ID)                         |
| `account_id`        | String            | AWS Account ID (12 digits)                                      |
| `account_name`      | String            | Friendly name for the account                                   |
| `region`            | String            | Primary AWS region (e.g., `us-east-1`)                          |
| `access_key_id`     | String            | AWS access key (encrypted, optional)                            |
| `secret_access_key` | String            | AWS secret key (encrypted, optional)                            |
| `role_arn`          | String            | IAM role ARN (preferred authentication method, optional)        |
| `status`            | AwsAccountStatus  | Deployment/monitoring status                                    |
| `deployed_at`       | Integer           | Unix timestamp when monitoring was deployed (optional)          |
| `last_sync`         | Integer           | Unix timestamp of last successful connection test (optional)    |
| `is_active`         | Boolean           | Monitoring enabled/disabled, defaults to `true`                 |
| `created_at`        | Integer           | Unix timestamp of when account was registered                   |
| `updated_at`        | Integer           | Unix timestamp of when account was last updated                 |

### AwsAccountStatus Enum

- `pending` - Account registered, deployment not started
- `deploying` - Deployment in progress
- `active` - Deployed and actively monitoring
- `failed` - Deployment failed
- `disabled` - Monitoring disabled

### Authentication Methods

The model supports two authentication methods (must have one):

1. **IAM Role** (Preferred): `role_arn`
2. **Access Keys**: `access_key_id` + `secret_access_key`

## Example

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "account_id": "123456789012",
  "account_name": "Production AWS Account",
  "region": "us-east-1",
  "access_key_id": null,
  "secret_access_key": null,
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

| Field               | Type      | Description                                                    |
|---------------------|-----------|----------------------------------------------------------------|
| `pk`                | String    | Partition key: `CONFIG`                                        |
| `sk`                | String    | Sort key: `AWS_ACCOUNT#{id}`                                   |
| `account_id`        | String    | AWS Account ID                                                 |
| `account_name`      | String    | Friendly name                                                  |
| `region`            | String    | AWS region                                                     |
| `access_key_id`     | String    | AWS access key (encrypted)                                     |
| `secret_access_key` | String    | AWS secret key (encrypted)                                     |
| `role_arn`          | String    | IAM role ARN                                                   |
| `status`            | String    | Account status                                                 |
| `deployed_at`       | Number    | Unix timestamp (optional)                                      |
| `last_sync`         | Number    | Unix timestamp (optional)                                      |
| `is_active`         | Boolean   | Monitoring enabled                                             |
| `created_at`        | Number    | Unix timestamp                                                 |
| `updated_at`        | Number    | Unix timestamp                                                 |
| `account_pk`        | String    | GSI1 partition key: `ACCOUNT_ID#{account_id}`                  |
| `account_sk`        | String    | GSI1 sort key: `AWS_ACCOUNT#{id}`                              |

## Example DynamoDB Record

```json
{
  "pk": "CONFIG",
  "sk": "AWS_ACCOUNT#880e8400-e29b-41d4-a716-446655440003",
  "account_id": "123456789012",
  "account_name": "Production AWS Account",
  "region": "us-east-1",
  "access_key_id": null,
  "secret_access_key": null,
  "role_arn": "arn:aws:iam::123456789012:role/MonitoringRole",
  "status": "active",
  "deployed_at": 1735689600,
  "last_sync": 1735776000,
  "is_active": true,
  "created_at": 1735689600,
  "updated_at": 1735776000,
  "account_pk": "ACCOUNT_ID#123456789012",
  "account_sk": "AWS_ACCOUNT#880e8400-e29b-41d4-a716-446655440003"
}
```

## Access Patterns

|   | Access Pattern                      | Table/Index | Key Condition                                                  | Notes                          |
|:--|:------------------------------------|:------------|----------------------------------------------------------------|:-------------------------------|
| 1 | Get AWS account by config ID        | Table       | pk=`CONFIG` AND sk=`AWS_ACCOUNT#{id}`                          | Direct lookup by config ID     |
| 2 | List all AWS accounts               | Table       | pk=`CONFIG` AND sk begins with `AWS_ACCOUNT#`                  | All registered accounts        |
| 3 | Get AWS account by account ID       | GSI1        | account_pk=`ACCOUNT_ID#{account_id}`                           | Lookup by AWS account ID       |
| 4 | List active AWS accounts            | Table       | pk=`CONFIG` AND sk begins with `AWS_ACCOUNT#` with filter is_active=true | Only active accounts |

## Validation Rules

### Account ID Validation
- Must be exactly 12 digits
- Numeric only
- No spaces or special characters

### Region Validation
- Must be valid AWS region format
- Pattern: `[a-z]{2}-[a-z]+-\d{1}` (e.g., `us-east-1`, `eu-west-1`)

### Credentials Validation
- Must have either:
  - `access_key_id` AND `secret_access_key`
  - OR `role_arn`
- Cannot have neither
- Can have both, but role_arn takes precedence

### Security Considerations
- Credentials (`access_key_id`, `secret_access_key`) must be encrypted at rest
- Use AWS KMS or similar for encryption
- Never log or expose credentials in API responses
- Use `mask_credentials()` method for safe display

## Business Logic Methods

### Authentication Type Checks
- `uses_role_auth()` - Returns true if using IAM role authentication
- `uses_key_auth()` - Returns true if using access key authentication

### Status Checks
- `is_deployed()` - Returns true if status is `active`
- `is_pending_deployment()` - Returns true if status is `pending` or `deploying`

### State Mutations
- `mark_deployed()` - Set status to `active`, update deployed_at timestamp
- `mark_deployment_failed()` - Set status to `failed`
- `disable_monitoring()` - Set status to `disabled`, set is_active to false
- `enable_monitoring()` - Set status to `active` (if previously deployed), set is_active to true
- `update_last_sync(success)` - Update last_sync timestamp if successful

### Security Methods
- `mask_credentials()` - Return account info with masked credentials for safe display

## Related Use Cases

- **RegisterAwsAccount** - Validate account_id, validate credentials, create configuration, set status to `pending`
- **UpdateAccountStatus** - Update deployment status, track deployed_at timestamp
- **TestConnection** - Verify credentials, update last_sync timestamp
- **UpdateMonitoringConfig** - Update account settings, credentials (re-encrypt if changed)
- **EnableService** - Activate monitoring for the account
- **DisableService** - Deactivate monitoring (soft disable)
- **DeleteAccount** - Remove account configuration (hard delete or soft disable)

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

## Masked Credentials Example

When displaying account information to users, credentials should be masked:

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "account_id": "123456789012",
  "account_name": "Production AWS Account",
  "region": "us-east-1",
  "access_key_id": "AKIA...XYZ",
  "secret_access_key": "***REDACTED***",
  "role_arn": "arn:aws:iam::123456789012:role/MonitoringRole",
  "status": "active",
  "deployed_at": 1735689600,
  "last_sync": 1735776000,
  "is_active": true,
  "created_at": 1735689600,
  "updated_at": 1735776000
}
```

## Migration from Agent Model

This model replaces the previous "Agent" model. Key changes:

### Added Fields
- `status` - Tracks deployment/monitoring status (replaces agent status)
- `deployed_at` - Timestamp of deployment
- `account_name` - Friendly name for the account

### Renamed/Restructured
- Agent's health/status tracking → `status` field with more granular states
- Agent deployment info → `deployed_at`, `last_sync` fields

### Same Fields
- `account_id` - AWS Account ID
- `region` - Primary region
- `access_key_id`, `secret_access_key`, `role_arn` - Authentication
- `is_active` - Enable/disable flag
- `created_at`, `updated_at` - Timestamps

## Example: Account with Access Keys (Encrypted)

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440004",
  "account_id": "987654321098",
  "account_name": "Development AWS Account",
  "region": "eu-west-1",
  "access_key_id": "AKIAIOSFODNN7EXAMPLE",
  "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "role_arn": null,
  "status": "active",
  "deployed_at": 1735689600,
  "last_sync": 1735776000,
  "is_active": true,
  "created_at": 1735689600,
  "updated_at": 1735776000
}
```

**Note:** In actual storage, `access_key_id` and `secret_access_key` would be encrypted using AWS KMS or similar encryption service.

# User Model Documentation

The User model handles authentication and authorization for the AWS monitoring system. Users can have different roles (
admin, manager, user) with hierarchical permissions.

## Entity Model

| Field           | Type     | Description                                      |
|-----------------|----------|--------------------------------------------------|
| `id`            | String   | User UUIDv7 (generated on creation)              |
| `email`         | String   | Unique email address (lowercase, validated)      |
| `full_name`     | String   | Display name (2-100 characters)                  |
| `password_hash` | String   | Bcrypt hashed password (never exposed in API)    |
| `role`          | UserRole | User role: `admin` or `user`                     |
| `created_at`    | Integer  | Unix timestamp of when the user was created      |
| `updated_at`    | Integer  | Unix timestamp of when the user was last updated |
| `last_login`    | Integer  | Unix timestamp of last login (optional)          |

### UserRole Enum

- `user` - Manage tasks, view own profile, view events
- `admin` - Full access

**Permission Hierarchy:** admin > manager > user

## Example

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "password_hash": "$2b$12$KpBGJEKJXx5wqPKOkXz2fOqYJC4Z7K8lXJQsXJqJwJqJqJqJqJqJq",
  "role": "manager",
  "created_at": 1735689600,
  "updated_at": 1735689600
}
```

## DynamoDB Schema

| Field           | Type    | Description                       |
|-----------------|---------|-----------------------------------|
| `pk`            | String  | Partition key: `USER`             |
| `sk`            | String  | Sort key: `USER#{user_id}`        |
| `email`         | String  | Email address                     |
| `full_name`     | String  | Display name                      |
| `password_hash` | String  | Bcrypt hashed password            |
| `role`          | String  | User role                         |
| `created_at`    | Number  | Unix timestamp                    |
| `updated_at`    | Number  | Unix timestamp                    |
| `gsi1pk`        | String  | GSI1 partition key: `EMAIL`       |
| `gsi1sk`        | String  | GSI1 sort key: `EMAIL#{email}`    |
| `gsi2pk`        | String  | GSI2 partition key: `ROLE#{role}` |
| `gsi2sk`        | String  | GSI2 sort key: `USER#{user_id}`   |

## Example DynamoDB Record

```json
{
  "pk": "USER",
  "sk": "USER#550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "password_hash": "$2b$12$KpBGJEKJXx5wqPKOkXz2fOqYJC4Z7K8lXJQsXJqJwJqJqJqJqJqJq",
  "role": "manager",
  "created_at": 1735689600,
  "updated_at": 1735689600,
  "gsi1pk": "EMAIL",
  "gsi1sk": "john.doe@example.com",
  "gsi2pk": "ROLE#manager",
  "gsi2sk": "USER#550e8400-e29b-41d4-a716-446655440000"
}
```

## Access Patterns

|   | Access Pattern            | Table/Index | Key Condition                                    | Notes                                |
|:--|:--------------------------|:------------|--------------------------------------------------|:-------------------------------------|
| 1 | Get user by ID            | Table       | pk=`USER` AND sk=`USER#{user_id}`                | Direct lookup                        |
| 2 | Get user by email (login) | GSI1        | email_pk=`EMAIL` AND email_sk=`EMAIL#{email}`    | For authentication                   |
| 3 | List all users            | Table       | pk=`USER`                                        | Returns all users order by create_at |
| 4 | List users by role        | GSI2        | role_pk=`ROLE#{role}`                            | Filter by role order by create_at    |

## Validation Rules

### Email Validation
- Convert to lowercase
- Strip whitespace
- Must contain `@` and domain with `.`
- Must be unique (enforced at repository layer)

### Full Name Validation
- Strip whitespace
- Minimum 2 characters
- Maximum 100 characters

### Password Requirements
- Hashed using bcrypt with cost factor 12
- Never returned in API responses
- Auto-generated if not provided during creation

## Business Logic Methods

### Permission Methods
- `has_permission(required_role)` - Check if user has required permission level
- `is_admin()` - Check if user is an admin

## Related Use Cases

- **CreateUser** - Validate email uniqueness, hash password, generate UUID (admin only)
- **AuthenticateUser** - Find by email, verify password, generate JWT
- **GetUserProfile** - Fetch user, convert to profile (exclude password_hash)
- **UpdateUser** - Validate permissions, update fields, hash password if changed
- **DeleteUser** - Validate permissions, remove user record
- **ListUsers** - Filter by role, search by email, paginate

## UserDTO (API Response)

The UserDTO model is used for API responses and excludes sensitive data:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "role": "manager",
  "is_active": true,
  "created_at": 1735689600
}
```

### Permission by Role

**User:**
- full access events
- full access tasks
- read user profile
- read monitoring config

**Admin:**
- full access all resources

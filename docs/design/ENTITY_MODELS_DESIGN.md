# Entity Models Design

Comprehensive design for User, Task, TaskComment, and Configuration domain models following the hexagonal architecture pattern used in the AWS Monitoring backend.

**Architecture Pattern:** Domain-Driven Design (DDD) with Pydantic BaseModel
**Reference:** Existing Event and Agent models in `backend/src/domain/models/`

---

## 1. User Entity Model

### 1.1 Domain Model

**File:** `backend/src/domain/models/user.py`

```python
class UserRole(str, Enum):
    """User role enumeration with permission hierarchy."""
    ADMIN = "admin"      # Full system access
    MANAGER = "manager"  # Can manage tasks, view all users
    USER = "user"        # Basic access, own tasks only

class User(BaseModel):
    """User domain model for authentication and authorization."""

    # Identity
    id: str                    # User UUID (generated on creation)
    email: str                 # Unique, lowercase, validated
    full_name: str             # Display name
    password_hash: str         # Bcrypt hashed password (never exposed in API)

    # Authorization
    role: UserRole             # User role (admin/manager/user)
    is_active: bool = True     # Account status (for soft delete)

    # Timestamps
    created_at: int = Field(default_factory=current_utc_timestamp)
    updated_at: int = Field(default_factory=current_utc_timestamp)
    last_login: int | None = None  # Unix timestamp of last login

    # DynamoDB key
    @property
    def persistence_id(self) -> str:
        return self.id  # SK: USER#{id}
```

### 1.2 Validation Rules

```python
@field_validator("email")
@classmethod
def validate_email(cls, value: str) -> str:
    """
    - Convert to lowercase
    - Strip whitespace
    - Validate format: must contain @ and domain
    - Check uniqueness (handled by repository layer)
    """
    value = value.lower().strip()
    if "@" not in value or "." not in value.split("@")[1]:
        raise ValueError("Invalid email format")
    return value

@field_validator("full_name")
@classmethod
def validate_full_name(cls, value: str) -> str:
    """
    - Strip whitespace
    - Minimum 2 characters
    - Maximum 100 characters
    """
    value = value.strip()
    if len(value) < 2:
        raise ValueError("Full name must be at least 2 characters")
    if len(value) > 100:
        raise ValueError("Full name cannot exceed 100 characters")
    return value
```

### 1.3 Business Logic Methods

```python
def has_permission(self, required_role: UserRole) -> bool:
    """
    Check if user has required permission level.
    Permission hierarchy: admin > manager > user
    """
    role_hierarchy = {
        UserRole.ADMIN: 3,
        UserRole.MANAGER: 2,
        UserRole.USER: 1,
    }
    return role_hierarchy[self.role] >= role_hierarchy[required_role]

def is_admin(self) -> bool:
    """Check if user is an admin."""
    return self.role == UserRole.ADMIN

def is_manager_or_above(self) -> bool:
    """Check if user is manager or admin."""
    return self.role in (UserRole.ADMIN, UserRole.MANAGER)

def update_last_login(self) -> None:
    """Update last login timestamp to current time."""
    self.last_login = current_utc_timestamp()
    self.updated_at = current_utc_timestamp()
```

### 1.4 Related Models

#### UserProfile (API Response Model)

```python
class UserProfile(BaseModel):
    """
    User profile for API responses.
    Excludes sensitive data (password_hash).
    Includes computed permissions.
    """
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: int
    last_login: int | None = None
    permissions: list[str] = []  # Computed from role

    @classmethod
    def from_user(cls, user: User) -> "UserProfile":
        """Create profile from User entity."""
        permissions = cls._get_permissions_for_role(user.role)
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login,
            permissions=permissions,
        )

    @staticmethod
    def _get_permissions_for_role(role: UserRole) -> list[str]:
        """Get permissions based on role."""
        # Base permissions (all users)
        base = [
            "read:events",
            "read:own_tasks",
            "update:own_tasks",
            "read:own_profile",
            "update:own_profile",
        ]

        # Manager permissions
        manager = base + [
            "read:all_tasks",
            "create:tasks",
            "update:tasks",
            "delete:own_tasks",
            "read:users",
        ]

        # Admin permissions
        admin = manager + [
            "create:users",
            "update:users",
            "delete:users",
            "delete:events",
            "delete:tasks",
            "read:config",
            "update:config",
        ]

        if role == UserRole.ADMIN:
            return admin
        elif role == UserRole.MANAGER:
            return manager
        else:
            return base
```

### 1.5 DynamoDB Schema

**Table:** Single table design with `EventsTable`

```python
# Partition Key (PK): USER
# Sort Key (SK): USER#{user_id}
# GSI1-PK: EMAIL#{email}  (for login lookup)
# GSI1-SK: USER#{user_id}
# GSI2-PK: ROLE#{role}    (for role filtering)
# GSI2-SK: USER#{user_id}

class UserPersistence(DynamoModel, discriminator="USER"):
    pk = KeyAttribute(hash_key=True, default="USER")
    sk = KeyAttribute(range_key=True, prefix="USER#")

    # User fields
    email = UnicodeAttribute(null=False)
    full_name = UnicodeAttribute(null=False)
    password_hash = UnicodeAttribute(null=False)
    role = UnicodeAttribute(null=False)
    is_active = BooleanAttribute(default=True)

    # Timestamps
    created_at = NumberAttribute(null=False)
    updated_at = NumberAttribute(null=False)
    last_login = NumberAttribute(null=True)

    # GSI for email lookup
    email_pk = KeyAttribute(default_factory=lambda: "EMAIL")
    email_sk = KeyAttribute(default_factory=lambda self: self.email)

    # GSI for role filtering
    role_pk = KeyAttribute(default_factory=lambda self: f"ROLE#{self.role}")
    role_sk = KeyAttribute(default_factory=lambda self: f"USER#{self.sk}")
```

### 1.6 Use Cases

```
CreateUser
- Validate email uniqueness
- Hash password with bcrypt
- Generate UUID
- Set default role (USER)
- Create user in database

AuthenticateUser (Login)
- Find user by email
- Verify password hash
- Update last_login timestamp
- Generate JWT tokens (access + refresh)

GetUserProfile
- Fetch user by ID
- Convert to UserProfile (exclude password_hash)
- Return profile with permissions

UpdateUser
- Validate permissions (self or admin)
- Update allowed fields
- Hash password if changed
- Update updated_at timestamp

DeactivateUser (Soft Delete)
- Set is_active = False
- Prevent login
- Keep data for audit

ListUsers
- Filter by role, is_active
- Search by email/name
- Paginate results
- Require manager+ role
```

---

## 2. Task Entity Model

### 2.1 Domain Model

**File:** `backend/src/domain/models/task.py`

```python
class TaskStatus(str, Enum):
    """Task status enumeration."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

class TaskPriority(str, Enum):
    """Task priority enumeration."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Task(BaseModel):
    """
    Task domain model.
    Represents work items created from events or manually.
    """

    # Identity
    id: str                           # Task UUID
    title: str                        # Short description (3-200 chars)
    description: str                  # Detailed description (10-5000 chars)

    # Status & Priority
    status: TaskStatus = TaskStatus.OPEN
    priority: TaskPriority

    # Assignment
    assigned_user_id: str             # User ID
    assigned_user_name: str | None = None  # Denormalized for display

    # Event Link (Optional)
    event_id: str | None = None       # Source event ID
    event_details: dict | None = None # Denormalized event info
    # event_details structure:
    # {
    #   "account": "123456789012",
    #   "region": "us-east-1",
    #   "source": "aws.guardduty",
    #   "severity": "critical"
    # }

    # Scheduling
    due_date: int | None = None       # Unix timestamp (optional)

    # Timestamps
    created_at: int = Field(default_factory=current_utc_timestamp)
    updated_at: int = Field(default_factory=current_utc_timestamp)
    created_by: str                   # User ID who created
    closed_at: int | None = None      # When task was closed

    # Denormalized counts
    comment_count: int = 0            # Number of comments

    # DynamoDB key
    @property
    def persistence_id(self) -> str:
        return self.id  # SK: TASK#{id}
```

### 2.2 Validation Rules

```python
@field_validator("title")
@classmethod
def validate_title(cls, value: str) -> str:
    """
    - Strip whitespace
    - Minimum 3 characters
    - Maximum 200 characters
    """
    value = value.strip()
    if len(value) < 3:
        raise ValueError("Title must be at least 3 characters")
    if len(value) > 200:
        raise ValueError("Title cannot exceed 200 characters")
    return value

@field_validator("description")
@classmethod
def validate_description(cls, value: str) -> str:
    """
    - Strip whitespace
    - Minimum 10 characters
    - Maximum 5000 characters
    """
    value = value.strip()
    if len(value) < 10:
        raise ValueError("Description must be at least 10 characters")
    if len(value) > 5000:
        raise ValueError("Description cannot exceed 5000 characters")
    return value

@field_validator("due_date")
@classmethod
def validate_due_date(cls, value: int | None, info: ValidationInfo) -> int | None:
    """
    - Must be in the future (or None)
    - Cannot be before created_at
    """
    if value is None:
        return value

    created_at = info.data.get("created_at", current_utc_timestamp())
    if value < created_at:
        raise ValueError("Due date cannot be in the past")

    return value

@model_validator(mode="after")
def validate_model(self):
    """
    Cross-field validation:
    - Set closed_at when status changes to CLOSED
    - Clear closed_at when reopening task
    """
    if self.status == TaskStatus.CLOSED and self.closed_at is None:
        self.closed_at = current_utc_timestamp()

    return self
```

### 2.3 Business Logic Methods

```python
# Status checks
@property
def is_open(self) -> bool:
    return self.status == TaskStatus.OPEN

@property
def is_closed(self) -> bool:
    return self.status == TaskStatus.CLOSED

@property
def is_overdue(self) -> bool:
    """Check if task is overdue."""
    if self.due_date is None or self.is_closed:
        return False
    return current_utc_timestamp() > self.due_date

# State mutations
def update_status(self, new_status: TaskStatus) -> None:
    """Update task status and set timestamps."""
    old_status = self.status
    self.status = new_status
    self.updated_at = current_utc_timestamp()

    # Set closed_at when closing
    if new_status == TaskStatus.CLOSED and old_status != TaskStatus.CLOSED:
        self.closed_at = current_utc_timestamp()

    # Clear closed_at when reopening
    if new_status != TaskStatus.CLOSED and old_status == TaskStatus.CLOSED:
        self.closed_at = None

def assign_to_user(self, user_id: str, user_name: str) -> None:
    """Assign task to a user."""
    self.assigned_user_id = user_id
    self.assigned_user_name = user_name
    self.updated_at = current_utc_timestamp()

def increment_comment_count(self) -> None:
    """Increment comment count (called when comment is added)."""
    self.comment_count += 1
    self.updated_at = current_utc_timestamp()

def link_to_event(self, event_id: str, event_details: dict) -> None:
    """Link task to a source event."""
    self.event_id = event_id
    self.event_details = event_details
    self.updated_at = current_utc_timestamp()
```

### 2.4 DynamoDB Schema

**Table:** Single table design with `EventsTable`

```python
# Partition Key (PK): TASK
# Sort Key (SK): TASK#{task_id}
# GSI1-PK: ASSIGNED#{user_id}  (for "my tasks" queries)
# GSI1-SK: STATUS#{status}#PRIORITY#{priority}#TASK#{task_id}
# GSI2-PK: STATUS#{status}     (for status filtering)
# GSI2-SK: CREATED#{created_at}#TASK#{task_id}
# GSI3-PK: EVENT#{event_id}    (for event-linked tasks)
# GSI3-SK: TASK#{task_id}

class TaskPersistence(DynamoModel, discriminator="TASK"):
    pk = KeyAttribute(hash_key=True, default="TASK")
    sk = KeyAttribute(range_key=True, prefix="TASK#")

    # Task fields
    title = UnicodeAttribute(null=False)
    description = UnicodeAttribute(null=False)
    status = UnicodeAttribute(null=False)
    priority = UnicodeAttribute(null=False)
    assigned_user_id = UnicodeAttribute(null=False)
    assigned_user_name = UnicodeAttribute(null=True)
    event_id = UnicodeAttribute(null=True)
    event_details = UnicodeAttribute(null=True)  # JSON string
    due_date = NumberAttribute(null=True)
    created_at = NumberAttribute(null=False)
    updated_at = NumberAttribute(null=False)
    created_by = UnicodeAttribute(null=False)
    closed_at = NumberAttribute(null=True)
    comment_count = NumberAttribute(default=0)

    # GSI1: Assigned user index (for "my tasks")
    assigned_pk = KeyAttribute()  # ASSIGNED#{user_id}
    assigned_sk = KeyAttribute()  # STATUS#{status}#PRIORITY#{priority}#TASK#{id}

    # GSI2: Status index
    status_pk = KeyAttribute()    # STATUS#{status}
    status_sk = KeyAttribute()    # CREATED#{created_at}#TASK#{id}

    # GSI3: Event link index
    event_pk = KeyAttribute()     # EVENT#{event_id}
    event_sk = KeyAttribute()     # TASK#{id}
```

### 2.5 Use Cases

```
CreateTask
- Validate title, description
- Set status to OPEN
- Assign to user
- Link to event (if from event)
- Generate UUID
- Set created_by from auth context

GetTask
- Fetch task by ID
- Include comments (separate query)
- Return task with comment list

UpdateTask
- Validate permissions (assigned user, manager, admin)
- Update allowed fields
- Track status changes in history
- Update updated_at timestamp

DeleteTask
- Soft delete (or hard delete based on requirements)
- Require admin permission
- Cascade delete comments (or keep for audit)

ListTasks
- Filter by: status, priority, assigned_user, event_id, date range
- Sort by: created_at, due_date, priority
- Paginate with cursor
- Return tasks with denormalized user names

CreateTaskFromEvent
- Fetch event details
- Pre-fill task description with event data
- Link task to event
- Set priority based on event severity
```

---

## 3. TaskComment Entity Model

### 3.1 Domain Model

**File:** `backend/src/domain/models/task.py` (same file as Task)

```python
class TaskComment(BaseModel):
    """
    Task comment model.
    Represents a comment on a task for discussion and updates.
    """

    # Identity
    id: str                    # Comment UUID
    task_id: str               # Parent task ID

    # Author
    user_id: str               # User who created comment
    user_name: str             # Denormalized for display

    # Content
    comment: str               # Comment text (1-2000 chars)

    # Timestamp
    created_at: int = Field(default_factory=current_utc_timestamp)

    # DynamoDB key
    @property
    def persistence_id(self) -> str:
        # Sort by timestamp for chronological order
        return f"{self.created_at}#{self.id}"  # SK: COMMENT#{timestamp}#{id}
```

### 3.2 Validation Rules

```python
@field_validator("comment")
@classmethod
def validate_comment(cls, value: str) -> str:
    """
    - Strip whitespace
    - Minimum 1 character
    - Maximum 2000 characters
    """
    value = value.strip()
    if len(value) < 1:
        raise ValueError("Comment cannot be empty")
    if len(value) > 2000:
        raise ValueError("Comment cannot exceed 2000 characters")
    return value
```

### 3.3 DynamoDB Schema

**Table:** Single table design with `EventsTable`

```python
# Partition Key (PK): TASK#{task_id}  (comments grouped by task)
# Sort Key (SK): COMMENT#{created_at}#{comment_id}
# This enables efficient query of all comments for a task, sorted by time

class TaskCommentPersistence(DynamoModel, discriminator="COMMENT"):
    pk = KeyAttribute(hash_key=True)  # TASK#{task_id}
    sk = KeyAttribute(range_key=True, prefix="COMMENT#")

    # Comment fields
    comment_id = UnicodeAttribute(null=False)  # UUID
    user_id = UnicodeAttribute(null=False)
    user_name = UnicodeAttribute(null=False)
    comment = UnicodeAttribute(null=False)
    created_at = NumberAttribute(null=False)
```

### 3.4 Use Cases

```
AddComment
- Validate comment text
- Get user name from auth context
- Create comment
- Increment task.comment_count
- Update task.updated_at

GetTaskComments
- Query all comments for task_id
- Sort by created_at (ascending)
- Paginate if needed
- Return list of comments

DeleteComment (Optional)
- Soft delete or hard delete
- Decrement task.comment_count
- Require comment author or admin
```

---

## 4. Configuration Entity Models

### 4.1 AWS Account Configuration

**File:** `backend/src/domain/models/config.py`

```python
class AwsAccount(BaseModel):
    """
    AWS Account configuration for monitoring.
    Represents an AWS account that is being monitored.
    """

    # Identity
    id: str                    # Configuration UUID (not AWS account ID)
    account_id: str            # AWS Account ID (12 digits)
    account_name: str          # Friendly name

    # AWS Connection
    region: str                # Primary AWS region
    access_key_id: str | None = None      # AWS access key (encrypted)
    secret_access_key: str | None = None  # AWS secret key (encrypted)
    role_arn: str | None = None           # IAM role ARN (preferred)

    # Status
    is_active: bool = True     # Monitoring enabled/disabled
    last_sync: int | None = None  # Last successful connection test

    # Timestamps
    created_at: int = Field(default_factory=current_utc_timestamp)
    updated_at: int = Field(default_factory=current_utc_timestamp)

    # DynamoDB key
    @property
    def persistence_id(self) -> str:
        return self.id  # SK: AWS_ACCOUNT#{id}
```

#### Validation Rules

```python
@field_validator("account_id")
@classmethod
def validate_account_id(cls, value: str) -> str:
    """
    - Must be 12 digits
    - Numeric only
    """
    value = value.strip()
    if not value.isdigit() or len(value) != 12:
        raise ValueError("AWS Account ID must be 12 digits")
    return value

@field_validator("region")
@classmethod
def validate_region(cls, value: str) -> str:
    """
    - Must be valid AWS region format
    - e.g., us-east-1, eu-west-1
    """
    import re
    if not re.match(r'^[a-z]{2}-[a-z]+-\d{1}$', value):
        raise ValueError("Invalid AWS region format")
    return value

@model_validator(mode="after")
def validate_credentials(self):
    """
    Must have either:
    - access_key_id + secret_access_key
    - OR role_arn
    """
    has_keys = self.access_key_id and self.secret_access_key
    has_role = self.role_arn

    if not (has_keys or has_role):
        raise ValueError("Must provide either access keys or role ARN")

    return self
```

#### Business Logic Methods

```python
def uses_role_auth(self) -> bool:
    """Check if using IAM role authentication."""
    return self.role_arn is not None

def uses_key_auth(self) -> bool:
    """Check if using access key authentication."""
    return self.access_key_id is not None

def update_last_sync(self, success: bool) -> None:
    """Update last sync timestamp."""
    if success:
        self.last_sync = current_utc_timestamp()
    self.updated_at = current_utc_timestamp()

def mask_credentials(self) -> dict:
    """Return account info with masked credentials."""
    data = self.model_dump()
    if self.access_key_id:
        data["access_key_id"] = f"{self.access_key_id[:4]}...{self.access_key_id[-4:]}"
    if self.secret_access_key:
        data["secret_access_key"] = "***REDACTED***"
    return data
```

### 4.2 Monitoring Configuration

**File:** `backend/src/domain/models/config.py`

```python
class ServiceConfig(BaseModel):
    """Configuration for a specific AWS service."""

    service_name: str          # e.g., "cloudwatch", "guardduty"
    enabled: bool = True       # Service monitoring enabled

    # Polling configuration
    polling_interval: int = 300  # Seconds (default: 5 minutes)

    # Alert thresholds
    thresholds: dict = {}      # Service-specific thresholds
    # Example for CloudWatch:
    # {
    #   "cpu_threshold": 80,
    #   "memory_threshold": 90,
    #   "error_rate_threshold": 5
    # }

    # Resource filtering
    resource_filters: dict = {}
    # {
    #   "resource_ids": ["i-1234567890", "db-instance-1"],
    #   "tags": {"Environment": "production", "Team": "platform"},
    #   "resource_types": ["AWS::EC2::Instance", "AWS::RDS::DBInstance"]
    # }

    # Severity rules
    severity_rules: list[dict] = []
    # [
    #   {
    #     "metric": "cpu_utilization",
    #     "operator": ">=",
    #     "value": 90,
    #     "severity": "critical"
    #   },
    #   {
    #     "metric": "cpu_utilization",
    #     "operator": ">=",
    #     "value": 70,
    #     "severity": "high"
    #   }
    # ]

class MonitoringConfig(BaseModel):
    """
    Global monitoring configuration.
    Singleton configuration for the entire system.
    """

    # Service configurations
    services: list[ServiceConfig] = []

    # Global settings
    global_settings: dict = {
        "default_polling_interval": 300,      # 5 minutes
        "alert_email_enabled": True,
        "alert_email_recipients": [],
        "alert_slack_enabled": True,
        "alert_slack_webhook": "",
        "data_retention_days": 90,
        "event_batch_size": 100,
    }

    # Timestamps
    updated_at: int = Field(default_factory=current_utc_timestamp)
    updated_by: str | None = None  # User ID who last updated

    # DynamoDB key
    @property
    def persistence_id(self) -> str:
        return "MONITORING_CONFIG"  # Singleton
```

#### Validation Rules

```python
@field_validator("services")
@classmethod
def validate_services(cls, value: list[ServiceConfig]) -> list[ServiceConfig]:
    """
    - No duplicate service names
    - At least one service enabled
    """
    service_names = [s.service_name for s in value]
    if len(service_names) != len(set(service_names)):
        raise ValueError("Duplicate service names not allowed")

    if not any(s.enabled for s in value):
        raise ValueError("At least one service must be enabled")

    return value
```

#### Business Logic Methods

```python
def get_service_config(self, service_name: str) -> ServiceConfig | None:
    """Get configuration for a specific service."""
    for service in self.services:
        if service.service_name == service_name:
            return service
    return None

def is_service_enabled(self, service_name: str) -> bool:
    """Check if a service is enabled."""
    service = self.get_service_config(service_name)
    return service.enabled if service else False

def update_service_config(self, service_name: str, config: ServiceConfig) -> None:
    """Update or add service configuration."""
    for i, service in enumerate(self.services):
        if service.service_name == service_name:
            self.services[i] = config
            self.updated_at = current_utc_timestamp()
            return

    # Service not found, add it
    self.services.append(config)
    self.updated_at = current_utc_timestamp()

def get_enabled_services(self) -> list[ServiceConfig]:
    """Get list of enabled services."""
    return [s for s in self.services if s.enabled]
```

### 4.3 DynamoDB Schema

**AwsAccount Table:**

```python
# Partition Key (PK): CONFIG
# Sort Key (SK): AWS_ACCOUNT#{id}
# GSI1-PK: ACCOUNT_ID#{account_id}  (for lookup by AWS account ID)
# GSI1-SK: AWS_ACCOUNT#{id}

class AwsAccountPersistence(DynamoModel, discriminator="AWS_ACCOUNT"):
    pk = KeyAttribute(hash_key=True, default="CONFIG")
    sk = KeyAttribute(range_key=True, prefix="AWS_ACCOUNT#")

    account_id = UnicodeAttribute(null=False)
    account_name = UnicodeAttribute(null=False)
    region = UnicodeAttribute(null=False)
    access_key_id = UnicodeAttribute(null=True)  # Encrypted
    secret_access_key = UnicodeAttribute(null=True)  # Encrypted
    role_arn = UnicodeAttribute(null=True)
    is_active = BooleanAttribute(default=True)
    last_sync = NumberAttribute(null=True)
    created_at = NumberAttribute(null=False)
    updated_at = NumberAttribute(null=False)

    # GSI1 for account_id lookup
    account_pk = KeyAttribute()  # ACCOUNT_ID#{account_id}
    account_sk = KeyAttribute()  # AWS_ACCOUNT#{id}
```

**MonitoringConfig Table:**

```python
# Partition Key (PK): CONFIG
# Sort Key (SK): MONITORING_CONFIG (singleton)

class MonitoringConfigPersistence(DynamoModel, discriminator="MONITORING_CONFIG"):
    pk = KeyAttribute(hash_key=True, default="CONFIG")
    sk = KeyAttribute(range_key=True, default="MONITORING_CONFIG")

    services = UnicodeAttribute(null=False)  # JSON string
    global_settings = UnicodeAttribute(null=False)  # JSON string
    updated_at = NumberAttribute(null=False)
    updated_by = UnicodeAttribute(null=True)
```

---

## 5. Complete DynamoDB Single Table Design

### 5.1 Table Structure Overview

**Table Name:** `EventsTable`

```
Primary Key:
  - PK (Partition Key): String
  - SK (Sort Key): String

Global Secondary Indexes:
  - GSI1: GSI1-PK, GSI1-SK
  - GSI2: GSI2-PK, GSI2-SK
  - GSI3: GSI3-PK, GSI3-SK

TTL Field: expired_at
```

### 5.2 Access Patterns

| Entity | PK | SK | GSI1-PK | GSI1-SK | GSI2-PK | GSI2-SK | GSI3-PK | GSI3-SK |
|--------|----|----|---------|---------|---------|---------|---------|---------|
| **Event** | EVENT | EVENT#{timestamp}#{id} | ACCOUNT#{account} | EVENT#{timestamp}#{id} | SOURCE#{source} | EVENT#{timestamp}#{id} | - | - |
| **Agent** | AGENT | AGENT#{id} | - | - | - | - | - | - |
| **User** | USER | USER#{id} | EMAIL#{email} | USER#{id} | ROLE#{role} | USER#{id} | - | - |
| **Task** | TASK | TASK#{id} | ASSIGNED#{user_id} | STATUS#{status}#TASK#{id} | STATUS#{status} | CREATED#{created_at}#TASK#{id} | EVENT#{event_id} | TASK#{id} |
| **TaskComment** | TASK#{task_id} | COMMENT#{timestamp}#{id} | - | - | - | - | - | - |
| **AwsAccount** | CONFIG | AWS_ACCOUNT#{id} | ACCOUNT_ID#{account_id} | AWS_ACCOUNT#{id} | - | - | - | - |
| **MonitoringConfig** | CONFIG | MONITORING_CONFIG | - | - | - | - | - | - |

### 5.3 Query Examples

```python
# Get user by ID
pk = "USER", sk = "USER#{user_id}"

# Get user by email (GSI1)
GSI1-PK = "EMAIL#{email}", GSI1-SK begins_with "USER#"

# List users by role (GSI2)
GSI2-PK = "ROLE#{role}", GSI2-SK begins_with "USER#"

# Get task by ID
pk = "TASK", sk = "TASK#{task_id}"

# Get my tasks (GSI1)
GSI1-PK = "ASSIGNED#{user_id}", GSI1-SK begins_with "STATUS#"

# Get tasks by status (GSI2)
GSI2-PK = "STATUS#{status}", GSI2-SK begins_with "CREATED#"

# Get tasks linked to event (GSI3)
GSI3-PK = "EVENT#{event_id}", GSI3-SK begins_with "TASK#"

# Get task comments
pk = "TASK#{task_id}", sk begins_with "COMMENT#"

# Get AWS account by ID
pk = "CONFIG", sk = "AWS_ACCOUNT#{id}"

# Get AWS account by account_id (GSI1)
GSI1-PK = "ACCOUNT_ID#{account_id}", GSI1-SK begins_with "AWS_ACCOUNT#"

# Get monitoring config (singleton)
pk = "CONFIG", sk = "MONITORING_CONFIG"
```

---

## 6. DTOs (Data Transfer Objects)

### 6.1 Input DTOs

```python
# User DTOs
class CreateUserDTO(BaseModel):
    email: str
    full_name: str
    role: UserRole
    password: str | None = None  # Optional, auto-generate if None

class UpdateUserDTO(BaseModel):
    email: str | None = None
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = None

class ListUsersDTO(PaginatedInputDTO):
    search: str | None = None       # Search in email/name
    role: UserRole | None = None
    is_active: bool | None = None

# Task DTOs
class CreateTaskDTO(BaseModel):
    title: str
    description: str
    priority: TaskPriority
    assigned_user_id: str
    event_id: str | None = None
    due_date: int | None = None

class UpdateTaskDTO(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assigned_user_id: str | None = None
    due_date: int | None = None

class ListTasksDTO(PaginatedInputDTO):
    status: list[TaskStatus] | None = None
    priority: list[TaskPriority] | None = None
    assigned_user_id: str | None = None
    event_id: str | None = None
    start_date: int | None = None
    end_date: int | None = None

class AddCommentDTO(BaseModel):
    comment: str

# Config DTOs
class CreateAwsAccountDTO(BaseModel):
    account_id: str
    account_name: str
    region: str
    access_key_id: str | None = None
    secret_access_key: str | None = None
    role_arn: str | None = None

class UpdateAwsAccountDTO(BaseModel):
    account_name: str | None = None
    region: str | None = None
    access_key_id: str | None = None
    secret_access_key: str | None = None
    role_arn: str | None = None
    is_active: bool | None = None
```

### 6.2 Output Models (Query Results)

```python
# Generic paginated results
UserQueryResult = QueryResult[User]
TaskQueryResult = QueryResult[Task]
CommentQueryResult = QueryResult[TaskComment]

# Dashboard statistics
class EventStats(BaseModel):
    total: int
    by_severity: dict[str, int]  # {"critical": 5, "high": 10, ...}
    by_source: dict[str, int]    # {"aws.guardduty": 8, ...}
    recent_events: list[Event]   # Last 10 events

class TaskStats(BaseModel):
    total: int
    by_status: dict[TaskStatus, int]
    by_priority: dict[TaskPriority, int]
    my_tasks: int  # Tasks assigned to current user

class UserStats(BaseModel):
    total: int
    active: int
    by_role: dict[UserRole, int]

class DashboardOverview(BaseModel):
    events: EventStats
    tasks: TaskStats
    users: UserStats
```

---

## 7. Use Case Files Structure

```
backend/src/domain/use_cases/
├── auth/
│   ├── __init__.py
│   ├── login.py              # AuthenticateUser use case
│   ├── logout.py             # LogoutUser use case
│   ├── get_profile.py        # GetUserProfile use case
│   └── refresh_token.py      # RefreshAccessToken use case
├── users/
│   ├── __init__.py
│   ├── list_users.py         # ListUsers use case
│   ├── get_user.py           # GetUser use case
│   ├── create_user.py        # CreateUser use case
│   ├── update_user.py        # UpdateUser use case
│   └── delete_user.py        # DeleteUser/DeactivateUser use case
├── tasks/
│   ├── __init__.py
│   ├── list_tasks.py         # ListTasks use case
│   ├── get_task.py           # GetTask use case
│   ├── create_task.py        # CreateTask use case
│   ├── update_task.py        # UpdateTask use case
│   ├── delete_task.py        # DeleteTask use case
│   ├── add_comment.py        # AddTaskComment use case
│   └── update_status.py      # UpdateTaskStatus use case
├── events/
│   ├── __init__.py
│   ├── list_events.py        # Existing
│   ├── get_event.py          # Existing
│   ├── delete_event.py       # DeleteEvent use case
│   └── create_task_from_event.py  # CreateTaskFromEvent use case
├── dashboard/
│   ├── __init__.py
│   ├── get_overview.py       # GetDashboardOverview use case
│   ├── get_event_stats.py    # GetEventStats use case
│   ├── get_task_stats.py     # GetTaskStats use case
│   └── get_user_stats.py     # GetUserStats use case
└── config/
    ├── __init__.py
    ├── aws_accounts/
    │   ├── list_accounts.py
    │   ├── get_account.py
    │   ├── create_account.py
    │   ├── update_account.py
    │   ├── delete_account.py
    │   └── test_connection.py
    └── monitoring/
        ├── get_config.py
        └── update_config.py
```

---

## 8. Summary

### 8.1 Entities Created

1. **User** - Authentication and authorization
2. **Task** - Work items from events or manual creation
3. **TaskComment** - Discussion on tasks
4. **AwsAccount** - AWS account monitoring configuration
5. **MonitoringConfig** - Global monitoring settings

### 8.2 Design Principles Applied

✅ **Pydantic BaseModel** for domain models
✅ **Field validators** for input validation
✅ **Model validators** for cross-field validation
✅ **Business logic methods** on domain models
✅ **Separation of domain and persistence** models
✅ **DTOs for input/output** boundaries
✅ **Single table DynamoDB** design with GSIs
✅ **Denormalization** for performance (user names, event details)
✅ **Timestamp tracking** (created_at, updated_at)
✅ **Soft delete** capability (is_active flags)
✅ **Audit trail** (created_by, updated_by, history)

### 8.3 Next Steps

1. Review and approve entity designs
2. Implement domain models in `backend/src/domain/models/`
3. Create persistence models in `backend/src/adapters/db/models/`
4. Create mappers in `backend/src/adapters/db/mappers/`
5. Create repositories in `backend/src/adapters/db/repositories/`
6. Implement use cases
7. Create API Gateway handlers
8. Write tests
9. Update DynamoDB schema
10. Deploy and test

---

**Last Updated:** 2025-11-20
**Status:** Design Complete - Ready for Implementation
**Reference:** See `docs/MISSING_API_ENDPOINTS.md` for implementation tasks

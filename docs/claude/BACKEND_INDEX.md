# Backend Codebase Index

**Generated**: 2025-11-24
**Version**: 1.0.0
**Purpose**: Comprehensive mapping of backend structure, patterns, and integrations

---

## 📋 Table of Contents

1. [Quick Reference](#quick-reference)
2. [Directory Structure](#directory-structure)
3. [Domain Layer](#domain-layer)
4. [Adapters Layer](#adapters-layer)
5. [Entrypoints Layer](#entrypoints-layer)
6. [Architectural Patterns](#architectural-patterns)
7. [Dependencies & Integrations](#dependencies--integrations)
8. [Testing Organization](#testing-organization)
9. [Infrastructure & Deployment](#infrastructure--deployment)
10. [Usage Examples](#usage-examples)

---

## 🎯 Quick Reference

### Core Entities
- **Event**: Monitoring events from AWS services (CloudWatch, GuardDuty, Health, etc.)
- **Task**: Actionable items created from events or manually
- **User**: System users with authentication and authorization
- **AwsConfig**: AWS account monitoring configuration
- **MonitoringConfig**: Global monitoring settings

### Key Technologies
- **Runtime**: Python 3.13
- **Framework**: Serverless Framework 4.x
- **Database**: DynamoDB (PynamoDB ORM)
- **Architecture**: Hexagonal (Ports & Adapters)
- **Testing**: Pytest, Moto, LocalStack
- **Validation**: Pydantic v2.11.0

### Entry Points
- **Lambda Functions**: 3 event-driven functions
- **API Gateway**: 33 REST API endpoints
- **Event Sources**: EventBridge, CloudWatch, Manual triggers

---

## 📁 Directory Structure

```
backend/
├── src/                          # Source code
│   ├── domain/                   # Core business logic (↓)
│   │   ├── models/              # Domain entities
│   │   ├── ports/               # Interface contracts
│   │   └── use_cases/           # Business workflows
│   ├── adapters/                # External integrations (→)
│   │   ├── auth/                # Authentication (JWT, password)
│   │   ├── aws/                 # AWS service clients
│   │   ├── db/                  # DynamoDB repositories
│   │   └── notifiers/           # Slack notifications
│   ├── entrypoints/             # Application entry (↑)
│   │   ├── apigw/               # API Gateway handlers
│   │   └── functions/           # Lambda functions
│   └── common/                  # Shared utilities
│       ├── enums.py             # Type-safe enumerations
│       ├── exceptions.py        # Custom exceptions
│       ├── logger.py            # Logging configuration
│       └── utils/               # Utility functions
├── tests/                       # Test files
│   ├── adapters/                # Adapter tests
│   ├── integrations/            # Integration tests
│   └── data/                    # Test fixtures
├── infra/                       # Infrastructure as Code
│   ├── configs/                 # Stage configurations
│   ├── functions/               # Lambda definitions
│   ├── resources/               # AWS resources
│   └── roles/                   # IAM policies
├── statics/                     # Static assets
│   └── templates/               # Jinja2 templates
└── ops/                         # Operational scripts
    ├── deployment/              # Deploy/destroy scripts
    ├── development/             # Dev environment setup
    └── local/                   # LocalStack data
```

**Dependency Flow**: Entrypoints → Adapters → Domain (Core)
**Principle**: Dependencies point inward toward domain layer

---

## 🎯 Domain Layer

### Domain Models (`src/domain/models/`)

#### Event Model (`event.py`)
**Purpose**: Monitoring events from AWS services with TTL support

```python
class Event(BaseModel):
    id: str                    # {published_at}-{event_uuid}
    account: str               # AWS Account ID (12 digits)
    region: str                # AWS region (e.g., us-east-1)
    source: str                # Event source (aws.*, monitoring.*)
    detail_type: str           # Event type classification
    detail: dict               # Event-specific data
    severity: int              # 0-5 severity level
    resources: list[str]       # Affected AWS resources
    published_at: int          # Unix timestamp
    updated_at: int            # Unix timestamp
    expired_at: int            # TTL timestamp (90 days default)
```

**Key Methods**:
- `is_critical()` → Check severity >= 4
- `is_high_priority()` → Check severity >= 3
- `get_severity_label()` → Human-readable severity
- `days_until_expiry()` → Calculate remaining lifetime

**Validations**:
- Account ID: exactly 12 digits
- Region: AWS region format (`^[a-z]{2}-[a-z]+-\d{1}$`)
- Source: must start with `aws.` or `monitoring.`
- Severity: 0-5 range

**Storage Pattern**: DynamoDB single-table design
- PK: `EVENT`
- SK: `EVENT#{id}`
- GSI1: Source-based queries (PK: `SOURCE#{source}`, SK: `EVENT#{id}`)

---

#### Task Model (`task.py`)
**Purpose**: Actionable items for tracking event resolution or manual tasks

```python
class Task(BaseModel):
    id: str                    # Task UUID (uuid7)
    title: str                 # 3-200 characters
    description: str           # 10-5000 characters
    status: TaskStatus         # open | in_progress | closed
    priority: TaskPriority     # critical | high | medium | low
    assigned_user: AssignedUser  # Nested user object
    event_id: str | None       # Source event link (optional)
    event_details: dict | None # Denormalized event info
    due_date: int | None       # Unix timestamp (optional)
    created_at: int            # Unix timestamp
    updated_at: int            # Unix timestamp
    created_by: str            # Creator user ID
    closed_at: int | None      # Closure timestamp
    comments: list[TaskComment]  # Comment history
```

**Nested Models**:
- `AssignedUser`: `{id, name}` - Denormalized user assignment
- `TaskComment`: `{id, user_id, user_name, comment, created_at}`

**Key Methods**:
- `update_status(new_status)` → Change status with timestamp management
- `assign_to_user(user_id, user_name)` → Update assignment
- `add_comment(comment_id, user_id, user_name, comment)` → Append comment
- `link_to_event(event_id, event_details)` → Associate with event

**Business Rules**:
- Auto-set `closed_at` when status → `closed`
- Clear `closed_at` when reopening
- Due date must be in future
- Title: 3-200 chars, Description: 10-5000 chars

**Storage Pattern**:
- PK: `TASK`
- SK: `TASK#{id}`
- GSI indexes for filtering by status, priority, assigned user

---

#### User Model (`user.py`)
**Purpose**: Authentication and authorization management

```python
class User(BaseModel):
    id: str                    # User UUID
    email: str                 # Unique email (lowercase)
    full_name: str             # 2-100 characters
    password_hash: str         # Bcrypt hashed (never exposed)
    role: UserRole             # admin | user
    is_active: bool            # Account status
    created_at: int            # Unix timestamp
    updated_at: int            # Unix timestamp
    last_login: int | None     # Last login timestamp
```

**Permission Model**:
```
Role Hierarchy: admin > user

Base Permissions (all users):
- read:events
- read:own_tasks, update:own_tasks
- read:own_profile, update:own_profile

Admin Permissions:
- read:all_tasks, create/update/delete:tasks
- create/update/delete:users, read:users
- read/update:config
```

**Key Methods**:
- `has_permission(required_role)` → Check permission level
- `is_admin()` → Check admin role
- `update_last_login()` → Update login timestamp

**Security Features**:
- Email validation (format check, lowercase normalization)
- Password hashing via bcrypt
- Role-based access control (RBAC)
- UserProfile model excludes sensitive data for API responses

---

#### Configuration Models (`config.py`)

**AwsConfig**: AWS account monitoring setup
```python
class AwsConfig(BaseModel):
    id: str                    # Config UUID (not AWS account ID)
    account_id: str            # AWS Account ID (12 digits)
    account_name: str          # Friendly name
    region: str                # Primary AWS region
    role_arn: str | None       # Cross-account IAM role (optional)
    status: AwsConfigStatus    # pending | deploying | active | failed | disabled
    deployed_at: int | None    # Deployment timestamp
    last_sync: int | None      # Last connection test
    is_active: bool            # Monitoring enabled
```

**MonitoringConfig**: Global monitoring settings (singleton)
```python
class MonitoringConfig(BaseModel):
    services: list[ServiceConfig]  # Service-specific configs
    global_settings: dict         # System-wide settings
    updated_at: int               # Last update timestamp
    updated_by: str | None        # Last updater user ID
```

**ServiceConfig**: Per-service monitoring configuration
```python
class ServiceConfig(BaseModel):
    service_name: str          # e.g., "cloudwatch", "guardduty"
    enabled: bool              # Service monitoring toggle
    polling_interval: int      # Seconds (30-3600)
    thresholds: dict           # Service-specific alert thresholds
    resource_filters: dict     # Resource filtering rules
    severity_rules: list[dict] # Severity determination logic
```

---

### Domain Ports (`src/domain/ports/`)

**Purpose**: Interface contracts defining adapter requirements (Dependency Inversion)

```python
# repositories.py
class IEventRepository(Protocol):
    def get(self, id: str) -> Event: ...
    def list(self, dto: ListEventsDTO | None = None) -> EventQueryResult: ...
    def create(self, entity: Event) -> None: ...
    def delete(self, id: str) -> None: ...

class ITaskRepository(Protocol):
    def get(self, task_id: str) -> Task: ...
    def create(self, entity: Task) -> None: ...
    def update(self, entity: Task) -> None: ...
    def delete(self, task_id: str) -> None: ...
    def list(self, dto: ListTasksDTO) -> TaskListResult: ...

class IUserRepository(Protocol):
    def get(self, user_id: str) -> User: ...
    def get_by_email(self, email: str) -> User: ...
    def create(self, entity: User) -> None: ...
    def update(self, entity: User) -> None: ...
    def delete(self, user_id: str) -> None: ...

# notifier.py
class IEventNotifier(Protocol):
    def notify(self, event: EventBridgeEvent) -> None: ...

class IReportNotifier(Protocol):
    def notify(self, report_data: dict) -> None: ...

# logs.py
class ILogService(Protocol):
    def query_logs(
        self,
        log_group_names: list[str],
        query_string: str,
        start_time: int,
        end_time: int,
    ) -> list[ResultFieldTypeDef]: ...

# publisher.py
class IPublisher(Protocol):
    def publish(self, event_data: dict) -> None: ...
```

**Pattern**: Protocol-based interfaces enable adapter swapping without domain changes

---

### Use Cases (`src/domain/use_cases/`)

**Organization**: Grouped by feature domain

```
use_cases/
├── auth/                      # Authentication workflows
│   ├── authenticate_user.py   # Email/password login
│   ├── generate_auth_tokens.py # JWT token generation
│   ├── get_current_user.py    # Get authenticated user
│   ├── logout_user.py         # Invalidate session
│   └── refresh_auth_token.py  # Token refresh
├── config/                    # Configuration management
│   ├── get_aws_config.py      # Fetch AWS account config
│   ├── get_monitoring_config.py # Fetch monitoring settings
│   ├── test_aws_connection.py # Validate AWS credentials
│   ├── update_aws_config.py   # Update AWS account config
│   └── update_monitoring_config.py # Update monitoring settings
├── dashboard/                 # Dashboard statistics
│   ├── get_dashboard_overview.py # Aggregate all stats
│   ├── get_events_stats.py    # Event metrics
│   ├── get_tasks_stats.py     # Task metrics
│   └── get_users_stats.py     # User metrics
├── tasks/                     # Task management
│   ├── add_comment_to_task.py # Add task comment
│   ├── create_task.py         # Create new task
│   ├── create_task_from_event.py # Convert event to task
│   ├── delete_task.py         # Delete task
│   ├── get_task.py            # Fetch single task
│   ├── list_tasks.py          # List/filter tasks
│   ├── update_task.py         # Update task fields
│   └── update_task_status.py  # Change task status
├── users/                     # User management
│   ├── change_password.py     # Update user password
│   ├── create_user.py         # Register new user
│   ├── delete_user.py         # Remove user
│   ├── get_user.py            # Fetch user by ID
│   ├── list_users.py          # List all users
│   └── update_user.py         # Update user profile
├── daily_report.py           # Generate daily summary
├── insert_monitoring_event.py # Store incoming events
└── query_error_logs.py       # Query CloudWatch logs
```

**Use Case Pattern**:
```python
class CreateTask:
    """Use case for creating new task."""

    def __init__(
        self,
        task_repository: TaskRepository | None = None,
        user_repository: UserRepository | None = None,
    ):
        self.task_repository = task_repository or TaskRepository()
        self.user_repository = user_repository or UserRepository()

    def execute(self, dto: CreateTaskDTO, created_by_user_id: str) -> Task:
        """Execute use case with DTO input."""
        # 1. Validate dependencies (assigned user exists)
        assigned_user_entity = self.user_repository.get(dto.assigned_user_id)

        # 2. Create domain entity
        task = Task(
            id=str(uuid7()),
            title=dto.title,
            description=dto.description,
            status=TaskStatus.OPEN,
            priority=dto.priority,
            assigned_user=AssignedUser(
                id=assigned_user_entity.id,
                name=assigned_user_entity.full_name,
            ),
            created_by=created_by_user_id,
        )

        # 3. Persist via repository
        self.task_repository.create(task)

        # 4. Return result
        return task
```

**Key Characteristics**:
- **Single Responsibility**: Each use case handles one business operation
- **Dependency Injection**: Repositories injected (default instances for convenience)
- **DTO Pattern**: Input validation via Pydantic DTOs
- **Domain-Centric**: Business logic stays in domain layer
- **Error Handling**: Raises domain exceptions (NotFoundError, UnauthorizedError, etc.)

---

## 🔌 Adapters Layer

### Database Adapters (`src/adapters/db/`)

**Architecture**: Three-layer pattern (Models → Mappers → Repositories)

#### Database Models (`db/models/`)
**Purpose**: PynamoDB persistence models (DynamoDB schema)

```python
# Base infrastructure
class DynamoModel(Model):
    """Base model for all DynamoDB entities."""

    class Meta(DynamoMeta):
        table_name = os.getenv("AWS_DYNAMODB_TABLE", "monitoring-local")
        region = AWS_REGION
        host = AWS_ENDPOINT

    pk = KeyAttribute(hash_key=True)      # Partition key
    sk = KeyAttribute(range_key=True)     # Sort key

# Event persistence model
class EventPersistence(DynamoModel, discriminator="EVENT"):
    pk = KeyAttribute(hash_key=True, default="EVENT")
    sk = KeyAttribute(range_key=True, prefix="EVENT#")

    # Attributes
    id = UnicodeAttribute(null=False)
    account = UnicodeAttribute(null=False)
    region = UnicodeAttribute(null=False)
    source = UnicodeAttribute(null=False)
    detail_type = UnicodeAttribute(null=False)
    detail = UnicodeAttribute(null=False)  # JSON string
    severity = NumberAttribute(null=False, default=0)
    resources = UnicodeAttribute(null=False, default="[]")
    published_at = NumberAttribute(null=False)
    updated_at = NumberAttribute(null=False)
    expired_at = NumberAttribute(null=False)  # TTL

    # Global Secondary Index for source-based queries
    gsi1 = GSI1Index()
    gsi1pk = KeyAttribute(prefix="SOURCE#", null=False)
    gsi1sk = KeyAttribute(prefix="EVENT#", null=False)
```

**Single Table Design**:
| Entity | PK | SK | GSI1PK | GSI1SK |
|--------|----|----|--------|--------|
| Event | `EVENT` | `EVENT#{id}` | `SOURCE#{source}` | `EVENT#{id}` |
| Task | `TASK` | `TASK#{id}` | `STATUS#{status}` | `TASK#{created_at}` |
| User | `USER` | `USER#{id}` | `EMAIL#{email}` | `USER#{id}` |
| AwsConfig | `AWS_CONFIG` | `CONFIG#{id}` | - | - |
| MonitoringConfig | `MONITORING_CONFIG` | `CONFIG` | - | - |

---

#### Mappers (`db/mappers/`)
**Purpose**: Bidirectional conversion between domain models and persistence models

```python
class EventMapper(Mapper):
    """Maps between Event domain model and EventPersistence."""

    @staticmethod
    def to_entity(model: EventPersistence) -> Event:
        """Convert persistence model to domain entity."""
        return Event(
            id=model.id,
            account=model.account,
            region=model.region,
            source=model.source,
            detail_type=model.detail_type,
            detail=json.loads(model.detail),
            severity=model.severity,
            resources=json.loads(model.resources),
            published_at=model.published_at,
            updated_at=model.updated_at,
            expired_at=model.expired_at,
        )

    @staticmethod
    def to_persistence(entity: Event) -> EventPersistence:
        """Convert domain entity to persistence model."""
        return EventPersistence(
            pk="EVENT",
            sk=f"EVENT#{entity.id}",
            id=entity.id,
            account=entity.account,
            region=entity.region,
            source=entity.source,
            detail_type=entity.detail_type,
            detail=json.dumps(entity.detail),
            severity=entity.severity,
            resources=json.dumps(entity.resources),
            published_at=entity.published_at,
            updated_at=entity.updated_at,
            expired_at=entity.expired_at,
            gsi1pk=f"SOURCE#{entity.source}",
            gsi1sk=f"EVENT#{entity.id}",
        )
```

**Mapper Responsibilities**:
- JSON serialization/deserialization (`detail`, `resources` fields)
- Key generation (PK, SK, GSI keys)
- Type conversion (domain types ↔ DynamoDB types)
- Denormalization (e.g., `AssignedUser` in tasks)

---

#### Repositories (`db/repositories/`)
**Purpose**: Data access implementations following domain ports

**Base Repository Pattern**:
```python
class DynamoRepository[M: DynamoModel]:
    """Generic DynamoDB repository with CRUD operations."""

    model_cls: Type[M]             # Persistence model class
    mapper: Type[Mapper]           # Mapper class
    hash_key_attr: Attribute       # PK attribute
    range_key_attr: Attribute      # SK attribute

    # Generic CRUD operations
    def _get(self, hash_key, range_key=None) -> M: ...
    def _query(self, hash_key, range_key_condition=None, ...) -> ResultIterator[M]: ...
    def _create(self, model: M) -> None: ...
    def _update(self, hash_key, range_key=None, attributes=None) -> None: ...
    def _delete(self, hash_key, range_key=None) -> None: ...
    def _count(self, hash_key, range_key_condition=None, ...) -> int: ...
```

**Concrete Repository Example**:
```python
class EventRepository(DynamoRepository):
    model_cls = EventPersistence
    mapper = EventMapper

    def get(self, id: str) -> Event:
        """Get event by ID."""
        model = self._get(hash_key="EVENT", range_key=f"EVENT#{id}")
        return self.mapper.to_entity(model)

    def list(self, dto: ListEventsDTO | None = None) -> EventQueryResult:
        """List events with pagination and filtering."""
        dto = dto or ListEventsDTO()

        # Build range key condition for date filtering
        if dto.start_date and dto.end_date:
            range_key_condition = self.model_cls.sk.between(
                f"EVENT#{dto.start_date}",
                f"EVENT#{dto.end_date}"
            )
        elif dto.start_date:
            range_key_condition = self.model_cls.sk >= f"EVENT#{dto.start_date}"
        elif dto.end_date:
            range_key_condition = self.model_cls.sk <= f"EVENT#{dto.end_date}"
        else:
            range_key_condition = None

        # Execute query
        result = self._query(
            hash_key="EVENT",
            range_key_condition=range_key_condition,
            last_evaluated_key=base64_to_json(dto.cursor),
            scan_index_forward=dto.direction == "asc",
            limit=dto.limit,
        )

        # Map to domain entities
        return EventQueryResult(
            items=[self.mapper.to_entity(item) for item in result],
            limit=dto.limit,
            cursor=result.last_evaluated_key,
        )

    def list_by_source(self, source: str, ...) -> list[Event]:
        """Query events by source using GSI1."""
        result = self._query(
            hash_key=f"SOURCE#{source}",
            range_key_condition=...,  # Optional date filtering
            index=self.model_cls.gsi1,
        )
        return [self.mapper.to_entity(item) for item in result]

    def create(self, entity: Event) -> None:
        """Create new event."""
        model = self.mapper.to_persistence(entity)
        self._create(model)

    def delete(self, id: str) -> None:
        """Delete event by ID."""
        self._delete(hash_key="EVENT", range_key=f"EVENT#{id}")
```

**Repository Roster**:
- `EventRepository`: Event CRUD + source/date queries
- `TaskRepository`: Task CRUD + status/priority/assignee filtering
- `UserRepository`: User CRUD + email lookup
- `AwsConfigRepository`: AWS account config management
- `MonitoringConfigRepository`: Global monitoring settings (singleton)

---

### AWS Service Adapters (`src/adapters/aws/`)

**CloudWatch Logs Service** (`cloudwatch.py`):
```python
class CloudwatchLogService(metaclass=SingletonMeta):
    """CloudWatch Logs Insights query service."""

    def query_logs(
        self,
        log_group_names: list[str],
        query_string: str,
        start_time: int,
        end_time: int,
        timeout: int = 15,
    ) -> list[ResultFieldTypeDef]:
        """Execute CloudWatch Logs Insights query."""
        # Start async query
        response = self.client.start_query(
            logGroupNames=log_group_names,
            queryString=query_string,
            startTime=start_time,
            endTime=end_time,
        )
        query_id = response["queryId"]

        # Poll for completion (with timeout)
        while response["status"] == "Running":
            if time.time() - query_time > timeout:
                raise RequestTimeoutError(...)
            time.sleep(1)
            response = self.client.get_query_results(queryId=query_id)

        return response.get("results", [])
```

**EventBridge Data Classes** (`data_classes.py`):
```python
# Base event wrapper
class EventBridgeEvent:
    """Generic EventBridge event wrapper."""
    def __init__(self, event: dict):
        self.raw_event = event
        self.account = event["account"]
        self.region = event["region"]
        self.source = event["source"]
        self.detail_type = event["detail-type"]
        self.detail = event["detail"]
        self.time = event["time"]

# Service-specific event types
class CwAlarmEvent(EventBridgeEvent):
    """CloudWatch Alarm event."""
    @property
    def detail(self):
        return CwAlarmDetail(self.raw_event["detail"])

class GuardDutyFindingEvent(EventBridgeEvent):
    """GuardDuty security finding."""
    @property
    def detail(self):
        return GuardDutyDetail(self.raw_event["detail"])

class HealthEvent(EventBridgeEvent):
    """AWS Health event."""
    @property
    def detail(self):
        return HealthDetail(self.raw_event["detail"])

class CfnStackEvent(EventBridgeEvent):
    """CloudFormation stack event."""
    @property
    def stack_data(self):
        return CfnStackData(self.raw_event["detail"])

class CwLogEvent(EventBridgeEvent):
    """Custom CloudWatch Logs event."""
    @property
    def detail(self):
        return CwLogDetail(self.raw_event["detail"])
```

**Other AWS Adapters**:
- `ecs.py`: ECS task management
- `lambda_function.py`: Lambda invocation
- `eventbridge.py`: EventBridge publishing

---

### Authentication Adapters (`src/adapters/auth/`)

**JWT Service** (`jwt.py`):
```python
class JWTService:
    """JWT token generation and validation."""

    def create_access_token(self, user_id: str, role: str) -> str:
        """Create short-lived access token (15 min)."""
        payload = {
            "sub": user_id,
            "role": role,
            "type": "access",
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def create_refresh_token(self, user_id: str) -> str:
        """Create long-lived refresh token (7 days)."""
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def decode_token(self, token: str) -> dict:
        """Decode and validate JWT token."""
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token has expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedError("Invalid token")
```

**Password Service** (`password.py`):
```python
class PasswordService:
    """Bcrypt password hashing and verification."""

    def hash_password(self, plain_password: str) -> str:
        """Hash password using bcrypt."""
        return bcrypt.hashpw(
            plain_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
```

---

### Notifier Adapters (`src/adapters/notifiers/`)

**Slack Event Notifier** (`events.py`):
```python
class EventNotifier:
    """Send event notifications to Slack."""

    def __init__(self, client: SlackClient):
        self.client = client

    @staticmethod
    def event_to_message(event: EventBridgeEvent) -> Message:
        """Convert event to Slack message format."""
        match event.source:
            case EventSource.AWS_CLOUDWATCH.value:
                return cw_alarm_event_to_message(event)
            case EventSource.AWS_GUARDDUTY.value:
                return guardduty_event_to_message(event)
            case EventSource.AWS_HEALTH.value:
                return health_event_to_message(event)
            case EventSource.AWS_CLOUDFORMATION.value:
                return cfn_event_to_message(event)
            case EventSource.AGENT_LOGS.value:
                return cw_log_event_to_message(event)
            case _:
                raise ValueError(f"Unknown event source: {event.source}")

    def notify(self, event: EventBridgeEvent):
        """Send notification to Slack."""
        message = self.event_to_message(event)
        self.client.send(message)
```

**Message Templates**: Jinja2 templates in `statics/templates/`
- `cloudwatch_alarm.jinja`: CloudWatch alarm formatting
- `guardduty.jinja`: GuardDuty finding formatting
- `health.jinja`: AWS Health event formatting
- `cfn_deployment.jinja`: CloudFormation status formatting
- `cloudwatch_log.jinja`: Custom log event formatting
- `daily_report.jinja`: Daily summary report

---

## 🚀 Entrypoints Layer

### API Gateway Handlers (`src/entrypoints/apigw/`)

**Base App Configuration** (`base.py`):
```python
from aws_lambda_powertools.event_handler import APIGatewayRestResolver

def create_app(cors_allow_origin: str, cors_max_age: int) -> APIGatewayRestResolver:
    """Create API Gateway resolver with CORS."""
    return APIGatewayRestResolver(
        enable_validation=True,
        cors=CORSConfig(
            allow_origin=cors_allow_origin,
            max_age=cors_max_age,
            allow_headers=["Content-Type", "Authorization"],
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        ),
    )
```

**Authentication Middleware** (`middleware/auth.py`):
```python
class AuthContext:
    """Authentication context for requests."""
    user_id: str
    email: str
    role: str

    def is_admin(self) -> bool:
        return self.role == "admin"

def get_auth_context(app: APIGatewayRestResolver) -> AuthContext:
    """Extract and validate authentication from request."""
    # Get token from Authorization header
    auth_header = app.current_event.get_header_value("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedError("Missing or invalid authorization header")

    token = auth_header[7:]  # Remove "Bearer " prefix

    # Decode and validate JWT
    payload = jwt_service.decode_token(token)

    # Return auth context
    return AuthContext(
        user_id=payload["sub"],
        email=payload.get("email"),
        role=payload.get("role", "user"),
    )
```

**API Handler Pattern**:
```python
# tasks/main.py
from src.entrypoints.apigw.base import create_app
from src.entrypoints.apigw.middleware.auth import get_auth_context

app = create_app(cors_allow_origin="*", cors_max_age=300)

# Initialize use cases
create_task_uc = CreateTask()
list_tasks_uc = ListTasks()

# Route handlers
@app.post("/tasks")
def create_task(request: CreateTaskRequest):
    """Create new task endpoint."""
    # Authenticate request
    auth = get_auth_context(app)

    # Create DTO from request
    dto = CreateTaskDTO(
        title=request.title,
        description=request.description,
        priority=request.priority,
        assigned_user_id=request.assigned_user_id,
    )

    # Execute use case
    task = create_task_uc.execute(dto, created_by_user_id=auth.user_id)

    # Return response
    return task.model_dump(), HTTPStatus.CREATED

@app.get("/tasks")
def list_tasks(
    status: Annotated[TaskStatus | None, Query] = None,
    page: Annotated[int, Query] = 1,
    page_size: Annotated[int, Query] = 20,
):
    """List tasks with filtering."""
    auth = get_auth_context(app)

    dto = ListTasksDTO(status=status, page=page, page_size=page_size)
    result = list_tasks_uc.execute(dto)

    return {
        "items": [task.model_dump() for task in result.items],
        "total": result.total,
        "page": result.page,
        "page_size": result.page_size,
    }

# Lambda handler entrypoint
def handler(event: dict, context: LambdaContext) -> dict:
    """Lambda function handler."""
    return app.resolve(event, context)
```

**API Roster** (33 endpoints across 5 modules):

**Auth Module** (`auth/main.py`):
- `POST /auth/login` → Authenticate user, return tokens
- `POST /auth/refresh` → Refresh access token
- `POST /auth/logout` → Invalidate refresh token

**Events Module** (`events/main.py`):
- `GET /events` → List events with pagination
- `GET /events/{id}` → Get single event
- `POST /events/{id}/create-task` → Create task from event

**Tasks Module** (`tasks/main.py`):
- `GET /tasks` → List tasks with filtering
- `GET /tasks/{id}` → Get single task
- `POST /tasks` → Create new task
- `PUT /tasks/{id}` → Update task
- `PUT /tasks/{id}/status` → Update task status
- `DELETE /tasks/{id}` → Delete task (admin only)
- `POST /tasks/{id}/comments` → Add comment

**Users Module** (`users/main.py`):
- `GET /users` → List all users (admin only)
- `GET /users/{id}` → Get user by ID
- `GET /users/me` → Get current user profile
- `POST /users` → Create new user (admin only)
- `PUT /users/{id}` → Update user
- `DELETE /users/{id}` → Delete user (admin only)
- `PUT /users/{id}/password` → Change password

**Config Module** (`config/main.py`):
- `GET /config/aws` → Get AWS account configs
- `POST /config/aws` → Create AWS config
- `PUT /config/aws/{id}` → Update AWS config
- `POST /config/aws/{id}/test` → Test AWS connection
- `GET /config/monitoring` → Get monitoring config
- `PUT /config/monitoring` → Update monitoring config

**Dashboard Module** (`dashboard/main.py`):
- `GET /dashboard/overview` → Get all statistics
- `GET /dashboard/events-stats` → Get event metrics
- `GET /dashboard/tasks-stats` → Get task metrics
- `GET /dashboard/users-stats` → Get user metrics

---

### Lambda Functions (`src/entrypoints/functions/`)

**HandleMonitoringEvents** (`handle_monitoring_events/main.py`):
```python
@event_source(data_class=EventBridgeEvent)
def handler(event: EventBridgeEvent, context):
    """
    Process monitoring events from EventBridge.

    Triggers:
    - EventBridge events from CloudWatch, GuardDuty, Health, CloudFormation

    Actions:
    1. Store event in DynamoDB
    2. Send Slack notification
    """
    try:
        insert_monitoring_event_use_case(event, event_repo, notifier)
    except Exception:
        logger.exception("Error handling monitoring event")
        raise
```

**DailyReport** (`daily_report/main.py`):
```python
def handler(event, context):
    """
    Generate and send daily monitoring summary.

    Triggers:
    - EventBridge scheduled rule (cron: 0 9 * * ? *)

    Actions:
    1. Query events from last 24 hours
    2. Aggregate statistics by source and severity
    3. Send formatted report to Slack
    """
    generate_daily_report_use_case(
        report_notifier=report_notifier,
        event_repo=event_repo,
    )
```

**QueryErrorLogs** (`query_error_logs/main.py`):
```python
def handler(event, context):
    """
    Query CloudWatch Logs for errors and publish to EventBridge.

    Triggers:
    - EventBridge scheduled rule (rate: 5 minutes)

    Actions:
    1. Query CloudWatch Logs Insights for error patterns
    2. Transform results into monitoring events
    3. Publish to EventBridge for processing
    """
    query_error_logs_use_case(
        log_service=log_service,
        publisher=publisher,
    )
```

---

## 🏗️ Architectural Patterns

### 1. Hexagonal Architecture (Ports & Adapters)

**Principle**: Business logic (domain) independent of external concerns

```
┌─────────────────────────────────────────────────────┐
│                  Entrypoints Layer                  │
│         (API Gateway, Lambda Functions)             │
└─────────────────┬───────────────────────────────────┘
                  │ calls
                  ▼
┌─────────────────────────────────────────────────────┐
│                   Domain Layer                      │
│         (Use Cases, Entities, Ports)                │
│                                                     │
│  Use Cases define: IEventRepository, INotifier      │
└──────┬──────────────────────────────────────┬───────┘
       │ implements                           │ implements
       ▼                                      ▼
┌──────────────────┐                  ┌──────────────────┐
│  Adapters Layer  │                  │  Adapters Layer  │
│  (Repositories)  │                  │   (Notifiers)    │
│                  │                  │                  │
│  - DynamoDB      │                  │  - Slack         │
│  - PynamoDB ORM  │                  │  - Email         │
└──────────────────┘                  └──────────────────┘
```

**Benefits**:
- Domain logic testable without databases or external services
- Easy adapter swapping (e.g., DynamoDB → PostgreSQL)
- Clear separation of concerns
- Dependency Inversion Principle (domain defines interfaces, adapters implement)

---

### 2. Repository Pattern

**Purpose**: Abstract data access logic from business logic

```python
# Domain defines interface (Port)
class IEventRepository(Protocol):
    def get(self, id: str) -> Event: ...
    def create(self, entity: Event) -> None: ...

# Adapter implements interface
class EventRepository(DynamoRepository):
    def get(self, id: str) -> Event:
        model = self._get(hash_key="EVENT", range_key=id)
        return self.mapper.to_entity(model)

    def create(self, entity: Event) -> None:
        model = self.mapper.to_persistence(entity)
        self._create(model)
```

**Benefits**:
- Domain uses `Event` entities, not database models
- Swappable persistence (DynamoDB, RDS, mock)
- Centralized query logic
- Consistent error handling

---

### 3. Data Mapper Pattern

**Purpose**: Separate domain entities from persistence models

```python
class EventMapper(Mapper):
    @staticmethod
    def to_entity(model: EventPersistence) -> Event:
        """Persistence → Domain."""
        return Event(
            id=model.id,
            detail=json.loads(model.detail),  # Deserialize JSON
            severity=model.severity,
            ...
        )

    @staticmethod
    def to_persistence(entity: Event) -> EventPersistence:
        """Domain → Persistence."""
        return EventPersistence(
            pk="EVENT",
            sk=f"EVENT#{entity.id}",
            detail=json.dumps(entity.detail),  # Serialize JSON
            severity=entity.severity,
            ...
        )
```

**Responsibilities**:
- Type conversions (dict ↔ JSON string, int ↔ timestamp)
- Key generation (PK, SK, GSI keys)
- Denormalization (e.g., embed user name in task assignment)

---

### 4. DTO Pattern (Data Transfer Objects)

**Purpose**: Input validation and API contract definition

```python
# Use case input DTO
class CreateTaskDTO(BaseModel):
    """Validates and structures task creation input."""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    priority: TaskPriority
    assigned_user_id: str
    due_date: int | None = None

# Use case execution
def execute(self, dto: CreateTaskDTO, created_by_user_id: str) -> Task:
    # DTO already validated by Pydantic
    task = Task(
        id=str(uuid7()),
        title=dto.title,  # Safe to use
        description=dto.description,
        ...
    )
    return task
```

**Benefits**:
- Input validation via Pydantic (type checking, constraints)
- API contract documentation
- Separation of API models from domain entities
- Prevents domain entity pollution with API-specific fields

---

### 5. Dependency Injection

**Pattern**: Constructor injection with default instances

```python
class CreateTask:
    def __init__(
        self,
        task_repository: TaskRepository | None = None,
        user_repository: UserRepository | None = None,
    ):
        # Default instances for convenience, but injectable for testing
        self.task_repository = task_repository or TaskRepository()
        self.user_repository = user_repository or UserRepository()
```

**Usage**:
```python
# Production: Use defaults
use_case = CreateTask()

# Testing: Inject mocks
use_case = CreateTask(
    task_repository=MockTaskRepository(),
    user_repository=MockUserRepository(),
)
```

---

### 6. Single Table Design (DynamoDB)

**Pattern**: Store all entities in one table with discriminator

**Key Structure**:
```
PK (Partition Key)    SK (Sort Key)           Entity Type
------------------    ----------------        -----------
EVENT                 EVENT#{id}              Event
TASK                  TASK#{id}               Task
USER                  USER#{id}               User
AWS_CONFIG            CONFIG#{id}             AwsConfig
MONITORING_CONFIG     CONFIG                  MonitoringConfig
```

**Global Secondary Indexes**:
```
GSI1: Query by source
  PK: SOURCE#{source}
  SK: EVENT#{id}

GSI2: Query tasks by status
  PK: STATUS#{status}
  SK: TASK#{created_at}

GSI3: Query users by email
  PK: EMAIL#{email}
  SK: USER#{id}
```

**Benefits**:
- Cost-effective (one table vs. many)
- Consistent throughput management
- Flexible access patterns via GSIs
- Easier backup and monitoring

---

### 7. Error Handling Strategy

**Custom Exceptions** (`src/common/exceptions.py`):
```python
class DomainError(Exception):
    """Base domain exception."""
    pass

class NotFoundError(DomainError):
    """Entity not found (404)."""
    pass

class UnauthorizedError(DomainError):
    """Authentication failed (401)."""
    pass

class ForbiddenError(DomainError):
    """Authorization failed (403)."""
    pass

class ConflictError(DomainError):
    """Resource conflict (409)."""
    pass

class ValidationError(DomainError):
    """Input validation failed (400)."""
    pass

class InternalServerError(DomainError):
    """Unexpected server error (500)."""
    pass
```

**Exception Flow**:
```
Repository → DynamoDB error → Custom exception
↓
Use Case → Re-raise or wrap in domain exception
↓
API Handler → Catch exception → HTTP status code
```

**Example**:
```python
# Repository layer
def get(self, id: str) -> Event:
    try:
        model = self._get(hash_key="EVENT", range_key=id)
        return self.mapper.to_entity(model)
    except DoesNotExist:
        raise NotFoundError(f"Event not found: {id}")
    except GetError as err:
        raise InternalServerError(f"Database error: {err}")

# API handler layer
@app.get("/events/<event_id>")
def get_event(event_id: str):
    try:
        event = event_repo.get(event_id)
        return event.model_dump(), 200
    except NotFoundError as err:
        return {"error": str(err)}, 404
    except InternalServerError as err:
        return {"error": "Internal server error"}, 500
```

---

### 8. Singleton Pattern

**Use Case**: AWS service clients (expensive to instantiate)

```python
from src.common.meta import SingletonMeta

class CloudwatchLogService(metaclass=SingletonMeta):
    """CloudWatch Logs client (singleton)."""

    def __init__(self, region=AWS_REGION, endpoint_url=AWS_ENDPOINT):
        self.client = boto3.client("logs", region_name=region, endpoint_url=endpoint_url)
```

**Benefit**: One boto3 client instance per Lambda container (reused across invocations)

---

## 🔗 Dependencies & Integrations

### Core Dependencies (`pyproject.toml`)

**Runtime Dependencies**:
```toml
[project.dependencies]
aws-lambda-powertools = "~3.20.0"    # Lambda utilities, logging, tracing
pydantic = "~2.11.0"                 # Data validation and serialization
pynamodb = "~6.1.0"                  # DynamoDB ORM
dependency-injector = "~4.48.0"      # Dependency injection container
jinja2 = "~3.1.0"                    # Template rendering (notifications)
pyjwt = "~2.8.0"                     # JWT token handling
bcrypt = "~4.1.2"                    # Password hashing
passlib[bcrypt] = "~1.7.4"           # Password utilities
requests = "~2.32.0"                 # HTTP client
uuid-utils = "~0.11.0"               # UUID7 generation
types-boto3[logs, ssm, ...] = "~1.40.0"  # Boto3 type hints
```

**Development Dependencies**:
```toml
[dependency-groups.local]
pre-commit = "~4.3.0"               # Git hooks
awscli = "~1.42.0"                  # AWS CLI
boto3 = "~1.40.0"                   # AWS SDK
ruff = "~0.14.0"                    # Linter and formatter
bandit = "~1.8.0"                   # Security linter
rich = "~14.2.0"                    # Terminal formatting

[dependency-groups.test]
pytest = "~8.4.0"                   # Testing framework
pytest-cov = "~7.0.0"               # Coverage reporting
moto = "~5.1.0"                     # AWS mocking
faker = "~37.12.0"                  # Test data generation
python-dotenv = "~1.1.0"            # Environment loading
```

---

### AWS Service Integrations

**DynamoDB**:
- **Purpose**: Primary data store (events, tasks, users, configs)
- **Client**: PynamoDB ORM
- **Configuration**: `AWS_DYNAMODB_TABLE` environment variable
- **Access Patterns**: Single-table design with GSI indexes

**EventBridge**:
- **Purpose**: Event routing and scheduled execution
- **Event Sources**:
  - CloudWatch Alarms
  - GuardDuty findings
  - AWS Health events
  - CloudFormation stack changes
  - Custom monitoring events
- **Targets**: HandleMonitoringEvents Lambda function

**CloudWatch Logs**:
- **Purpose**: Error log querying and analysis
- **Client**: boto3 CloudWatch Logs client
- **Query Method**: CloudWatch Logs Insights
- **Use Case**: QueryErrorLogs Lambda function

**Lambda**:
- **Runtime**: Python 3.13
- **Memory**: 256 MB (default)
- **Timeout**: 10 seconds (API), 60 seconds (background)
- **Layers**: PythonRequirementsLambdaLayer (dependencies)

**API Gateway**:
- **Type**: REST API
- **Resolver**: AWS Lambda Powertools APIGatewayRestResolver
- **CORS**: Configurable per stage
- **Authentication**: JWT Bearer tokens

**SNS** (Optional):
- **Purpose**: Email notifications (future feature)
- **Status**: Infrastructure defined, not actively used

**SQS** (Optional):
- **Purpose**: Event buffering (future feature)
- **Status**: Infrastructure defined, not actively used

---

### External Integrations

**Slack**:
- **Purpose**: Real-time monitoring notifications
- **Method**: Incoming webhooks
- **Configuration**: `MONITORING_WEBHOOK_URL` environment variable
- **Message Format**: Slack Block Kit (via Jinja2 templates)
- **Templates**:
  - `cloudwatch_alarm.jinja`
  - `guardduty.jinja`
  - `health.jinja`
  - `cfn_deployment.jinja`
  - `daily_report.jinja`

---

### Environment Variables

**Required**:
```bash
# AWS Configuration
AWS_REGION=us-east-1                          # Default AWS region
AWS_DYNAMODB_TABLE=monitoring-{stage}         # DynamoDB table name

# Authentication
JWT_SECRET_KEY=your-secret-key-here          # JWT signing secret
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15           # Access token lifetime
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7              # Refresh token lifetime

# Notifications
MONITORING_WEBHOOK_URL=https://hooks.slack.com/...  # Slack webhook URL

# Logging
POWERTOOLS_LOG_LEVEL=INFO                    # Log level (DEBUG, INFO, WARN, ERROR)
```

**Optional**:
```bash
# LocalStack (local development)
AWS_ENDPOINT=http://localhost:4566           # LocalStack endpoint
LOCALSTACK_HOSTNAME=localhost                # LocalStack hostname

# Service Metadata
SERVICE=monitoring                           # Service name
STAGE=local                                  # Deployment stage
```

---

## 🧪 Testing Organization

### Test Structure (`backend/tests/`)

```
tests/
├── adapters/                  # Adapter unit tests
│   └── repositories/
│       └── test_event.py     # EventRepository tests
├── integrations/             # Integration tests
│   ├── api/
│   │   └── test_events.py    # Events API tests
│   └── functions/
│       ├── test_handle_monitoring_events.py
│       ├── test_daily_report.py
│       └── test_query_error_logs.py
├── data/                     # Test fixtures
│   ├── alarm_event.json      # Sample CloudWatch alarm
│   ├── guardduty_event.json  # Sample GuardDuty finding
│   ├── health_event.json     # Sample Health event
│   ├── cloudformation_event.json
│   └── logs_event.json
├── conftest.py              # Pytest configuration and fixtures
└── mock.py                  # Mock utilities
```

---

### Test Fixtures (`conftest.py`)

**DynamoDB Mocking**:
```python
import pytest
from moto import mock_aws

@pytest.fixture(scope="function")
def dynamodb_table():
    """Create mocked DynamoDB table for testing."""
    with mock_aws():
        # Create table
        table = EventPersistence.create_table(
            read_capacity_units=1,
            write_capacity_units=1,
            wait=True,
        )
        yield table
        # Cleanup happens automatically with mock_aws context
```

**Test Data Factories**:
```python
from faker import Faker

fake = Faker()

@pytest.fixture
def sample_event():
    """Generate sample Event entity."""
    return Event(
        id=f"{int(time.time())}-{fake.uuid4()}",
        account="123456789012",
        region="us-east-1",
        source="aws.cloudwatch",
        detail_type="CloudWatch Alarm State Change",
        detail={"alarmName": fake.word()},
        severity=3,
        resources=[],
    )

@pytest.fixture
def sample_task():
    """Generate sample Task entity."""
    return Task(
        id=str(uuid7()),
        title=fake.sentence(),
        description=fake.text(),
        status=TaskStatus.OPEN,
        priority=TaskPriority.HIGH,
        assigned_user=AssignedUser(id=str(uuid7()), name=fake.name()),
        created_by=str(uuid7()),
    )
```

---

### Testing Patterns

**Repository Tests** (`tests/adapters/repositories/test_event.py`):
```python
def test_create_event(dynamodb_table, sample_event):
    """Test event creation in DynamoDB."""
    repo = EventRepository()

    # Create event
    repo.create(sample_event)

    # Verify persistence
    retrieved = repo.get(sample_event.id)
    assert retrieved.id == sample_event.id
    assert retrieved.severity == sample_event.severity

def test_list_events_with_date_filter(dynamodb_table):
    """Test event listing with date range."""
    repo = EventRepository()

    # Create events with different timestamps
    events = [create_event(published_at=ts) for ts in [100, 200, 300]]
    for event in events:
        repo.create(event)

    # Query with date filter
    dto = ListEventsDTO(start_date=150, end_date=250)
    result = repo.list(dto)

    # Verify filtering
    assert len(result.items) == 1
    assert result.items[0].published_at == 200
```

**Integration Tests** (`tests/integrations/functions/test_handle_monitoring_events.py`):
```python
@mock_aws
def test_handle_cloudwatch_alarm(alarm_event_json):
    """Test handling CloudWatch alarm event."""
    # Mock dependencies
    event_repo = EventRepository()
    notifier = MockNotifier()

    # Load test event
    event = EventBridgeEvent(alarm_event_json)

    # Execute handler
    insert_monitoring_event_use_case(event, event_repo, notifier)

    # Verify event stored
    events = event_repo.list()
    assert len(events.items) == 1
    assert events.items[0].source == "aws.cloudwatch"

    # Verify notification sent
    assert notifier.call_count == 1
```

**API Tests** (`tests/integrations/api/test_events.py`):
```python
def test_list_events_endpoint(api_client, sample_events, auth_token):
    """Test GET /events endpoint."""
    # Make request with auth
    response = api_client.get(
        "/events?limit=10&direction=desc",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "next" in data
    assert len(data["items"]) <= 10
```

---

### Running Tests

**Commands**:
```bash
# Run all tests
make test

# Run with coverage
make coverage

# Run specific test file
pytest tests/adapters/repositories/test_event.py -v

# Run specific test
pytest tests/adapters/repositories/test_event.py::test_create_event -v

# Run integration tests only
pytest tests/integrations/ -v
```

**Coverage Configuration** (`pyproject.toml`):
```toml
[tool.pytest.ini_options]
addopts = "-ra --cov=src"
testpaths = ["tests"]
```

---

## 🚀 Infrastructure & Deployment

### Serverless Framework Configuration

**Main Configuration** (`serverless.yml`):
```yaml
service: monitoring

provider:
  name: aws
  runtime: python3.13
  stage: ${opt:stage, "dev"}
  region: ${opt:region, "us-east-1"}
  stackName: monitoring-${self:provider.stage}

  # IAM role for Lambda functions
  role: LambdaFunctionRole

  # Lambda defaults
  memorySize: 256
  timeout: 10
  logRetentionInDays: 7

  # Layers
  layers:
    - !Ref PythonRequirementsLambdaLayer

  # Environment variables
  environment:
    AWS_DYNAMODB_TABLE: ${self:service}-${self:provider.stage}
    POWERTOOLS_LOG_LEVEL: INFO

# Functions (imported from separate files)
functions:
  # Background functions
  HandleMonitoringEvents: ${file(infra/functions/HandleMonitoringEvents.yml)}
  DailyReport: ${file(infra/functions/DailyReport.yml)}
  QueryErrorLogs: ${file(infra/functions/QueryErrorLogs.yml)}

  # API functions (33 endpoints)
  AuthLogin: ${file(infra/functions/api/Auth-Login.yml)}
  ListTasks: ${file(infra/functions/api/Tasks-List.yml)}
  # ... (see infra/functions/api/ for complete list)

# Resources (imported from separate files)
resources:
  - ${file(infra/resources/dynamodb.yml)}
  - ${file(infra/resources/event_bridge.yml)}
  - ${file(infra/resources/iam.yml)}
  - ${file(infra/resources/sqs.yml)}
```

---

### Stage Configurations

**Local Stage** (`infra/configs/local.yml`):
```yaml
Profile: default
Region: us-east-1

Lambda:
  LogRetentionInDays: 1
  Environment:
    LOG_LEVEL: DEBUG

DynamoDB:
  TableName: monitoring-local
```

**Production Stage** (`infra/configs/neos.yml`):
```yaml
Profile: production
Region: ap-southeast-1

Lambda:
  LogRetentionInDays: 30
  Environment:
    LOG_LEVEL: INFO

DynamoDB:
  TableName: monitoring-production

IAM:
  DeploymentRole: arn:aws:iam::ACCOUNT_ID:role/DeploymentRole

S3:
  DeploymentBucket:
    Name: monitoring-deployment-artifacts
```

---

### Function Definitions

**EventBridge-Triggered Function** (`infra/functions/HandleMonitoringEvents.yml`):
```yaml
function:
  name: ${self:service}-${self:provider.stage}-HandleMonitoringEvents
  handler: src.entrypoints.functions.handle_monitoring_events.main.handler
  timeout: 60
  events:
    - eventBridge:
        pattern:
          source:
            - aws.cloudwatch
            - aws.guardduty
            - aws.health
            - aws.cloudformation
            - monitoring.agent
```

**Scheduled Function** (`infra/functions/DailyReport.yml`):
```yaml
function:
  name: ${self:service}-${self:provider.stage}-DailyReport
  handler: src.entrypoints.functions.daily_report.main.handler
  timeout: 60
  events:
    - schedule:
        rate: cron(0 9 * * ? *)  # 9 AM UTC daily
        enabled: true
```

**API Gateway Function** (`infra/functions/api/Tasks-List.yml`):
```yaml
function:
  name: ${self:service}-${self:provider.stage}-Tasks-List
  handler: src.entrypoints.apigw.tasks.main.handler
  timeout: 10
  events:
    - httpApi:
        path: /tasks
        method: GET
```

---

### Resource Definitions

**DynamoDB Table** (`infra/resources/dynamodb.yml`):
```yaml
DynamoDBTable:
  Type: AWS::DynamoDB::Table
  UpdateReplacePolicy: Retain
  Properties:
    KeySchema:
      - AttributeName: pk
        KeyType: HASH
      - AttributeName: sk
        KeyType: RANGE
    AttributeDefinitions:
      - AttributeName: pk
        AttributeType: S
      - AttributeName: sk
        AttributeType: S
    BillingMode: PAY_PER_REQUEST
    PointInTimeRecoverySpecification:
      PointInTimeRecoveryEnabled: true
    TimeToLiveSpecification:
      AttributeName: expired_at
      Enabled: true
    TableName: ${self:service}-${self:provider.stage}
```

**EventBridge Rules** (`infra/resources/event_bridge.yml`):
```yaml
MonitoringEventRule:
  Type: AWS::Events::Rule
  Properties:
    EventBusName: default
    EventPattern:
      source:
        - aws.cloudwatch
        - aws.guardduty
        - aws.health
    Targets:
      - Arn: !GetAtt HandleMonitoringEventsLambdaFunction.Arn
        Id: HandleMonitoringEventsTarget
```

**IAM Roles** (`infra/resources/iam.yml`):
```yaml
LambdaFunctionRole:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Version: "2012-10-17"
      Statement:
        - Effect: Allow
          Principal:
            Service: lambda.amazonaws.com
          Action: sts:AssumeRole
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    Policies:
      - PolicyName: DynamoDBAccess
        PolicyDocument:
          Version: "2012-10-17"
          Statement:
            - Effect: Allow
              Action:
                - dynamodb:GetItem
                - dynamodb:PutItem
                - dynamodb:UpdateItem
                - dynamodb:DeleteItem
                - dynamodb:Query
                - dynamodb:Scan
              Resource:
                - !GetAtt DynamoDBTable.Arn
                - !Sub "${DynamoDBTable.Arn}/index/*"
      - PolicyName: CloudWatchLogsAccess
        PolicyDocument:
          Version: "2012-10-17"
          Statement:
            - Effect: Allow
              Action:
                - logs:StartQuery
                - logs:GetQueryResults
              Resource: "*"
```

---

### Deployment Workflows

**Development Workflow**:
```bash
# 1. Install dependencies
make install

# 2. Start LocalStack
make start

# 3. Deploy to local
make deploy stage=local

# 4. Run tests
make test

# 5. Stop LocalStack
make stop
```

**Production Deployment**:
```bash
# 1. Package for production
make package stage=prod

# 2. Review CloudFormation changeset
aws cloudformation describe-change-set --change-set-name <changeset-name>

# 3. Deploy to production
make deploy stage=prod

# 4. Verify deployment
make logs stage=prod
```

**Destruction**:
```bash
# Remove deployment
make destroy stage=local
```

---

## 📚 Usage Examples

### Creating and Using a New Use Case

**1. Define Domain Model** (`src/domain/models/notification.py`):
```python
from pydantic import BaseModel
from src.common.utils.datetime_utils import current_utc_timestamp

class Notification(BaseModel):
    id: str
    user_id: str
    message: str
    read: bool = False
    created_at: int = Field(default_factory=current_utc_timestamp)
```

**2. Define Repository Port** (`src/domain/ports/repositories.py`):
```python
class INotificationRepository(Protocol):
    def create(self, entity: Notification) -> None: ...
    def get_by_user(self, user_id: str) -> list[Notification]: ...
    def mark_as_read(self, notification_id: str) -> None: ...
```

**3. Implement Repository** (`src/adapters/db/repositories/notification.py`):
```python
class NotificationRepository(DynamoRepository):
    model_cls = NotificationPersistence
    mapper = NotificationMapper

    def create(self, entity: Notification) -> None:
        model = self.mapper.to_persistence(entity)
        self._create(model)

    def get_by_user(self, user_id: str) -> list[Notification]:
        result = self._query(
            hash_key=f"USER#{user_id}",
            index=self.model_cls.gsi1,
        )
        return [self.mapper.to_entity(item) for item in result]
```

**4. Create Use Case** (`src/domain/use_cases/notifications/create_notification.py`):
```python
from uuid_utils import uuid7

class CreateNotificationDTO(BaseModel):
    user_id: str
    message: str

class CreateNotification:
    def __init__(self, repository: NotificationRepository | None = None):
        self.repository = repository or NotificationRepository()

    def execute(self, dto: CreateNotificationDTO) -> Notification:
        notification = Notification(
            id=str(uuid7()),
            user_id=dto.user_id,
            message=dto.message,
        )
        self.repository.create(notification)
        return notification
```

**5. Create API Endpoint** (`src/entrypoints/apigw/notifications/main.py`):
```python
app = create_app(cors_allow_origin="*", cors_max_age=300)
create_notification_uc = CreateNotification()

@app.post("/notifications")
def create_notification(request: CreateNotificationRequest):
    auth = get_auth_context(app)

    dto = CreateNotificationDTO(
        user_id=request.user_id,
        message=request.message,
    )

    notification = create_notification_uc.execute(dto)
    return notification.model_dump(), HTTPStatus.CREATED

def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
```

**6. Define Lambda Function** (`infra/functions/api/Notifications-Create.yml`):
```yaml
function:
  name: ${self:service}-${self:provider.stage}-Notifications-Create
  handler: src.entrypoints.apigw.notifications.main.handler
  timeout: 10
  events:
    - httpApi:
        path: /notifications
        method: POST
```

**7. Register Function** (`serverless.yml`):
```yaml
functions:
  # ... existing functions
  CreateNotification: ${file(infra/functions/api/Notifications-Create.yml)}
```

---

### Adding a New Event Source

**1. Define Event Data Class** (`src/adapters/aws/data_classes.py`):
```python
class SecurityHubFindingEvent(EventBridgeEvent):
    """AWS Security Hub finding event."""

    @property
    def detail(self) -> "SecurityHubDetail":
        return SecurityHubDetail(self.raw_event["detail"])

class SecurityHubDetail:
    def __init__(self, detail: dict):
        self._detail = detail

    @property
    def finding_id(self) -> str:
        return self._detail["Id"]

    @property
    def severity(self) -> float:
        return self._detail["Severity"]["Normalized"]

    @property
    def title(self) -> str:
        return self._detail["Title"]
```

**2. Create Notification Template** (`statics/templates/securityhub.jinja`):
```jinja2
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "{{ emoji }} Security Hub Finding"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Finding:* {{ finding_title }}"
        },
        {
          "type": "mrkdwn",
          "text": "*Severity:* {{ severity_label }}"
        }
      ]
    }
  ]
}
```

**3. Add Notifier Handler** (`src/adapters/notifiers/events.py`):
```python
def securityhub_event_to_message(event: EventBridgeEvent) -> Message:
    event = SecurityHubFindingEvent(event)
    severity = SeverityLevel.from_score(event.detail.severity)

    return render_message(
        "securityhub.jinja",
        context={
            "emoji": ":shield:",
            "color": severity.color(),
            "finding_title": event.detail.title,
            "severity_label": severity.value,
            "account": event.account,
            "region": event.region,
        },
    )

# Update EventNotifier.event_to_message
def event_to_message(event: EventBridgeEvent) -> Message:
    match event.source:
        # ... existing cases
        case "aws.securityhub":
            return securityhub_event_to_message(event)
```

**4. Update EventBridge Rule** (`infra/resources/event_bridge.yml`):
```yaml
MonitoringEventRule:
  Type: AWS::Events::Rule
  Properties:
    EventPattern:
      source:
        - aws.cloudwatch
        - aws.guardduty
        - aws.health
        - aws.cloudformation
        - aws.securityhub  # Add new source
```

---

### Querying Events Programmatically

**By ID**:
```python
from src.adapters.db.repositories import EventRepository

repo = EventRepository()
event = repo.get("1732464000-abc123")
print(f"Event: {event.source} - {event.detail_type}")
```

**By Date Range**:
```python
from src.domain.models.event import ListEventsDTO
from datetime import datetime, timedelta

# Last 24 hours
end_time = int(datetime.now().timestamp())
start_time = int((datetime.now() - timedelta(days=1)).timestamp())

dto = ListEventsDTO(
    start_date=start_time,
    end_date=end_time,
    limit=50,
    direction="desc",
)

result = repo.list(dto)
print(f"Found {len(result.items)} events")
for event in result.items:
    print(f"- {event.get_severity_label()}: {event.detail_type}")
```

**By Source**:
```python
# Get all GuardDuty findings from last week
start_time = int((datetime.now() - timedelta(days=7)).timestamp())
events = repo.list_by_source("aws.guardduty", start_date=start_time)

print(f"GuardDuty findings: {len(events)}")
for event in events:
    if event.is_critical():
        print(f"CRITICAL: {event.detail}")
```

---

### Working with Tasks

**Create Task from Event**:
```python
from src.domain.use_cases.tasks import CreateTaskFromEvent, CreateTaskFromEventDTO
from src.domain.models.task import TaskPriority

uc = CreateTaskFromEvent()

dto = CreateTaskFromEventDTO(
    event_id="1732464000-abc123",
    assigned_user_id="user-456",
    priority=TaskPriority.HIGH,
    due_date=int((datetime.now() + timedelta(days=3)).timestamp()),
)

task = uc.execute(dto, created_by_user_id="admin-123")
print(f"Created task: {task.id}")
print(f"Linked to event: {task.event_id}")
```

**Filter Tasks**:
```python
from src.domain.use_cases.tasks import ListTasks, ListTasksDTO
from src.domain.models.task import TaskStatus, TaskPriority

uc = ListTasks()

# Get all open critical tasks
dto = ListTasksDTO(
    status=TaskStatus.OPEN,
    priority=TaskPriority.CRITICAL,
    page=1,
    page_size=20,
)

result = uc.execute(dto)
print(f"Found {result.total} critical open tasks")
for task in result.items:
    if task.is_overdue:
        print(f"OVERDUE: {task.title} (due: {task.due_date})")
```

**Add Comment to Task**:
```python
from src.domain.use_cases.tasks import AddCommentToTask, AddCommentDTO

uc = AddCommentToTask()

dto = AddCommentDTO(
    task_id="task-789",
    comment_text="Investigating root cause. Will update in 2 hours.",
)

task = uc.execute(dto, user_id="user-456")
print(f"Added comment. Total comments: {len(task.comments)}")
```

---

## 📊 Key Metrics & Insights

### Codebase Statistics

**Source Files**: ~100 Python files
- **Domain Layer**: ~15 models, ~35 use cases, 5 ports
- **Adapters Layer**: ~20 repositories/mappers, ~10 AWS clients, 3 notifiers
- **Entrypoints Layer**: 33 API endpoints, 3 Lambda functions
- **Common Layer**: ~10 utility modules

**Lines of Code**: ~8,000 LOC (excluding tests and infra)

**Test Coverage**: Target 80%+

---

### Component Distribution

**Use Cases by Domain**:
- Authentication: 5
- Tasks: 8
- Users: 6
- Events: 2
- Config: 5
- Dashboard: 4
- Background Jobs: 3

**Repository Implementations**: 5
- EventRepository
- TaskRepository
- UserRepository
- AwsConfigRepository
- MonitoringConfigRepository

**AWS Integrations**: 6
- DynamoDB (primary data store)
- EventBridge (event routing)
- CloudWatch Logs (log querying)
- Lambda (compute)
- API Gateway (HTTP interface)
- IAM (access control)

---

### Development Velocity

**Adding New Feature** (estimate):
- New domain model: 30 min
- Repository implementation: 1 hour
- Use case: 30 min
- API endpoint: 30 min
- Tests: 1 hour
- **Total**: ~3-4 hours for complete feature

**Infrastructure Changes**:
- New Lambda function: 15 min
- New API endpoint: 10 min
- New DynamoDB index: 30 min

---

## 🎓 Learning Resources

### Understanding the Architecture

**Read These Files First**:
1. `src/domain/models/event.py` - Domain model example
2. `src/domain/use_cases/tasks/create_task.py` - Use case pattern
3. `src/adapters/db/repositories/event.py` - Repository implementation
4. `src/entrypoints/apigw/events/main.py` - API handler pattern
5. `serverless.yml` - Infrastructure overview

**Key Patterns to Study**:
- Hexagonal Architecture: `src/domain/` ← `src/adapters/` ← `src/entrypoints/`
- Repository Pattern: `src/adapters/db/repositories/base.py`
- Data Mapper: `src/adapters/db/mappers/event.py`
- DTO Pattern: Look for `*DTO` classes in use cases

---

### Common Tasks

**Where to Add...**:
- New domain entity: `src/domain/models/`
- New business logic: `src/domain/use_cases/`
- New database query: `src/adapters/db/repositories/`
- New API endpoint: `src/entrypoints/apigw/`
- New Lambda function: `src/entrypoints/functions/`
- New AWS service client: `src/adapters/aws/`
- New notification template: `statics/templates/`

---

## 🔍 Index Summary

### Quick Lookup

**Find by Feature**:
- Events: `src/domain/models/event.py`, `src/adapters/db/repositories/event.py`
- Tasks: `src/domain/models/task.py`, `src/domain/use_cases/tasks/`
- Users: `src/domain/models/user.py`, `src/domain/use_cases/users/`
- Auth: `src/adapters/auth/`, `src/domain/use_cases/auth/`
- Config: `src/domain/models/config.py`, `src/domain/use_cases/config/`
- Dashboard: `src/domain/use_cases/dashboard/`
- Notifications: `src/adapters/notifiers/`

**Find by Layer**:
- Domain (Business Logic): `src/domain/`
- Adapters (External Systems): `src/adapters/`
- Entrypoints (User Interface): `src/entrypoints/`
- Common (Shared Utilities): `src/common/`

**Find by Technology**:
- DynamoDB: `src/adapters/db/`
- AWS Services: `src/adapters/aws/`
- API Gateway: `src/entrypoints/apigw/`
- Lambda Functions: `src/entrypoints/functions/`
- Slack: `src/adapters/notifiers/`, `statics/templates/`

---

### Navigation Tips

**Follow Dependency Flow**:
1. User Request → API Handler (`src/entrypoints/apigw/`)
2. API Handler → Use Case (`src/domain/use_cases/`)
3. Use Case → Repository (`src/adapters/db/repositories/`)
4. Repository → Database Model (`src/adapters/db/models/`)
5. Repository → Mapper → Domain Entity (`src/domain/models/`)

**Trace Event Flow**:
1. AWS Service → EventBridge → HandleMonitoringEvents
2. HandleMonitoringEvents → InsertMonitoringEvent use case
3. Use case → EventRepository → DynamoDB
4. Use case → EventNotifier → Slack

---

## 📝 Notes

- All timestamps are Unix timestamps (seconds since epoch)
- All entities use UUID7 for IDs (time-sortable)
- DynamoDB uses single-table design with composite keys
- Authentication uses JWT with 15-min access tokens, 7-day refresh tokens
- Password hashing uses bcrypt (cost factor: default)
- Event TTL: 90 days (configurable via `expired_at` field)
- Pagination uses cursor-based approach (base64-encoded `last_evaluated_key`)

---

**Index End** | Generated 2025-11-24 | Backend v1.0.0

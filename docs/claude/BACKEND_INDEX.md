# Backend Codebase Index

**Generated**: 2025-11-17
**Project**: AWS Monitoring Backend
**Architecture**: Hexagonal (Ports & Adapters)
**Language**: Python 3.13
**Framework**: Serverless Framework 4.x

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Directory Structure](#directory-structure)
- [Domain Layer Index](#domain-layer-index)
- [Adapters Layer Index](#adapters-layer-index)
- [Entrypoints Layer Index](#entrypoints-layer-index)
- [Common Layer Index](#common-layer-index)
- [Patterns & Conventions](#patterns--conventions)
- [Dependencies Map](#dependencies-map)
- [Testing Structure](#testing-structure)
- [Quick Reference](#quick-reference)

---

## Architecture Overview

### Hexagonal Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    ENTRYPOINTS                          │
│  Lambda Handlers | API Gateway | Event Triggers         │
├─────────────────────────────────────────────────────────┤
│                     USE CASES                           │
│  Business Logic Orchestration | Domain Rules            │
├─────────────────────────────────────────────────────────┤
│                      DOMAIN                             │
│  Models | Ports (Interfaces) | Business Entities        │
├─────────────────────────────────────────────────────────┤
│                     ADAPTERS                            │
│  DB | AWS Services | Notifications | External Systems   │
└─────────────────────────────────────────────────────────┘
```

**Dependency Rule**: Dependencies flow **inward** → Domain has zero external dependencies

---

## Directory Structure

```
backend/
├── src/                          # Source code
│   ├── domain/                   # 🎯 Core business logic
│   │   ├── models/               # Business entities
│   │   ├── ports/                # Interface contracts
│   │   └── use_cases/            # Business workflows
│   ├── adapters/                 # 🔌 External integrations
│   │   ├── db/                   # Database layer
│   │   │   ├── models/           # PynamoDB models
│   │   │   ├── mappers/          # Domain ↔ DB conversion
│   │   │   └── repositories/     # Data access implementations
│   │   ├── aws/                  # AWS service clients
│   │   └── notifiers/            # Notification services
│   ├── entrypoints/              # 🚪 Application entry points
│   │   ├── functions/            # Lambda handlers
│   │   └── apigw/                # API Gateway endpoints
│   └── common/                   # 🛠️ Shared utilities
│       ├── utils/                # Helper functions
│       ├── enums.py              # Type-safe enumerations
│       ├── constants.py          # Configuration
│       ├── exceptions.py         # Custom exceptions
│       └── logger.py             # Structured logging
├── statics/                      # Static assets
│   └── templates/                # Jinja2 notification templates
├── tests/                        # Test suite
│   ├── adapters/                 # Adapter tests
│   ├── integrations/             # Integration tests
│   │   ├── api/                  # API endpoint tests
│   │   └── functions/            # Lambda function tests
│   └── data/                     # Mock event data
├── pyproject.toml                # Project config & dependencies
└── serverless.yml                # Infrastructure definition
```

---

## Domain Layer Index

### 📦 Models (`src/domain/models/`)

Domain entities representing core business concepts with Pydantic validation.

#### Event Model (`event.py`)
```python
Event(BaseModel)
├── id: str                       # AWS EventID
├── account: str                  # AWS Account ID
├── region: str | None            # AWS Region
├── source: str                   # Event source (EventSource enum)
├── detail: dict                  # Event payload
├── detail_type: str | None       # Event classification
├── resources: list[str]          # Affected resources
├── published_at: int             # Unix timestamp
├── updated_at: int               # Unix timestamp
└── @property persistence_id      # Composite key: {timestamp}-{id}
```

**DTOs**:
- `ListEventsDTO(PaginatedInputDTO)` - Query filters with date range validation
- `EventQueryResult = QueryResult[Event]` - Paginated query results

#### Agent Model (`agent.py`)
```python
Agent(BaseModel)
├── id: str                       # AWS AccountID
├── region: str                   # Deployment region
├── status: str | None            # Agent health status
├── deployed_at: int              # Deployment timestamp
├── created_at: int               # Creation timestamp
└── @property persistence_id      # Returns id (AccountID)
```

**DTOs**:
- `UpdateAgentDTO(BaseModel)` - Partial update model
- `AgentQueryResult = QueryResult[Agent]` - Query results

#### Log Models (`logs.py`)
```python
LogEntry(BaseModel)
├── message: str                  # Log message
├── timestamp: str                # ISO timestamp
└── log_group: str                # Source log group

QueryLogsResult(BaseModel)
├── log_group_name: str           # Log group identifier
└── logs: list[LogEntry]          # Matching log entries
```

#### Base Models (`base.py`)
```python
PaginatedInputDTO(BaseModel)
├── limit: int = 50               # Page size
├── direction: str = "desc"       # Sort direction
└── cursor: str | None            # Pagination token

QueryResult[T](BaseModel)
├── items: list[T]                # Result items
├── cursor: dict | None           # Next page cursor
└── limit: int                    # Applied limit
```

### 🔌 Ports (`src/domain/ports/`)

Protocol interfaces defining contracts for external dependencies.

#### Repository Ports (`repositories.py`)
```python
IAgentRepository(Protocol)
├── get(id: str) → Agent
├── list() → AgentQueryResult
├── create(entity: Agent) → None
├── update(id: str, dto: UpdateAgentDTO) → None
├── delete(id: str) → None
└── exists(id: str) → bool

IEventRepository(Protocol)
├── get(id: str) → Event
├── list(dto: ListEventsDTO | None) → EventQueryResult
├── create(entity: Event) → None
└── delete(id: str) → None
```

#### Notifier Ports (`notifier.py`)
```python
IEventNotifier(Protocol)
└── notify(event: EventBridgeEvent) → None

IReportNotifier(Protocol)
└── report(events: list[Event]) → None
```

#### Publisher Ports (`publisher.py`)
```python
IPublisher(Protocol)
└── publish(events: list[EventEntry]) → None
```

#### Logs Ports (`logs.py`)
```python
ILogQueryService(Protocol)
└── query_logs(
    log_group_names: list[str],
    query_string: str,
    start_time: int,
    end_time: int
) → list[ResultFieldTypeDef]
```

### ⚙️ Use Cases (`src/domain/use_cases/`)

Business logic orchestration with minimal external dependencies.

#### Insert Monitoring Event (`insert_monitoring_event.py`)
**Purpose**: Process and persist incoming monitoring events
**Dependencies**: `IEventRepository`, `IEventNotifier`
**Flow**:
1. Convert EventBridge event to domain Event model
2. Persist event via repository
3. Send notification via notifier

```python
def insert_monitoring_event_use_case(
    event: EventBridgeEvent,
    event_repo: IEventRepository,
    notifier: IEventNotifier
)
```

#### Daily Report (`daily_report.py`)
**Purpose**: Generate and send daily monitoring summary
**Dependencies**: `IEventRepository`, `IReportNotifier`
**Flow**:
1. Query events from previous day (midnight to midnight UTC)
2. Aggregate events (up to 100 items)
3. Generate formatted report and send notification

```python
def daily_report_use_case(
    event_repo: IEventRepository,
    notifier: IReportNotifier
)
```

#### Query Error Logs (`query_error_logs.py`)
**Purpose**: Search CloudWatch logs for error patterns
**Dependencies**: `ILogQueryService`, `IPublisher`
**Flow**:
1. Query CloudWatch Logs Insights for error patterns
2. Aggregate results from multiple log groups
3. Publish results as monitoring events

```python
def query_error_logs_use_case(
    log_service: ILogQueryService,
    publisher: IPublisher,
    log_group_names: list[str],
    query_string: str,
    start_time: int,
    end_time: int
)
```

#### Update Deployment (`update_deployment.py`)
**Purpose**: Handle agent deployment status updates
**Dependencies**: `IAgentRepository`, `IEventNotifier`
**Flow**:
1. Update agent deployment metadata
2. Send deployment notification

```python
def update_deployment_use_case(
    agent_repo: IAgentRepository,
    notifier: IEventNotifier,
    agent_id: str,
    deployment_data: dict
)
```

---

## Adapters Layer Index

### 💾 Database Adapters (`src/adapters/db/`)

DynamoDB data layer with single-table design using PynamoDB ORM.

#### Database Models (`models/`)

PynamoDB models for DynamoDB persistence.

**Base Model** (`base.py`):
```python
DynamoModel(Model)
├── pk: UnicodeAttribute(hash_key=True)     # Partition key
├── sk: UnicodeAttribute(range_key=True)    # Sort key
└── Meta:
    ├── table_name: from AWS_DYNAMODB_TABLE
    ├── region: AWS_REGION
    └── host: AWS_ENDPOINT (LocalStack support)
```

**Event Persistence** (`event.py`):
```python
EventPersistence(DynamoModel)
├── pk: "EVENT"                   # Fixed partition key
├── sk: "{timestamp}-{event_id}"  # Sort key for time-based queries
├── account: str                  # AWS Account ID
├── region: str                   # AWS Region
├── source: str                   # Event source
├── detail: str                   # JSON-encoded event detail
├── detail_type: str              # Event classification
├── resources: list[str]          # Affected resources
├── published_at: int             # Unix timestamp
├── updated_at: int               # Unix timestamp
└── expired_at: int               # TTL attribute (7 days default)
```

**Agent Persistence** (`agent.py`):
```python
AgentPersistence(DynamoModel)
├── pk: "AGENT"                   # Fixed partition key
├── sk: "{account_id}"            # Account ID as sort key
├── region: str                   # Deployment region
├── status: str                   # Agent health status
├── deployed_at: int              # Deployment timestamp
└── created_at: int               # Creation timestamp
```

#### Mappers (`mappers/`)

Bidirectional converters between domain and persistence models.

**Event Mapper** (`event.py`):
```python
EventMapper
├── to_persistence(Event) → EventPersistence
│   ├── Converts domain Event to DynamoDB model
│   ├── JSON-encodes detail dict
│   └── Calculates TTL (published_at + AWS_DYNAMODB_TTL)
└── to_model(EventPersistence) → Event
    ├── Converts DynamoDB model to domain Event
    ├── JSON-decodes detail string
    └── Extracts event_id from composite SK
```

**Agent Mapper** (`agent.py`):
```python
AgentMapper
├── to_persistence(Agent) → AgentPersistence
└── to_model(AgentPersistence) → Agent
```

#### Repositories (`repositories/`)

Data access implementations using repository pattern.

**Base Repository** (`base.py`):
```python
DynamoRepository[M: DynamoModel]
├── Generic CRUD operations with exception handling
├── Methods:
│   ├── _get(hash_key, range_key) → M
│   ├── _query(hash_key, conditions, index, ...) → ResultIterator[M]
│   ├── _create(model: M) → None
│   ├── _update(hash_key, range_key, attributes) → None
│   ├── _delete(hash_key, range_key) → None
│   └── _count(hash_key, conditions) → int
└── Exception mapping:
    ├── DoesNotExist → NotFoundError
    ├── PutError (ConditionalCheckFailed) → ConflictError
    ├── GetError/QueryError → UnprocessedError
    └── Exception → InternalServerError
```

**Event Repository** (`event.py`):
```python
EventRepository(DynamoRepository)
├── Implements IEventRepository protocol
├── Methods:
│   ├── get(id: str) → Event
│   ├── list(dto: ListEventsDTO) → EventQueryResult
│   │   ├── Supports date range filtering
│   │   ├── Cursor-based pagination
│   │   └── Configurable sort direction
│   ├── create(entity: Event) → None
│   └── delete(id: str) → None
└── Access Pattern: Query by pk="EVENT", sk=between(start, end)
```

**Agent Repository** (`agent.py`):
```python
AgentRepository(DynamoRepository)
├── Implements IAgentRepository protocol
├── Methods:
│   ├── get(id: str) → Agent
│   ├── list() → AgentQueryResult
│   ├── create(entity: Agent) → None
│   ├── update(id: str, dto: UpdateAgentDTO) → None
│   ├── delete(id: str) → None
│   └── exists(id: str) → bool
└── Access Pattern: Query by pk="AGENT", sk={account_id}
```

### ☁️ AWS Service Adapters (`src/adapters/aws/`)

Client adapters for AWS services.

#### CloudWatch Logs Service (`cloudwatch.py`)
```python
CloudwatchLogService(metaclass=SingletonMeta)
├── query_logs(
│   log_group_names: list[str],
│   query_string: str,
│   start_time: int,
│   end_time: int,
│   timeout: int = 15,
│   delay: int = 1
│) → list[ResultFieldTypeDef]
├── Features:
│   ├── CloudWatch Logs Insights queries
│   ├── Synchronous polling with timeout
│   ├── Configurable delay between polls
│   └── Batch query support (multiple log groups)
└── Error Handling: RequestTimeoutError after timeout
```

#### EventBridge Publisher (`eventbridge.py`)
```python
EventBridgePublisher
├── publish(events: list[EventEntry]) → None
├── Features:
│   ├── Batch event publishing (max 10 per request)
│   ├── Automatic chunking for large batches
│   └── Custom event bus support
└── Configuration: EVENT_BUS_NAME from environment
```

#### ECS Service (`ecs.py`)
```python
ECSService
├── describe_tasks(cluster: str, tasks: list[str]) → dict
├── list_tasks(cluster: str, family: str) → list[str]
└── Features:
    ├── Task status queries
    ├── Task family filtering
    └── Container health checks
```

#### Lambda Service (`lambda_function.py`)
```python
LambdaService
├── invoke(function_name: str, payload: dict) → dict
├── Features:
│   ├── Synchronous invocation
│   ├── JSON payload encoding
│   └── Response parsing
└── Error Handling: Function errors, invocation failures
```

#### Data Classes (`data_classes.py`)
Event wrapper classes for type-safe event handling:
```python
EventBridgeEvent(BaseModel)
├── CwAlarmEvent              # CloudWatch Alarms
├── CwLogEvent                # CloudWatch Logs
├── GuardDutyFindingEvent     # GuardDuty findings
├── HealthEvent               # AWS Health events
├── CfnStackEvent             # CloudFormation stacks
└── Features:
    ├── Type-safe attribute access
    ├── Nested detail parsing
    └── Event source validation
```

### 📢 Notifier Adapters (`src/adapters/notifiers/`)

Notification service implementations.

#### Base Notifier (`base.py`)
```python
SlackClient
├── send(message: Message) → None
├── Features:
│   ├── Webhook-based Slack integration
│   ├── Markdown formatting support
│   └── Attachment blocks
└── Configuration: WEBHOOK_URL from environment

Message(BaseModel)
├── text: str                     # Plain text message
├── markdown: bool                # Enable markdown
└── blocks: list[dict] | None     # Slack block kit

render_message(template_file, context) → Message
├── Jinja2 template rendering
├── Template directory: statics/templates/
└── Returns formatted Slack message
```

#### Event Notifier (`events.py`)
```python
EventNotifier(IEventNotifier)
├── notify(event: EventBridgeEvent) → None
├── Event routing by source:
│   ├── aws.health → health_event_to_message()
│   ├── aws.guardduty → guardduty_event_to_message()
│   ├── aws.cloudwatch → cw_alarm_event_to_message()
│   ├── monitoring.agent.logs → cw_log_event_to_message()
│   └── aws.cloudformation → cfn_event_to_message()
└── Template files:
    ├── cloudwatch_alarm.jinja
    ├── cloudwatch_log.jinja
    ├── guardduty.jinja
    ├── health.jinja
    └── cfn_deployment.jinja
```

#### Report Notifier (`report.py`)
```python
ReportNotifier(IReportNotifier)
├── report(events: list[Event]) → None
├── Features:
│   ├── Daily aggregated event summary
│   ├── Event grouping by source
│   ├── Statistics and counts
│   └── Formatted Slack message
└── Template: daily_report.jinja
```

### 📤 Publisher Adapter (`publisher.py`)
```python
EventBridgePublisher(IPublisher)
├── publish(events: list[EventEntry]) → None
├── Features:
│   ├── Batch event publishing to EventBridge
│   ├── Custom event bus targeting
│   ├── Automatic chunking (10 events/batch)
│   └── Error handling and retry logic
└── Integration: AWS EventBridge service
```

---

## Entrypoints Layer Index

### ⚡ Lambda Functions (`src/entrypoints/functions/`)

Serverless function handlers implementing business workflows.

#### Handle Monitoring Events (`handle_monitoring_events/main.py`)
```python
handler(event: EventBridgeEvent, context) → None
├── Trigger: EventBridge events (Health, GuardDuty, CloudWatch, CloudFormation)
├── Dependencies:
│   ├── EventRepository()
│   └── EventNotifier(SlackClient)
├── Flow:
│   └── insert_monitoring_event_use_case(event, repo, notifier)
└── Configuration:
    ├── MONITORING_WEBHOOK_URL
    └── AWS_DYNAMODB_TABLE
```

**Event Sources**:
- `aws.health` - AWS Health events
- `aws.guardduty` - GuardDuty findings
- `aws.cloudwatch` - CloudWatch Alarms
- `aws.cloudformation` - CloudFormation stack events
- `monitoring.agent.*` - Custom monitoring events

#### Daily Report (`daily_report/main.py`)
```python
handler(event: dict, context) → None
├── Trigger: EventBridge scheduled rule (cron: 0 1 * * ? *)
├── Dependencies:
│   ├── EventRepository()
│   └── ReportNotifier(SlackClient)
├── Flow:
│   └── daily_report_use_case(event_repo, notifier)
└── Configuration:
    ├── REPORT_WEBHOOK_URL
    └── AWS_DYNAMODB_TABLE
```

**Schedule**: Daily at 01:00 UTC
**Report Period**: Previous day (00:00 - 23:59 UTC)
**Event Limit**: 100 most recent events

#### Query Error Logs (`query_error_logs/main.py`)
```python
handler(event: dict, context) → None
├── Trigger: EventBridge scheduled rule (rate: 1 hour)
├── Dependencies:
│   ├── CloudwatchLogService()
│   └── EventBridgePublisher()
├── Flow:
│   ├── Query CloudWatch Logs for ERROR level entries
│   ├── Aggregate results from multiple log groups
│   └── Publish findings as monitoring events
└── Configuration:
    ├── LOG_GROUPS: list[str] (from event payload)
    ├── QUERY_STRING: str (default: ERROR filter)
    └── TIME_RANGE: Previous 1 hour
```

**Query Pattern**:
```sql
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 20
```

#### Update Deployment (`update_deployment/main.py`)
```python
handler(event: dict, context) → None
├── Trigger: Manual invocation or CI/CD pipeline
├── Dependencies:
│   ├── AgentRepository()
│   └── EventNotifier(SlackClient)
├── Flow:
│   ├── Parse deployment event
│   ├── Update agent metadata in database
│   └── Send deployment notification
└── Configuration:
    ├── DEPLOYMENT_WEBHOOK_URL
    └── AWS_DYNAMODB_TABLE
```

**Event Payload**:
```json
{
  "agent_id": "123456789012",
  "region": "us-east-1",
  "status": "DEPLOYED",
  "deployed_at": 1699564800
}
```

### 🌐 API Gateway Endpoints (`src/entrypoints/apigw/`)

REST API endpoints for querying monitoring data.

#### Events API (`events/main.py`)
```python
app = create_app(cors_allow_origin, cors_max_age)

@app.get("/events/<event_id>")
├── Get single event by ID
├── Response: Event JSON
└── Errors:
    ├── 404: Event not found
    └── 500: Internal server error

@app.get("/events")
├── List events with filtering and pagination
├── Query Parameters:
│   ├── start_date: int (Unix timestamp)
│   ├── end_date: int (Unix timestamp)
│   ├── limit: int = 50 (max 100)
│   ├── direction: "asc" | "desc" = "desc"
│   └── cursor: str (pagination token)
├── Response:
│   ├── items: list[Event]
│   ├── limit: int
│   ├── next: str | None (cursor)
│   └── previous: str | None (cursor)
└── Errors:
    ├── 400: Invalid query parameters
    └── 500: Internal server error
```

**Example Request**:
```bash
GET /events?start_date=1699564800&end_date=1699651200&limit=10&direction=desc
```

**Example Response**:
```json
{
  "items": [
    {
      "id": "event-123",
      "account": "123456789012",
      "region": "us-east-1",
      "source": "aws.cloudwatch",
      "detail_type": "CloudWatch Alarm State Change",
      "detail": {...},
      "published_at": 1699564800,
      "updated_at": 1699564800
    }
  ],
  "limit": 10,
  "next": "eyJwayI6IkVWRU5UIiwic2siOiIxNjk5NTY0ODAwLWV2ZW50LTEyMyJ9",
  "previous": null
}
```

#### Agents API (`agents/main.py`)
```python
app = create_app(cors_allow_origin, cors_max_age)

@app.get("/agents/<agent_id>")
├── Get agent by account ID
├── Response: Agent JSON
└── Errors:
    ├── 404: Agent not found
    └── 500: Internal server error

@app.get("/agents")
├── List all registered agents
├── Response:
│   └── items: list[Agent]
└── Errors:
    └── 500: Internal server error

@app.post("/agents")
├── Register new monitoring agent
├── Request Body: Agent JSON
├── Response: Created Agent
└── Errors:
    ├── 400: Invalid request body
    ├── 409: Agent already exists
    └── 500: Internal server error

@app.patch("/agents/<agent_id>")
├── Update agent metadata
├── Request Body: UpdateAgentDTO JSON
├── Response: Updated Agent
└── Errors:
    ├── 400: Invalid request body
    ├── 404: Agent not found
    └── 500: Internal server error

@app.delete("/agents/<agent_id>")
├── Delete agent registration
├── Response: 204 No Content
└── Errors:
    ├── 404: Agent not found
    └── 500: Internal server error
```

#### Base API Configuration (`base.py`)
```python
create_app(cors_allow_origin, cors_max_age) → APIGatewayRestResolver
├── Features:
│   ├── CORS configuration
│   ├── OpenAPI documentation
│   ├── Request validation
│   ├── Error handling
│   └── Response serialization
└── Middleware:
    ├── Exception handler
    ├── Request logger
    └── CORS headers
```

#### API Configuration (`configs.py`)
```python
CORS_ALLOW_ORIGIN: str = "*"
CORS_MAX_AGE: int = 86400
API_VERSION: str = "v1"
```

---

## Common Layer Index

### 🛠️ Utilities (`src/common/utils/`)

Shared helper functions and utilities.

#### DateTime Utilities (`datetime_utils.py`)
```python
current_utc_timestamp() → int
├── Returns current Unix timestamp (UTC)
└── Usage: Default timestamp for models

datetime_str_to_timestamp(dt_str: str) → int
├── Converts ISO datetime string to Unix timestamp
└── Format: "2024-11-17T12:00:00Z"

timestamp_to_datetime_str(timestamp: int) → str
├── Converts Unix timestamp to ISO datetime string
└── Returns: "2024-11-17T12:00:00Z"
```

#### Encoding Utilities (`encoding.py`)
```python
json_to_base64(data: dict) → str
├── Encodes JSON dict to base64 string
└── Usage: Pagination cursors

base64_to_json(encoded: str) → dict
├── Decodes base64 string to JSON dict
└── Usage: Cursor deserialization
```

#### Object Utilities (`objects.py`)
```python
chunks(lst: list, chunk_size: int) → Generator
├── Splits list into fixed-size chunks
├── Usage: Batch processing (CloudWatch queries, EventBridge publishes)
└── Example: chunks(log_groups, 10) for CloudWatch limits

remove_none_values(d: dict) → dict
├── Removes None values from dictionary
└── Usage: Clean API responses

deep_merge(dict1: dict, dict2: dict) → dict
├── Recursively merges two dictionaries
└── Usage: Configuration merging
```

#### Template Utilities (`template.py`)
```python
render_template(template_file: str, context: dict) → str
├── Renders Jinja2 template with context
├── Template directory: statics/templates/
└── Usage: Notification message formatting

get_template_path(filename: str) → Path
├── Returns absolute path to template file
└── Usage: Template resolution
```

### 📊 Enumerations (`src/common/enums.py`)

Type-safe enumerations for business logic.

#### Event Source (`EventSource`)
```python
EventSource(str, Enum)
├── AWS native sources:
│   ├── AWS_HEALTH = "aws.health"
│   ├── AWS_GUARDDUTY = "aws.guardduty"
│   ├── AWS_CLOUDWATCH = "aws.cloudwatch"
│   └── AWS_CLOUDFORMATION = "aws.cloudformation"
└── Monitoring agent sources:
    ├── AGENT_HEALTH = "monitoring.agent.health"
    ├── AGENT_GUARDDUTY = "monitoring.agent.guardduty"
    ├── AGENT_CLOUDWATCH = "monitoring.agent.cloudwatch"
    ├── AGENT_LOGS = "monitoring.agent.logs"
    └── AGENT_CLOUDFORMATION = "monitoring.agent.cloudformation"
```

#### Alarm State (`AlarmState`)
```python
AlarmState(str, Enum)
├── ALARM = "ALARM"
├── OK = "OK"
├── INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
├── Methods:
│   ├── emoji() → str (":red_circle:", ":recycle:", ...)
│   └── color() → str ("#FF0000", "#36A64F", ...)
└── Usage: CloudWatch alarm notifications
```

#### Severity Level (`SeverityLevel`)
```python
SeverityLevel(str, Enum)
├── HIGH = "HIGH"
├── MEDIUM = "MEDIUM"
├── LOW = "LOW"
├── Methods:
│   ├── from_score(score: float) → SeverityLevel
│   │   ├── ≥7.0 → HIGH
│   │   ├── ≥4.0 → MEDIUM
│   │   └── <4.0 → LOW
│   └── color() → str ("#FF0000", "#FFA500", "#36A64F")
└── Usage: GuardDuty findings, security alerts
```

#### Health Event Category (`HealthEventCategory`)
```python
HealthEventCategory(str, Enum)
├── ISSUE = "issue"
├── ACCOUNT_NOTIFICATION = "accountnotification"
├── SCHEDULED_CHANGE = "scheduledchange"
├── Methods:
│   └── emoji() → str (":warning:", ":information_source:", ...)
└── Usage: AWS Health event notifications
```

#### Health Event Status (`HealthEventStatus`)
```python
HealthEventStatus(str, Enum)
├── OPEN = "open"
├── CLOSED = "closed"
├── UPCOMING = "upcoming"
├── Methods:
│   └── color() → str ("#FFA500", "#36A64F", "#439FE0")
└── Usage: AWS Health event tracking
```

#### CloudFormation Stack Status (`CfnStackStatusType`)
```python
CfnStackStatusType(str, Enum)
├── SUCCESS = "SUCCESS"
├── FAILURE = "FAILURE"
├── WARNING = "WARNING"
├── Methods:
│   ├── emoji() → str (":rocket:", ":x:", ":warning:")
│   └── color() → str ("#36A64F", "#FF0000", "#FFA500")
└── Usage: CloudFormation deployment notifications
```

### ⚠️ Exceptions (`src/common/exceptions.py`)

Custom exception hierarchy for domain-specific errors.

```python
# Base exceptions
class MonitoringException(Exception)
    """Base exception for all monitoring errors"""

# HTTP-style exceptions
class NotFoundError(MonitoringException)
    """Resource not found (HTTP 404)"""

class ConflictError(MonitoringException)
    """Resource conflict (HTTP 409)"""

class UnprocessedError(MonitoringException)
    """Unprocessable entity (HTTP 422)"""

class InternalServerError(MonitoringException)
    """Internal server error (HTTP 500)"""

class RequestTimeoutError(MonitoringException)
    """Request timeout (HTTP 408)"""

# Usage in repositories
try:
    model = self.model_cls.get(hash_key, range_key)
except DoesNotExist:
    raise NotFoundError(f"Entity not found: {hash_key}")
```

### 🔧 Configuration (`src/common/constants.py`)

Environment-based configuration constants.

```python
# File & Directory
BASE_DIR: Path                    # Project root
STATIC_DIR: Path                  # Static assets
TEMPLATE_DIR: Path                # Jinja2 templates

# Common
SERVICE: str = "monitoring"
STAGE: str = "dev" | "local" | "prod"

# Logging
LOG_LEVEL: str = "DEBUG" | "INFO" | "WARNING" | "ERROR"
LOG_EVENT: bool = True

# AWS
AWS_REGION: str                   # AWS region (e.g., "us-east-1")
AWS_ENDPOINT: str | None          # LocalStack endpoint for local dev

# DynamoDB
AWS_DYNAMODB_TABLE: str           # Table name (e.g., "monitoring-local")
AWS_DYNAMODB_TTL: int = 604800    # TTL in seconds (7 days)
AWS_DYNAMODB_DEFAULT_QUERY_LIMIT: int = 50

# Webhook URLs (required)
MONITORING_WEBHOOK_URL: str       # Event notifications
REPORT_WEBHOOK_URL: str           # Daily reports
DEPLOYMENT_WEBHOOK_URL: str       # Deployment notifications

# Template Files
CW_ALARM_TEMPLATE_FILE: str = "cloudwatch_alarm.jinja"
CW_LOG_TEMPLATE_FILE: str = "cloudwatch_log.jinja"
GUARDDUTY_TEMPLATE_FILE: str = "guardduty.jinja"
HEALTH_TEMPLATE_FILE: str = "health.jinja"
CFN_TEMPLATE_FILE: str = "cfn_deployment.jinja"
REPORT_TEMPLATE_FILE: str = "daily_report.jinja"

# Account Metadata
METADATA: dict[str, str]          # Account ID → Name mapping
```

### 📝 Logging (`src/common/logger.py`)

Structured logging with AWS Lambda Powertools.

```python
from src.common.logger import logger

# Logging methods
logger.debug("Debug message", extra={"key": "value"})
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Exception with traceback")

# Lambda context injection
@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    logger.info("Processing event")
```

**Features**:
- JSON structured logging
- Lambda context injection
- Correlation ID tracking
- Log level configuration via environment
- Exception stack traces

---

## Patterns & Conventions

### 🏗️ Architectural Patterns

#### Hexagonal Architecture (Ports & Adapters)
```
[Entrypoint] → [Use Case] → [Port Interface] ← [Adapter]
                    ↓
               [Domain Model]
```

**Key Principles**:
1. **Domain Independence**: Domain layer has zero external dependencies
2. **Dependency Inversion**: Adapters depend on domain ports, not vice versa
3. **Testability**: Business logic testable without external systems
4. **Flexibility**: Swap adapters without changing domain logic

**Example**:
```python
# Domain Port (interface)
class IEventRepository(Protocol):
    def create(self, entity: Event) -> None: ...

# Adapter Implementation
class EventRepository(DynamoRepository):
    def create(self, entity: Event) -> None:
        model = EventMapper.to_persistence(entity)
        self._create(model)

# Use Case (uses port)
def insert_event(event_repo: IEventRepository, event_data: dict):
    event = Event(**event_data)
    event_repo.create(event)  # Works with any IEventRepository implementation
```

#### Repository Pattern
```python
class BaseRepository[M: DynamoModel]:
    """Generic repository with CRUD operations"""

    def _get(self, hash_key, range_key=None) → M: ...
    def _query(self, hash_key, conditions) → ResultIterator[M]: ...
    def _create(self, model: M) → None: ...
    def _update(self, hash_key, attributes) → None: ...
    def _delete(self, hash_key, range_key=None) → None: ...
```

**Benefits**:
- Abstracted data access
- Centralized exception handling
- Consistent error mapping
- Generic CRUD operations

#### Mapper Pattern
```python
class EventMapper:
    @classmethod
    def to_persistence(cls, domain: Event) → EventPersistence:
        """Domain → Database conversion"""
        ...

    @classmethod
    def to_model(cls, persistence: EventPersistence) → Event:
        """Database → Domain conversion"""
        ...
```

**Purpose**: Decouple domain models from persistence models

### 📝 Naming Conventions

#### Python Code Style
```python
# Classes: PascalCase
class EventRepository: ...
class MonitoringException: ...

# Functions/Methods: snake_case
def insert_monitoring_event(): ...
def query_error_logs(): ...

# Constants: UPPER_SNAKE_CASE
AWS_REGION = "us-east-1"
DYNAMODB_TABLE = "monitoring-local"

# Private methods: _leading_underscore
def _validate_event(self): ...
def _create(self, model): ...

# Type variables: PascalCase with suffix
M = TypeVar("M", bound=BaseModel)
T = TypeVar("T")
```

#### File Organization
```python
# Domain models: singular noun
event.py          # Event model
agent.py          # Agent model

# Repositories: plural noun
repositories/event.py     # EventRepository
repositories/agent.py     # AgentRepository

# Use cases: verb + noun
insert_monitoring_event.py
query_error_logs.py
update_deployment.py

# Lambda handlers: always main.py
functions/handle_monitoring_events/main.py
functions/daily_report/main.py
```

### 🔍 Error Handling Patterns

#### Repository Exception Mapping
```python
try:
    model = self.model_cls.get(hash_key, range_key)
except DoesNotExist as err:
    raise NotFoundError(f"Resource not found: {err}")
except GetError as err:
    raise UnprocessedError(f"Database error: {err}")
except Exception as err:
    logger.exception("Unexpected error")
    raise InternalServerError(f"Internal error: {err}")
```

#### Use Case Error Handling
```python
def insert_monitoring_event_use_case(event, repo, notifier):
    try:
        # Business logic
        event_model = Event(**event.detail)
        repo.create(event_model)
        notifier.notify(event)
    except NotFoundError:
        logger.error("Event not found")
        raise
    except Exception:
        logger.exception("Unexpected error in use case")
        raise
```

#### Lambda Handler Error Pattern
```python
def handler(event, context):
    try:
        # Process event
        insert_monitoring_event_use_case(event, repo, notifier)
    except MonitoringException as err:
        logger.error(f"Business error: {err}")
        raise
    except Exception:
        logger.exception("Fatal error in handler")
        raise
```

### ✅ Validation Patterns

#### Pydantic Model Validation
```python
class ListEventsDTO(PaginatedInputDTO):
    start_date: int | None = None
    end_date: int | None = None

    @model_validator(mode="after")
    def validate_model(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must be <= end_date")
        return self
```

#### Field Validation
```python
class Event(BaseModel):
    id: str
    severity: str

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not value:
            raise ValueError("ID cannot be empty")
        return value

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: str) -> str:
        allowed = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if value.upper() not in allowed:
            raise ValueError(f"Severity must be one of {allowed}")
        return value.upper()
```

### 🧪 Testing Patterns

#### Repository Testing with Moto
```python
import pytest
from moto import mock_aws

@mock_aws
def test_create_event():
    # Arrange
    repo = EventRepository()
    event = Event(id="test-123", account="000000000000", ...)

    # Act
    repo.create(event)

    # Assert
    retrieved = repo.get("test-123")
    assert retrieved.id == "test-123"
```

#### Integration Testing Pattern
```python
def test_insert_monitoring_event_integration(sample_event):
    # Arrange
    event_repo = EventRepository()
    notifier = Mock(spec=IEventNotifier)

    # Act
    insert_monitoring_event_use_case(sample_event, event_repo, notifier)

    # Assert
    assert event_repo.exists(sample_event.id)
    notifier.notify.assert_called_once()
```

### 🔄 Dependency Injection

#### Constructor Injection
```python
class InsertMonitoringEvent:
    def __init__(self, repo: IEventRepository, notifier: IEventNotifier):
        self.repo = repo
        self.notifier = notifier

    def execute(self, event_data: dict) -> Event:
        event = Event(**event_data)
        saved = self.repo.create(event)
        self.notifier.notify(event)
        return saved
```

#### Lambda Handler Initialization
```python
# Module-level initialization (reused across invocations)
event_repo = EventRepository()
notifier = EventNotifier(SlackClient(MONITORING_WEBHOOK_URL))

def handler(event, context):
    insert_monitoring_event_use_case(event, event_repo, notifier)
```

### 📊 Data Access Patterns

#### Single-Table Design
```
DynamoDB Table: monitoring-{stage}

PK (Hash)    SK (Sort Key)              Attributes
------------ -------------------------- --------------------
EVENT        {timestamp}-{event_id}     account, region, source, detail, ...
AGENT        {account_id}               region, status, deployed_at, ...
```

**Benefits**:
- Efficient queries with composite keys
- Reduced costs (single table)
- Flexible access patterns

#### Query Patterns
```python
# Get single event
repo.get(id="event-123")
# Query: PK="EVENT", SK=contains("event-123")

# List events by date range
repo.list(ListEventsDTO(start_date=1699564800, end_date=1699651200))
# Query: PK="EVENT", SK between (start_date, end_date)

# Get agent by account ID
agent_repo.get(id="123456789012")
# Query: PK="AGENT", SK="123456789012"
```

#### Cursor-Based Pagination
```python
# First page
result = repo.list(ListEventsDTO(limit=10))
cursor = json_to_base64(result.cursor)

# Next page
next_result = repo.list(ListEventsDTO(limit=10, cursor=cursor))
```

---

## Dependencies Map

### 📦 Core Dependencies

#### Runtime Dependencies
```toml
aws-lambda-powertools = "~3.20.0"    # Lambda utilities, logging, tracing
pydantic = "~2.11.0"                 # Data validation and serialization
pynamodb = "~6.1.0"                  # DynamoDB ORM
requests = "~2.32.0"                 # HTTP client for webhooks
jinja2 = "~3.1.0"                    # Template rendering
uuid-utils = "~0.11.0"               # UUID utilities
```

#### AWS SDK Types
```toml
types-boto3[logs, ssm, health, events, ecs, lambda] = "~1.40.0"
# Type stubs for:
# - CloudWatch Logs
# - Systems Manager (SSM)
# - AWS Health
# - EventBridge
# - ECS
# - Lambda
```

#### Development Dependencies
```toml
pytest = "~8.4.0"              # Testing framework
pytest-cov = "~7.0.0"          # Coverage reporting
moto = "~5.1.0"                # AWS service mocking
faker = "~37.12.0"             # Test data generation
ruff = "~0.14.0"               # Linting and formatting
bandit = "~1.8.0"              # Security linting
pre-commit = "~4.3.0"          # Git hooks
```

### 🔗 Dependency Flow

#### Inward Dependencies (following hexagonal architecture)
```
Entrypoints
    ↓ depends on
Use Cases
    ↓ depends on
Domain Ports (Interfaces)
    ↑ implemented by
Adapters
```

**Example**:
```python
# Lambda handler (entrypoint)
from src.domain.use_cases.insert_monitoring_event import insert_monitoring_event_use_case
from src.adapters.db.repositories import EventRepository
from src.adapters.notifiers import EventNotifier

# Use case (domain)
from src.domain.ports.repositories import IEventRepository
from src.domain.ports.notifier import IEventNotifier

# Repository (adapter)
from src.domain.models import Event
from src.adapters.db.models import EventPersistence
```

### 🌐 External System Integration

#### AWS Services Integration
```python
# CloudWatch Logs
boto3.client("logs") → CloudwatchLogService
├── Used by: query_error_logs_use_case
└── Features: Logs Insights queries

# DynamoDB
pynamodb.models.Model → EventPersistence, AgentPersistence
├── Used by: All repositories
└── Features: Single-table design, TTL, GSI

# EventBridge
boto3.client("events") → EventBridgePublisher
├── Used by: query_error_logs_use_case
└── Features: Event publishing, custom buses

# Lambda
boto3.client("lambda") → LambdaService
├── Used by: Cross-function invocations
└── Features: Synchronous invocation

# ECS
boto3.client("ecs") → ECSService
├── Used by: Agent health checks
└── Features: Task status queries
```

#### Webhook Integrations
```python
# Slack (via webhook)
requests.post(webhook_url, json=message)
├── Used by: EventNotifier, ReportNotifier
└── Configuration: MONITORING_WEBHOOK_URL, REPORT_WEBHOOK_URL
```

---

## Testing Structure

### 🧪 Test Organization

```
tests/
├── adapters/                     # Adapter layer tests
│   └── repositories/             # Repository tests with moto
│       ├── test_event.py         # EventRepository tests
│       └── test_account.py       # AgentRepository tests (legacy name)
├── integrations/                 # Integration tests
│   ├── api/                      # API Gateway tests
│   │   ├── test_events.py        # Events API endpoints
│   │   └── test_agents.py        # Agents API endpoints
│   └── functions/                # Lambda function tests
│       ├── test_handle_monitoring_events.py
│       ├── test_daily_report.py
│       ├── test_query_error_logs.py
│       └── test_update_agent_deployment.py
├── data/                         # Mock event data (JSON)
│   ├── alarm_event.json
│   ├── cloudformation_event.json
│   ├── guardduty_event.json
│   ├── health_event.json
│   └── logs_event.json
├── conftest.py                   # Pytest fixtures and configuration
└── mock.py                       # Mock utilities and helpers
```

### 📊 Test Coverage

**Current Coverage**: ~88%
**Target Coverage**: >90% for new features

**Coverage by Layer**:
- Domain models: 100% (Pydantic auto-validation)
- Use cases: ~85%
- Repositories: ~90%
- Lambda handlers: ~80%
- API endpoints: ~85%

**Commands**:
```bash
# Run tests with coverage
poetry run pytest tests/ --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/integrations/api/test_events.py -v

# Run tests matching pattern
poetry run pytest tests/ -k "event" -v
```

### 🏷️ Test Fixtures

**Common Fixtures** (`conftest.py`):
```python
@pytest.fixture
def sample_event() → dict
    """Sample EventBridge event"""

@pytest.fixture
def event_repository() → EventRepository
    """Initialized EventRepository with mocked DynamoDB"""

@pytest.fixture
def agent_repository() → AgentRepository
    """Initialized AgentRepository with mocked DynamoDB"""

@pytest.fixture
def mock_notifier() → Mock
    """Mocked IEventNotifier"""

@pytest.fixture
def mock_slack_client() → Mock
    """Mocked SlackClient"""
```

### 🎭 Mocking Strategies

#### AWS Service Mocking with Moto
```python
from moto import mock_aws

@mock_aws
def test_create_event(event_repository, sample_event):
    # Moto intercepts boto3 calls
    event = Event(**sample_event)
    event_repository.create(event)

    # Verify persistence
    retrieved = event_repository.get(event.id)
    assert retrieved.id == event.id
```

#### Dependency Mocking with unittest.mock
```python
from unittest.mock import Mock, patch

def test_insert_event_with_notification():
    # Arrange
    repo = Mock(spec=IEventRepository)
    notifier = Mock(spec=IEventNotifier)

    # Act
    insert_monitoring_event_use_case(event, repo, notifier)

    # Assert
    repo.create.assert_called_once()
    notifier.notify.assert_called_once()
```

### 📂 Test Data

**Mock Event Files** (`tests/data/`):
```json
// alarm_event.json
{
  "id": "alarm-123",
  "source": "aws.cloudwatch",
  "detail-type": "CloudWatch Alarm State Change",
  "detail": {
    "alarmName": "HighCPUAlarm",
    "state": { "value": "ALARM" }
  }
}

// guardduty_event.json
{
  "id": "finding-123",
  "source": "aws.guardduty",
  "detail": {
    "severity": 8.0,
    "title": "Suspicious EC2 instance behavior"
  }
}
```

**Usage**:
```python
import json
from pathlib import Path

def load_test_event(filename: str) -> dict:
    path = Path(__file__).parent / "data" / filename
    return json.loads(path.read_text())

# In tests
alarm_event = load_test_event("alarm_event.json")
```

---

## Quick Reference

### 🔑 Key Files Locations

#### Domain Layer
```
src/domain/
├── models/event.py              # Event domain model
├── models/agent.py              # Agent domain model
├── ports/repositories.py        # Repository interfaces
├── use_cases/insert_monitoring_event.py
├── use_cases/daily_report.py
└── use_cases/query_error_logs.py
```

#### Adapters Layer
```
src/adapters/
├── db/repositories/event.py     # EventRepository implementation
├── db/repositories/agent.py     # AgentRepository implementation
├── aws/cloudwatch.py            # CloudWatch Logs client
├── aws/eventbridge.py           # EventBridge publisher
└── notifiers/events.py          # Event notification routing
```

#### Entrypoints Layer
```
src/entrypoints/
├── functions/
│   ├── handle_monitoring_events/main.py
│   ├── daily_report/main.py
│   └── query_error_logs/main.py
└── apigw/
    ├── events/main.py           # Events API
    └── agents/main.py           # Agents API
```

#### Configuration
```
backend/
├── .env.local                   # Local environment variables
├── pyproject.toml               # Python dependencies
├── serverless.yml               # Infrastructure definition
└── src/common/constants.py      # Configuration constants
```

### 🚀 Common Commands

#### Development
```bash
# Install dependencies
make install

# Run tests
make test

# Generate coverage
make coverage

# Start LocalStack
make start

# Deploy to local
make deploy stage=local
```

#### Database Operations
```bash
# List DynamoDB tables
aws dynamodb list-tables --endpoint-url=http://localhost:4566 --region us-east-1

# Describe table
aws dynamodb describe-table \
  --table-name monitoring-local \
  --endpoint-url=http://localhost:4566 \
  --region us-east-1

# Scan table
aws dynamodb scan \
  --table-name monitoring-local \
  --endpoint-url=http://localhost:4566 \
  --region us-east-1
```

#### Testing
```bash
# Run all tests
poetry run pytest tests/

# Run specific test
poetry run pytest tests/integrations/api/test_events.py::test_get_event -v

# Run with coverage
poetry run pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### 📊 Access Patterns

#### DynamoDB Query Patterns
```python
# Get event by ID
event = event_repo.get("event-123")

# List events with date range
events = event_repo.list(ListEventsDTO(
    start_date=1699564800,
    end_date=1699651200,
    limit=50,
    direction="desc"
))

# Get agent by account ID
agent = agent_repo.get("123456789012")

# List all agents
agents = agent_repo.list()
```

#### API Endpoints
```bash
# Get event
GET /events/{event_id}

# List events
GET /events?start_date=1699564800&end_date=1699651200&limit=50&direction=desc

# Get agent
GET /agents/{agent_id}

# List agents
GET /agents

# Create agent
POST /agents
Content-Type: application/json
{ "id": "123456789012", "region": "us-east-1", ... }

# Update agent
PATCH /agents/{agent_id}
Content-Type: application/json
{ "status": "DEPLOYED", "deployed_at": 1699564800 }
```

### 🔗 Event Sources

#### EventBridge Event Patterns
```python
# AWS Health
{
  "source": ["aws.health"],
  "detail-type": ["AWS Health Event"]
}

# GuardDuty
{
  "source": ["aws.guardduty"],
  "detail-type": ["GuardDuty Finding"]
}

# CloudWatch Alarms
{
  "source": ["aws.cloudwatch"],
  "detail-type": ["CloudWatch Alarm State Change"]
}

# CloudFormation
{
  "source": ["aws.cloudformation"],
  "detail-type": ["CloudFormation Stack Status Change"]
}

# Monitoring Agent (custom)
{
  "source": ["monitoring.agent.logs"],
  "detail-type": ["CloudWatch Logs Error"]
}
```

### 📝 Notification Templates

Available Jinja2 templates in `statics/templates/`:
- `cloudwatch_alarm.jinja` - CloudWatch alarm notifications
- `cloudwatch_log.jinja` - CloudWatch log error notifications
- `guardduty.jinja` - GuardDuty security findings
- `health.jinja` - AWS Health events
- `cfn_deployment.jinja` - CloudFormation stack status
- `daily_report.jinja` - Daily monitoring summary

**Context Variables** (common):
```python
{
    "emoji": ":warning:",
    "color": "#FF0000",
    "account": {"id": "123456789012", "name": "Production", "region": "us-east-1"},
    "time": "2024-11-17T12:00:00Z",
    ...
}
```

---

## Index Statistics

**Total Source Files**: 72 Python files
**Test Files**: 8 test files
**Domain Models**: 4 core models (Event, Agent, LogEntry, QueryResult)
**Use Cases**: 4 business workflows
**Repositories**: 2 data access implementations
**Lambda Functions**: 4 serverless handlers
**API Endpoints**: 7 REST endpoints
**AWS Services Integrated**: 5 (DynamoDB, EventBridge, CloudWatch, Lambda, ECS)
**Notification Templates**: 6 Jinja2 templates
**Test Coverage**: ~88%

---

## Next Steps for Exploration

### To Add New Features:
1. **New Event Type**: Start with domain model (`src/domain/models/`)
2. **New Use Case**: Add to `src/domain/use_cases/`
3. **New Lambda**: Create handler in `src/entrypoints/functions/`
4. **New API Endpoint**: Add to `src/entrypoints/apigw/`

### To Modify Existing:
1. **Data Model Change**: Update domain model → mapper → persistence model
2. **Business Logic**: Edit use case in `src/domain/use_cases/`
3. **AWS Integration**: Modify adapter in `src/adapters/aws/`
4. **Notification Format**: Edit Jinja2 template in `statics/templates/`

### To Debug Issues:
1. **Check Logs**: CloudWatch Logs or LocalStack container logs
2. **Inspect DynamoDB**: Use AWS CLI with LocalStack endpoint
3. **Run Tests**: `poetry run pytest tests/ -v`
4. **Coverage Analysis**: `poetry run pytest tests/ --cov=src --cov-report=html`

---

**Index Maintainer**: Claude Code
**Last Updated**: 2025-11-17
**For Updates**: Re-run `/index` command

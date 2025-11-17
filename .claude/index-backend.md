# Backend Architecture Index

**Project**: AWS Monitoring - Serverless Multi-Account Monitoring Solution
**Architecture**: Hexagonal (Ports & Adapters)
**Language**: Python 3.13
**Framework**: Serverless Framework 4.x
**Generated**: 2025-11-17

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Domain Layer](#domain-layer)
3. [Adapters Layer](#adapters-layer)
4. [Entrypoints Layer](#entrypoints-layer)
5. [Common Layer](#common-layer)
6. [Component Registry](#component-registry)
7. [Data Flow Patterns](#data-flow-patterns)
8. [Testing Structure](#testing-structure)

---

## Architecture Overview

The backend follows **hexagonal architecture** (ports and adapters pattern) with strict layer separation:

```
┌─────────────────────────────────────────────────┐
│             Entrypoints Layer                   │
│  (Lambda Handlers, API Gateway Endpoints)       │
└───────────────┬─────────────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────────────┐
│              Domain Layer                       │
│  ┌─────────────┐  ┌─────────┐  ┌────────────┐  │
│  │   Models    │  │  Ports  │  │ Use Cases  │  │
│  │  (Entities) │  │ (Ifaces)│  │ (Business) │  │
│  └─────────────┘  └─────────┘  └────────────┘  │
└───────────────┬─────────────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────────────┐
│             Adapters Layer                      │
│  (DB Repositories, AWS Services, Notifiers)     │
└─────────────────────────────────────────────────┘
```

**Key Principles:**
- Dependencies flow inward (entrypoints → domain → adapters implement domain ports)
- Domain layer has no external dependencies
- All external interactions go through ports (interfaces)
- Use cases orchestrate business logic
- Adapters implement technical details

---

## Domain Layer

### Location: `src/domain/`

The core business logic layer with zero external dependencies.

### Models (`src/domain/models/`)

Domain entities with business logic and validation using Pydantic v2.

#### Core Models

| Model | File | Description | Key Fields |
|-------|------|-------------|------------|
| `Event` | `event.py:9` | Monitoring event entity | id, account, region, source, detail, published_at |
| `Agent` | `agent.py:8` | Monitoring agent entity | account, region, status, deployed_at |
| `LogEntry` | `logs.py:10` | CloudWatch log entry | timestamp, message, log_stream, log_group |
| `LogQueryResult` | `logs.py:26` | Log query results container | status, results, statistics |
| `Message` | `messages.py:12` | Notification message | blocks, text, type |

#### DTOs (Data Transfer Objects)

| DTO | File | Purpose |
|-----|------|---------|
| `ListEventsDTO` | `event.py:26` | Pagination and filtering for events |
| `UpdateAgentDTO` | `agent.py:21` | Agent update parameters |
| `PaginatedInputDTO` | `base.py:8` | Base pagination input |
| `PaginatedOutputDTO` | `base.py:16` | Base pagination output |
| `QueryResult[T]` | `base.py:24` | Generic query result wrapper |

#### Type Aliases

```python
EventQueryResult = QueryResult[Event]      # event.py:38
AgentQueryResult = QueryResult[Agent]      # agent.py (imported)
```

### Ports (`src/domain/ports/`)

Interfaces defining contracts for external dependencies (dependency inversion).

#### Repository Ports

**File**: `repositories.py`

```python
class IAgentRepository(Protocol):          # Line 8
    def get(id: str) -> Agent
    def list() -> AgentQueryResult
    def create(entity: Agent) -> None
    def update(id: str, dto: UpdateAgentDTO) -> None
    def delete(id: str) -> None
    def exists(id: str) -> bool

class IEventRepository(Protocol):          # Line 22
    def get(id: str) -> Event
    def list(dto: ListEventsDTO) -> EventQueryResult
    def create(entity: Event) -> None
    def delete(id: str) -> None
```

#### Service Ports

| Interface | File | Methods | Purpose |
|-----------|------|---------|---------|
| `IPublisher` | `publisher.py:6` | `publish(entries)` | Publish events to EventBridge |
| `ILogService` | `logs.py:7` | `query(params) -> LogQueryResult` | Query CloudWatch Logs |
| `IEventNotifier` | `notifier.py:8` | `notify(event)` | Send event notifications |
| `IReportNotifier` | `notifier.py:12` | `notify(events)` | Send report notifications |

### Use Cases (`src/domain/use_cases/`)

Business logic orchestration. Each use case is a pure function.

#### Use Case: Insert Monitoring Event

**File**: `insert_monitoring_event.py`
**Function**: `insert_monitoring_event_use_case(event, event_repo, notifier)`

**Flow:**
1. Transform EventBridge event → Domain Event model
2. Save event via repository (event_repo.create)
3. Send notification via notifier (notifier.notify)

**Dependencies**: IEventRepository, IEventNotifier

#### Use Case: Query Error Logs

**File**: `query_error_logs.py`
**Function**: `query_error_logs_use_case(log_service, publisher, query_params)`

**Flow:**
1. Get list of Lambda functions
2. Query CloudWatch Logs for errors (in chunks of 10)
3. Transform log entries → Domain Event models
4. Publish events via EventBridge

**Dependencies**: ILogService, IPublisher

#### Use Case: Daily Report

**File**: `daily_report.py`
**Function**: `daily_report_use_case(event_repo, notifier, start_time, end_time)`

**Flow:**
1. Query events within time range
2. Generate report from events
3. Send report notification

**Dependencies**: IEventRepository, IReportNotifier

#### Use Case: Update Deployment

**File**: `update_deployment.py`
**Function**: `update_deployment_use_case(event, agent_repo)`

**Flow:**
1. Extract account from CloudFormation stack event
2. Update or create agent record
3. Update deployment status

**Dependencies**: IAgentRepository

---

## Adapters Layer

### Location: `src/adapters/`

Implementations of domain ports, connecting to external systems.

### Database Adapters (`src/adapters/db/`)

DynamoDB implementation using PynamoDB ORM.

#### Models (`models/`)

Database-specific entity representations (persistence models).

| Model | File | Discriminator | Attributes |
|-------|------|---------------|------------|
| `DynamoModel` | `base.py:40` | Base class | pk, sk, ttl |
| `EventPersistence` | `event.py:6` | "EVENT" | Extends DynamoModel with event fields |
| `AgentPersistence` | `agent.py:8` | "AGENT" | Extends DynamoModel with agent fields |

**Table Structure:**
- Single-table design
- Partition key (pk): Entity type (EVENT, AGENT)
- Sort key (sk): Entity identifier
- TTL: expired_at for automatic cleanup

#### Mappers (`mappers/`)

Convert between domain models and persistence models.

| Mapper | File | Methods |
|--------|------|---------|
| `EventMapper` | `event.py:8` | `to_model()`, `to_persistence()` |
| `AgentMapper` | `agent.py:5` | `to_model()`, `to_persistence()` |
| `Mapper[P, E]` | `base.py:8` | Protocol defining mapper interface |

**Pattern:**
```python
domain_model = Mapper.to_model(persistence_model)
persistence_model = Mapper.to_persistence(domain_model)
```

#### Repositories (`repositories/`)

Implement domain repository interfaces using DynamoDB.

| Repository | File | Inherits | Implements |
|------------|------|----------|------------|
| `DynamoRepository[M]` | `base.py:15` | Base class | CRUD operations |
| `EventRepository` | `event.py:8` | DynamoRepository | IEventRepository |
| `AgentRepository` | `agent.py:8` | DynamoRepository | IAgentRepository |

**Base Repository Methods:**
- `_get(hash_key, range_key)` - Get single item
- `_query(hash_key, conditions)` - Query with filters
- `_create(model)` - Create item
- `_update(hash_key, range_key, actions)` - Update item
- `_delete(hash_key, range_key)` - Delete item

**Access Patterns:**

*Events:*
- Get event: pk=EVENT, sk={published_at}-{id}
- List events: pk=EVENT, sk BETWEEN start_date AND end_date
- Sorted by published_at (descending)

*Agents:*
- Get agent: pk=AGENT, sk=AGENT#{account}
- List agents: pk=AGENT

### AWS Service Adapters (`src/adapters/aws/`)

Wrappers around AWS services using boto3.

| Service | File | Pattern | Key Methods |
|---------|------|---------|-------------|
| `CloudwatchLogService` | `cloudwatch.py:13` | Singleton | `query_logs(log_groups, query, duration)` |
| `EventBridgeService` | `eventbridge.py:14` | Singleton | `put_events(entries)` |
| `LambdaService` | `lambda_function.py:17` | Singleton | `get_all_functions()` |
| `ECSService` | `ecs.py:13` | Singleton | Service methods |

**Data Classes** (`data_classes.py`):
- `HealthEvent` (line 59): AWS Health events
- `GuardDutyFindingEvent` (line 96): GuardDuty findings
- `CwAlarmEvent` (line 103): CloudWatch alarms
- `CfnStackEvent` (line 145): CloudFormation events
- `CwLogEvent` (line 168): CloudWatch log events

### External Service Adapters

#### Publisher (`src/adapters/publisher.py`)

**Class**: `Publisher` (line 5)
**Implements**: IPublisher
**Purpose**: Publish events to EventBridge in batches

**Methods:**
- `publish(entries: list[LogEntry]) -> None`

#### Log Service (`src/adapters/logs.py`)

**Class**: `LogService` (line 12)
**Implements**: ILogService
**Purpose**: Query CloudWatch Logs Insights

**Methods:**
- `query(params: QueryParam) -> LogQueryResult`

#### Notifiers (`src/adapters/notifiers/`)

Notification implementations for different channels.

| Notifier | File | Implements | Purpose |
|----------|------|------------|---------|
| `SlackClient` | `base.py:15` | HTTP client | Send Slack webhooks |
| `EventNotifier` | `events.py:163` | IEventNotifier | Format and send event notifications |
| `ReportNotifier` | `report.py:10` | IReportNotifier | Format and send report notifications |

**Template System:**
- Uses Jinja2 templates from `statics/templates/`
- Templates: `event_notification.j2`, `daily_report.j2`

---

## Entrypoints Layer

### Location: `src/entrypoints/`

Application entry points - Lambda handlers and API endpoints.

### Lambda Functions (`src/entrypoints/functions/`)

Event-driven Lambda handlers.

#### HandleMonitoringEvents

**File**: `handle_monitoring_events/main.py`
**Handler**: `handler(event: EventBridgeEvent, context)`
**Trigger**: EventBridge events from agent accounts
**Use Case**: `insert_monitoring_event_use_case`

**Flow:**
1. Receive EventBridge event
2. Insert event into DynamoDB
3. Send Slack notification

**Dependencies:**
- EventRepository
- EventNotifier (Slack)

#### QueryErrorLogs

**File**: `query_error_logs/main.py`
**Handler**: `handler(event, context)`
**Trigger**: Scheduled EventBridge rule (every 5 minutes)
**Use Case**: `query_error_logs_use_case`

**Flow:**
1. List all Lambda functions
2. Query CloudWatch Logs for errors
3. Publish events to master EventBridge

**Dependencies:**
- LogService (CloudWatch)
- Publisher (EventBridge)
- LambdaService

#### DailyReport

**File**: `daily_report/main.py`
**Handler**: `handler(event, context)`
**Trigger**: Scheduled EventBridge rule (daily)
**Use Case**: `daily_report_use_case`

**Flow:**
1. Calculate time range (last 24 hours)
2. Query events from DynamoDB
3. Generate and send report

**Dependencies:**
- EventRepository
- ReportNotifier (Slack)

#### UpdateDeployment

**File**: `update_deployment/main.py`
**Handler**: `handler(event: CfnStackEvent, context)`
**Trigger**: CloudFormation stack events
**Use Case**: `update_deployment_use_case`

**Flow:**
1. Receive CFN stack event
2. Update agent deployment status
3. Log deployment changes

**Dependencies:**
- AgentRepository

### API Gateway Endpoints (`src/entrypoints/apigw/`)

REST API using AWS Lambda Powertools.

#### Events API

**File**: `events/main.py`
**Base Path**: `/events`

**Endpoints:**

| Method | Path | Handler | Purpose |
|--------|------|---------|---------|
| GET | `/events/<event_id>` | `get_event()` (line 20) | Get single event |
| GET | `/events` | `list_events()` (line 26) | List events with pagination |

**Query Parameters (list_events):**
- `start_date`: Filter by start timestamp
- `end_date`: Filter by end timestamp
- `limit`: Items per page (default: 50)
- `direction`: Sort order (asc/desc, default: desc)
- `cursor`: Pagination cursor (base64 encoded)

**Response Format:**
```json
{
  "items": [Event],
  "limit": 50,
  "next": "base64_cursor",
  "previous": "base64_cursor"
}
```

#### Agents API

**File**: `agents/main.py`
**Base Path**: `/agents`

**Endpoints:**

| Method | Path | Handler | Purpose |
|--------|------|---------|---------|
| GET | `/agents/<agent_id>` | `get_agent()` | Get single agent |
| GET | `/agents` | `list_agents()` | List all agents |
| POST | `/agents` | `create_agent()` | Create new agent |
| PATCH | `/agents/<agent_id>` | `update_agent()` | Update agent |
| DELETE | `/agents/<agent_id>` | `delete_agent()` | Delete agent |

#### Base Configuration

**File**: `base.py`
**Function**: `create_app(cors_allow_origin, cors_max_age)`

Creates API Gateway application with:
- CORS configuration
- OpenAPI documentation
- Error handling
- Request/response validation

**File**: `configs.py`
Constants:
- `CORS_ALLOW_ORIGIN`: Allowed origins
- `CORS_MAX_AGE`: CORS cache duration

---

## Common Layer

### Location: `src/common/`

Shared utilities and cross-cutting concerns.

### Core Components

| Component | File | Purpose |
|-----------|------|---------|
| `logger` | `logger.py` | Structured logging configuration |
| `exceptions` | `exceptions.py` | Custom exception hierarchy |
| `constants` | `constants.py` | Environment variables and config |
| `enums` | `enums.py` | Enumeration types |
| `models` | `models.py` | Generic models (Page, etc.) |
| `meta` | `meta.py` | Metaclasses (Singleton) |

### Utilities (`src/common/utils/`)

| Utility | File | Functions |
|---------|------|-----------|
| Date/Time | `datetime_utils.py` | `current_utc_timestamp()`, `datetime_str_to_timestamp()` |
| Encoding | `encoding.py` | `json_to_base64()`, `base64_to_json()` |
| Objects | `objects.py` | `chunks(list, size)` - Split list into chunks |
| Templates | `template.py` | `render_template(name, context)` - Jinja2 rendering |

### Enumerations

| Enum | File | Values |
|------|------|--------|
| `AlarmState` | `enums.py:11` | OK, ALARM, INSUFFICIENT_DATA |
| `HealthEventCategory` | `enums.py:35` | issue, accountNotification, scheduledChange |
| `SeverityLevel` | `enums.py:67` | UNKNOWN(0), LOW(1), MEDIUM(2), HIGH(3), CRITICAL(4) |
| `CfnStackStatusType` | `enums.py:101` | Stack creation/update/delete statuses |
| `EventSource` | `enums.py:125` | aws.cloudwatch, aws.health, aws.guardduty, etc. |

### Exception Hierarchy

```
Exception
└── ServiceError                    # Base service exception
    ├── UnprocessedError           # Failed to process
    ├── ConflictError              # Resource conflict
    └── InternalServerError        # Internal errors
        └── AWSClientException     # AWS SDK errors
```

---

## Component Registry

### Domain Models

| Component | Type | Location | Lines |
|-----------|------|----------|-------|
| Event | Model | domain/models/event.py | 9-23 |
| Agent | Model | domain/models/agent.py | 8-19 |
| LogEntry | Model | domain/models/logs.py | 10-24 |
| LogQueryResult | Model | domain/models/logs.py | 26-38 |
| Message | Model | domain/models/messages.py | 12-26 |

### Use Cases

| Use Case | Location | Dependencies |
|----------|----------|--------------|
| insert_monitoring_event | use_cases/insert_monitoring_event.py | IEventRepository, IEventNotifier |
| query_error_logs | use_cases/query_error_logs.py | ILogService, IPublisher |
| daily_report | use_cases/daily_report.py | IEventRepository, IReportNotifier |
| update_deployment | use_cases/update_deployment.py | IAgentRepository |

### Repositories

| Repository | Location | Implements |
|------------|----------|------------|
| EventRepository | adapters/db/repositories/event.py | IEventRepository |
| AgentRepository | adapters/db/repositories/agent.py | IAgentRepository |

### AWS Services

| Service | Location | Purpose |
|---------|----------|---------|
| CloudwatchLogService | adapters/aws/cloudwatch.py | Query CloudWatch Logs |
| EventBridgeService | adapters/aws/eventbridge.py | Publish events |
| LambdaService | adapters/aws/lambda_function.py | List Lambda functions |
| ECSService | adapters/aws/ecs.py | ECS operations |

### Lambda Handlers

| Handler | Location | Trigger |
|---------|----------|---------|
| HandleMonitoringEvents | functions/handle_monitoring_events/main.py | EventBridge |
| QueryErrorLogs | functions/query_error_logs/main.py | Scheduled |
| DailyReport | functions/daily_report/main.py | Scheduled |
| UpdateDeployment | functions/update_deployment/main.py | CloudFormation |

### API Endpoints

| Endpoint | Location | Methods |
|----------|----------|---------|
| /events | apigw/events/main.py | GET |
| /events/{id} | apigw/events/main.py | GET |
| /agents | apigw/agents/main.py | GET, POST |
| /agents/{id} | apigw/agents/main.py | GET, PATCH, DELETE |

---

## Data Flow Patterns

### Event Ingestion Flow

```
Agent Account                Master Account
┌─────────────┐             ┌──────────────────┐
│ QueryError  │             │ HandleMonitoring │
│ Logs Lambda │────────────▶│ Events Lambda    │
└─────────────┘             └──────────────────┘
      │ Scheduled                    │
      ↓                              ↓
┌─────────────┐             ┌──────────────────┐
│ CloudWatch  │             │ EventRepository  │
│ Logs        │             │ (DynamoDB)       │
└─────────────┘             └──────────────────┘
                                     │
                                     ↓
                            ┌──────────────────┐
                            │ EventNotifier    │
                            │ (Slack)          │
                            └──────────────────┘
```

### API Request Flow

```
Client Request
      │
      ↓
┌─────────────┐
│ API Gateway │
└─────────────┘
      │
      ↓
┌─────────────────┐
│ Lambda Handler  │
│ (events/main.py)│
└─────────────────┘
      │
      ↓
┌─────────────────┐
│ EventRepository │
└─────────────────┘
      │
      ↓
┌─────────────────┐
│ DynamoDB Table  │
└─────────────────┘
      │
      ↓
JSON Response
```

### Daily Report Flow

```
EventBridge Schedule
      │
      ↓
┌─────────────────┐
│ DailyReport     │
│ Lambda          │
└─────────────────┘
      │
      ├─────────────────────┐
      │                     │
      ↓                     ↓
┌──────────────┐    ┌──────────────┐
│ EventRepo    │    │ ReportNotifier│
│ (Query 24h)  │    │ (Format)      │
└──────────────┘    └──────────────┘
      │                     │
      └─────────┬───────────┘
                ↓
        ┌──────────────┐
        │ Slack Webhook│
        └──────────────┘
```

---

## Testing Structure

### Test Organization

```
tests/
├── conftest.py               # Pytest fixtures
├── data/                     # Test data
├── mock.py                   # Mock objects
├── adapters/                 # Adapter tests
│   ├── aws/                  # AWS service tests
│   ├── db/                   # Database tests
│   └── notifiers/            # Notifier tests
├── domain/                   # Domain tests
│   ├── models/               # Model tests
│   └── use_cases/            # Use case tests
├── entrypoints/              # Entrypoint tests
│   ├── functions/            # Lambda function tests
│   └── apigw/                # API tests
└── integrations/             # Integration tests
    ├── api/                  # API integration tests
    └── db/                   # DB integration tests
```

### Test Patterns

**Unit Tests:**
- Mock external dependencies
- Test business logic in isolation
- Use pytest fixtures for test data

**Integration Tests:**
- Use moto for AWS mocking
- Test component interactions
- Verify data flow between layers

**Coverage Expectations:**
- Overall: >90%
- Domain layer: 100% (critical business logic)
- Adapters: >85%
- Entrypoints: >80%

---

## File Count Summary

| Layer | Directory | Files | Purpose |
|-------|-----------|-------|---------|
| **Domain** | src/domain/ | 17 | Business logic |
| - Models | models/ | 5 | Domain entities |
| - Ports | ports/ | 4 | Interface contracts |
| - Use Cases | use_cases/ | 5 | Business workflows |
| **Adapters** | src/adapters/ | 26 | External integrations |
| - Database | db/ | 13 | DynamoDB |
| - AWS | aws/ | 6 | AWS services |
| - Notifiers | notifiers/ | 4 | Notifications |
| **Entrypoints** | src/entrypoints/ | 13 | Application entry |
| - Functions | functions/ | 8 | Lambda handlers |
| - API Gateway | apigw/ | 6 | REST endpoints |
| **Common** | src/common/ | 9 | Shared utilities |
| **Total** | src/ | 65 | Python modules |

---

## Quick Reference

### Adding New Event Type
1. Domain model: `src/domain/models/`
2. DB model: `src/adapters/db/models/`
3. Mapper: `src/adapters/db/mappers/`
4. Update repository: `src/adapters/db/repositories/`
5. Use case: `src/domain/use_cases/`
6. Entrypoint: `src/entrypoints/functions/`

### Adding New API Endpoint
1. Define route in `src/entrypoints/apigw/`
2. Use repository for data access
3. Return Pydantic model or dict
4. Add OpenAPI annotations

### Adding New Notifier
1. Implement `INotifier` in `src/adapters/notifiers/`
2. Create Jinja2 template in `statics/templates/`
3. Update use case to inject notifier

### Key Design Patterns
- **Repository Pattern**: Data access abstraction
- **Dependency Injection**: Loose coupling via constructors
- **Mapper Pattern**: Domain ↔ Persistence transformation
- **Use Case Pattern**: Business logic orchestration
- **Singleton Pattern**: AWS service clients
- **Protocol Pattern**: Interface definitions (Python Protocol)

---

**Index Version**: 1.0.0
**Last Updated**: 2025-11-17
**Total Components Indexed**: 65 Python modules, 70+ classes

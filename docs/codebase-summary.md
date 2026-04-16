# Codebase Summary

## 📁 Layer Structure Overview

The AWS Monitoring codebase follows a **hexagonal architecture (ports and adapters pattern)** with clean separation of concerns across multiple layers. This architecture ensures maintainability, testability, and scalability by separating business logic from external dependencies.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Entry Points Layer                         │
│  • Lambda Function Handlers                                │
│  • API Gateway Handlers                                     │
│  • Input Validation & Response Formatting                    │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                              │
│  • Business Logic & Use Cases                               │
│  • Domain Models & Entities                                 │
│  • Port Interfaces (Contracts)                             │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Adapters Layer                            │
│  • External Service Integrations                            │
│  • Database Repositories                                    │
│  • AWS Service Adapters                                     │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Common Layer                              │
│  • Shared Utilities & Configuration                         │
│  • Cross-Cutting Concerns                                   │
│  • Exception Handling                                       │
└─────────────────────────────────────────────────────────────┘
```

## 🏛️ Domain Layer (`src/domain/`)

The **Domain Layer** contains the core business logic and entities of the system. It has no external dependencies and defines the contracts through port interfaces.

### Models (`src/domain/models/`)

#### Event Model
- **Purpose**: Core business entity representing monitoring events
- **Validation**: Pydantic-based with strict type validation
- **Logic**: Domain validation rules and business methods
- **File**: `src/domain/models/event.py`

#### Agent Model
- **Purpose**: Represents monitoring agents deployed in AWS accounts
- **Validation**: Pydantic-based with account validation
- **Logic**: Agent status management and lifecycle methods
- **File**: `src/domain/models/agent.py`

#### Base Model
- **Purpose**: Common base class for all domain entities
- **Features**: Common attributes like ID, timestamps, versioning
- **File**: `src/domain/models/base.py`

### Ports (`src/domain/ports/`)

Port interfaces define contracts for external dependencies, enabling dependency inversion and testability.

#### Repository Ports
- `IAgentRepository`: Agent data persistence contract
- `IEventRepository`: Event data persistence contract
- **Features**: CRUD operations, querying, pagination
- **Files**: `src/domain/ports/repositories.py`

#### Service Ports
- `IEventNotifier`: Event notification contract
- `IReportNotifier`: Report notification contract
- `IPublisher`: Event publishing contract
- `ILogService`: Log querying service contract
- **Files**: `src/domain/ports/notifier.py`, `src/domain/ports/publisher.py`

### Use Cases (`src/domain/use_cases/`)

Use cases orchestrate business operations and contain the core application logic.

#### Daily Report Use Case
- **Purpose**: Generate and send daily monitoring reports
- **Dependencies**: Repository, Notifier, Publisher
- **Logic**: Event aggregation, report generation, notification dispatch
- **File**: `src/domain/use_cases/daily_report.py`

#### Event Processing Use Case
- **Purpose**: Process incoming monitoring events
- **Logic**: Event validation, enrichment, storage, notification
- **File**: `src/domain/use_cases/insert_monitoring_event.py`

#### Error Log Query Use Case
- **Purpose**: Query CloudWatch logs for errors and publish events
- **Logic**: Query execution, event transformation, publishing
- **File**: `src/domain/use_cases/query_error_logs.py`

#### Deployment Update Use Case
- **Purpose**: Track and update agent deployment status
- **Logic**: Status validation, tracking, updates
- **File**: `src/domain/use_cases/update_deployment.py`

## 🔌 Adapters Layer (`src/adapters/`)

The **Adapters Layer** implements the domain port interfaces and handles external service integrations.

### Database Adapters (`src/adapters/db/`)

#### Database Models (`src/adapters/db/models/`)
- **Agent Model**: DynamoDB-specific agent representation
- **Event Model**: DynamoDB-specific event representation
- **Base Model**: Common database attributes and methods
- **Features**: Type annotations, validation, serialization

#### Mappers (`src/adapters/db/mappers/`)
- **Purpose**: Convert between domain and database models
- **AgentMapper**: Domain ↔ Database agent conversion
- **EventMapper**: Domain ↔ Database event conversion
- **BaseMapper**: Common conversion utilities
- **Features**: Bidirectional conversion, validation, error handling

#### Repositories (`src/adapters/db/repositories/`)
- **AgentRepository**: Implements `IAgentRepository` for DynamoDB
- **EventRepository**: Implements `IEventRepository` for DynamoDB
- **BaseRepository**: Common repository functionality
- **Features**: CRUD operations, query optimization, pagination, error handling

### AWS Service Adapters (`src/adapters/aws/`)

#### CloudWatch Adapter (`src/adapters/aws/cloudwatch.py`)
- **Purpose**: CloudWatch Logs Insights query integration
- **Features**: Query execution, result parsing, error handling
- **Integration**: Event-driven log analysis for error detection

#### EventBridge Adapter (`src/adapters/aws/eventbridge.py`)
- **Purpose**: Event publishing to AWS EventBridge
- **Features**: Event publishing, retry logic, error handling
- **Integration**: Cross-account event communication

#### Lambda Function Adapter (`src/adapters/aws/lambda_function.py`)
- **Purpose**: AWS Lambda function invocation utilities
- **Features**: Synchronous/asynchronous invocation, error handling

#### ECS Adapter (`src/adapters/aws/ecs.py`)
- **Purpose**: ECS service monitoring and task management
- **Features**: Task discovery, health checks, monitoring

#### Data Classes (`src/adapters/aws/data_classes.py`)
- **Purpose**: Common data structures for AWS service interactions
- **Features**: Typed data classes, serialization, validation

### Notification Adapters (`src/adapters/notifiers/`)

#### Base Notifier (`src/adapters/notifiers/base.py`)
- **Purpose**: Base class for all notification services
- **Features**: Template rendering, delivery tracking, error handling

#### Event Notifier (`src/adapters/notifiers/events.py`)
- **Purpose**: Real-time event notifications
- **Integration**: Slack webhook integration
- **Features**: Formatting, delivery confirmation, retries

#### Report Notifier (`src/adapters/notifiers/report.py`)
- **Purpose**: Daily report generation and delivery
- **Features**: Report generation, template rendering, multiple channels

### External Service Adapters

#### Log Adapter (`src/adapters/logs.py`)
- **Purpose**: Cross-service log querying implementation
- **Integration**: CloudWatch Logs Insights query adapter
- **Features**: Query execution, pagination, error handling

#### Publisher Adapter (`src/adapters/publisher.py`)
- **Purpose**: Event publishing implementation
- **Integration**: EventBridge cross-account publishing
- **Features**: Event formatting, retry logic, delivery confirmation

## 🚪 Entry Points Layer (`src/entrypoints/`)

The **Entry Points Layer** serves as the application interface, handling input validation and response formatting while delegating business logic to domain use cases.

### Lambda Function Handlers (`src/entrypoints/functions/`)

#### Handle Monitoring Events (`src/entrypoints/functions/handle_monitoring_events/main.py`)
- **Purpose**: Process incoming monitoring events
- **Logic**: Input validation, use case delegation, response formatting
- **Integration**: EventBridge trigger, API Gateway, error handling

#### Daily Report (`src/entrypoints/functions/daily_report/main.py`)
- **Purpose**: Generate and send daily monitoring reports
- **Logic**: Scheduling, report generation, notification dispatch
- **Integration**: EventBridge scheduled trigger, error handling

#### Query Error Logs (`src/entrypoints/functions/query_error_logs/main.py`)
- **Purpose**: Query CloudWatch logs for errors
- **Logic**: Query configuration, execution, event publishing
- **Integration**: EventBridge scheduled trigger, CloudWatch integration

#### Update Deployment (`src/entrypoints/functions/update_deployment/main.py`)
- **Purpose**: Track agent deployment status
- **Logic**: Status validation, tracking, updates
- **Integration**: EventBridge trigger, agent management

### API Gateway Handlers (`src/entrypoints/apigw/`)

#### Base Handler (`src/entrypoints/apigw/base.py`)
- **Purpose**: Common API Gateway functionality
- **Features**: Input validation, response formatting, error handling
- **Integration**: CORS, authentication, logging

#### Agent Management API (`src/entrypoints/apigw/agents/main.py`)
- **Purpose**: REST API for agent management
- **Endpoints**: GET /agents, POST /agents, PUT /agents/{account}
- **Features**: Pagination, filtering, validation, error handling

#### Events API (`src/entrypoints/apigw/events/main.py`)
- **Purpose**: REST API for event querying
- **Endpoints**: GET /events, GET /events/{id}
- **Features**: Filtering, pagination, time range queries, aggregation

## 📦 Common Layer (`src/common/`)

The **Common Layer** provides shared utilities, configuration, and cross-cutting concerns used across all other layers.

### Configuration (`src/common/`)
- **Constants**: Application-wide constants and configuration
- **Environment Variables**: Runtime configuration management
- **Features**: Validation, defaults, type safety

### Exceptions (`src/common/exceptions.py`)
- **Purpose**: Custom exception hierarchy
- **Types**: `UnprocessedError`, `ConflictError`, `AWSClientException`
- **Features**: Error codes, message formatting, context preservation

### Logger (`src/common/logger.py`)
- **Purpose**: Structured logging configuration
- **Features**: JSON formatting, correlation IDs, log levels
- **Integration**: AWS Lambda Powertools for structured logging

### Models (`src/common/models.py`)
- **Purpose**: Common data structures
- **Features**: Response models, error models, pagination models
- **Integration**: Pydantic for validation and serialization

### Utilities (`src/common/utils/`)

#### DateTime Utils (`src/common/utils/datetime_utils.py`)
- **Purpose**: Date and time manipulation utilities
- **Features**: Timestamp conversion, time range calculations, formatting
- **Usage**: Event timestamp handling, reporting, queries

#### Encoding Utils (`src/common/utils/encoding.py`)
- **Purpose**: Data encoding and serialization utilities
- **Features**: JSON handling, base64 encoding, compression
- **Usage**: Event data processing, API responses

#### Objects Utils (`src/common/utils/objects.py`)
- **Purpose**: Object manipulation utilities
- **Features**: Chunking, filtering, transformation
- **Usage**: Data processing, API responses

#### Template Utils (`src/common/utils/template.py`)
- **Purpose**: Template rendering utilities
- **Features**: Jinja2 template engine, variable substitution
- **Usage**: Report generation, notification formatting

## 🧩 Module Responsibilities

### Domain Layer Responsibilities
- **Business Logic**: Core business rules and validation
- **Entity Management**: Domain model creation and validation
- **Use Case Orchestration**: Business operation coordination
- **Interface Definition**: Port contracts for external dependencies

### Adapters Layer Responsibilities
- **External Integration**: AWS services, databases, APIs
- **Data Transformation**: Domain ↔ External format conversion
- **Service Implementation**: Port interface implementations
- **Error Handling**: External service error management

### Entry Points Layer Responsibilities
- **Input Validation**: Request parameter validation
- **Response Formatting**: API response structure and formatting
- **Error Handling**: API-level error management
- **Security**: Authentication, authorization, input sanitization

### Common Layer Responsibilities
- **Shared Utilities**: Reusable code components
- **Configuration Management**: Centralized configuration
- **Exception Handling**: Cross-cutting error management
- **Logging**: Structured logging and observability

## 🏗️ Code Organization Principles

### Dependency Flow
```
Entry Points → Domain (Use Cases) → Domain (Ports) ← Adapters
     ↓              ↓                    ↓              ↑
   Common      Domain (Models)      Common        Common
```

### Key Principles
1. **Dependency Inversion**: Dependencies flow inward toward domain layer
2. **Single Responsibility**: Each component has a single, clear purpose
3. **Open/Closed**: Components are open for extension, closed for modification
4. **Interface Segregation**: Clients should not depend on interfaces they don't use
5. **Liskov Substitution**: Subtypes must be substitutable for their base types

### Testing Strategy
- **Unit Tests**: Domain logic and business rules
- **Integration Tests**: Adapter implementations and external service integration
- **End-to-End Tests**: Complete workflows and API endpoints
- **Mocking**: External dependencies mocked for isolated testing

### Code Quality Standards
- **Type Safety**: Full type annotations throughout the codebase
- **Error Handling**: Comprehensive exception handling and recovery
- **Performance**: Optimized database queries and efficient data processing
- **Security**: Input validation, sanitization, and secure coding practices

This hexagonal architecture provides a solid foundation for maintainable, scalable, and testable code while enabling easy extension of the system with new features and integrations.
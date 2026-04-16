# AWS Monitoring System - Adapters Layer Documentation
**Date:** 2026-04-16
**Report ID:** Explore-260416-1706-adapters-layer

## Executive Summary

This document provides a comprehensive analysis of the AWS monitoring system's adapters layer, which implements the dependency inversion principle by providing concrete implementations of domain ports. The adapters layer bridges the gap between domain logic and external systems including AWS services, databases, and external notifications.

## 1. Architecture Overview

The adapters layer follows clean architecture principles with clear separation of concerns:

```
Domain Layer (Ports) ← Adapters Layer (Implementations) ← External Systems
```

### Key Architectural Patterns:
- **Dependency Inversion**: Domain layer defines interfaces (ports), adapters implement them
- **Mapper Pattern**: Separate mapping between domain models and persistence models
- **Repository Pattern**: Abstract data access through repository interfaces
- **Adapter Pattern**: Wrap external service calls with domain-friendly interfaces

## 2. AWS Service Adapters

### 2.1 CloudWatch Logs Adapter (`src/adapters/aws/cloudwatch.py`)

**Purpose**: Provides CloudWatch Logs service integration with retry logic and timeout handling.

**Key Class**: `CloudwatchLogService`
- **Pattern**: Singleton using `SingletonMeta`
- **Client**: `CloudWatchLogsClient` from boto3
- **Methods**:
  - `query_logs()`: Executes log queries with configurable timeout and delay
  - **Features**: Automatic query polling, timeout handling, result aggregation

**Integration**: Used by `LogService` for executing CloudWatch log queries.

### 2.2 EventBridge Adapter (`src/adapters/aws/eventbridge.py`)

**Purpose**: Handles event publishing to AWS EventBridge.

**Key Class**: `EventBridgeService`
- **Pattern**: Singleton using `SingletonMeta`
- **Client**: `EventBridgeClient` from boto3
- **Methods**:
  - `put_events()`: Publishes events to EventBus with error handling
  - **Features**: Response validation, failure detection, logging

**Integration**: Used by `Publisher` adapter for event publishing.

### 2.3 ECS Adapter (`src/adapters/aws/ecs.py`)

**Purpose**: Manages ECS cluster operations with pagination and tag filtering.

**Key Class**: `ECSService`
- **Pattern**: Singleton using `SingletonMeta`
- **Client**: `ECSClient` from boto3
- **Methods**:
  - `list_clusters()`: Lists all ECS clusters with tags and configurations
  - **Features**: Pagination, tag-based filtering, error handling

**Integration**: Used by `LogService` to discover ECS clusters by tags.

### 2.4 Lambda Adapter (`src/adapters/aws/lambda_function.py`)

**Purpose**: Handles Lambda function operations with tag-based discovery.

**Key Class**: `LambdaService`
- **Pattern**: Singleton using `SingletonMeta`
- **Client**: `LambdaClient` from boto3
- **Methods**:
  - `list_functions()`: Lists Lambda functions with tags
  - **Features**: Pagination, automatic tag fetching, custom model mapping

**Integration**: Used by `LogService` to discover Lambda functions by tags.

### 2.5 Data Classes (`src/adapters/aws/data_classes.py`)

**Purpose**: Provides strongly-typed event wrappers for various AWS event types.

**Key Classes**:
- `HealthEvent`: AWS Health event wrapper
- `GuardDutyFindingEvent`: GuardDuty finding event wrapper
- `CwAlarmEvent`: CloudWatch alarm event wrapper
- `CfnStackEvent`: CloudFormation stack event wrapper
- `CwLogEvent`: CloudWatch log event wrapper

**Features**:
- Uses `DictWrapper` for safe property access
- Property-based data extraction
- Enum values for CloudFormation status

## 3. Database Adapters

### 3.1 Database Models (`src/adapters/db/models/`)

#### Base Model (`src/adapters/db/models/base.py`)
- `DynamoModel`: Base class for all DynamoDB models
- `DynamoMeta`: Configuration for table name, host, region
- `KeyAttribute`: Custom attribute with prefix support for composite keys

#### Agent Model (`src/adapters/db/models/agent.py`)
- `AgentPersistence`: DynamoDB model for agent data
- **Keys**: `pk="AGENT"`, `sk={AWS AccountID}`
- **Attributes**: region, status, deployed_at, created_at

#### Event Model (`src/adapters/db/models/event.py`)
- `EventPersistence`: DynamoDB model for event data
- **Keys**: `pk="EVENT"`, `sk={AWS EventTime}-{AWS EventID}`
- **Attributes**: account, region, source, detail (JSON), detail_type, resources, TTL

### 3.2 Mappers (`src/adapters/db/mappers/`)

#### Base Mapper (`src/adapters/db/mappers/base.py`)
- `Mapper[P, E]`: Protocol defining mapping interface
- Methods: `to_persistence()`, `to_entity()`

#### Agent Mapper (`src/adapters/db/mappers/agent.py`)
- `AgentMapper`: Bidirectional mapping between `Agent` and `AgentPersistence`
- **Mapping**: Simple field-to-field mapping with key handling

#### Event Mapper (`src/adapters/db/mappers/event.py`)
- `EventMapper`: Bidirectional mapping with JSON serialization
- **Special Handling**:
  - JSON serialization for `detail` field
  - TTL expiration calculation
  - ID extraction from composite key

### 3.3 Repositories (`src/adapters/db/repositories/`)

#### Base Repository (`src/adapters/db/repositories/base.py`)
- `DynamoRepository[T]`: Generic base repository with CRUD operations
- `QueryResult[T]`: Paginated result wrapper
- **Features**:
  - Generic CRUD operations (`_get`, `_query`, `_create`, `_update`, `_delete`)
  - Error handling with custom exceptions
  - Pagination support
  - Conditional operations

#### Agent Repository (`src/adapters/db/repositories/agent.py`)
- `AgentRepository`: Implements `IAgentRepository` port
- **Methods**: `get()`, `list()`, `create()`, `update()`, `delete()`, `exists()`
- **Features**: Simple key-based operations, partial updates via DTO

#### Event Repository (`src/adapters/db/repositories/event.py`)
- `EventRepository`: Implements `IEventRepository` port
- **Features**:
  - Date-based range queries
  - Pagination with cursor
  - Direction-based sorting
  - Complex key condition handling

## 4. Notifier Adapters

### 4.1 Base Notifier (`src/adapters/notifiers/base.py`)

**Purpose**: Provides base infrastructure for notification services.

**Key Classes**:
- `Message`: Notification message model with body and attachments
- `SlackClient`: HTTP client for Slack webhook integration
- `render_message()`: Template rendering utility

**Features**:
- JSON template rendering with context
- HTTP client with error handling
- Message formatting utilities

### 4.2 Event Notifier (`src/adapters/notifiers/events.py`)

**Purpose**: Handles event notifications via Slack with event-specific formatting.

**Key Classes**:
- `EventNotifier`: Implements `IEventNotifier` port
- Event-specific message converters (`cw_alarm_event_to_message`, etc.)

**Event Types Supported**:
- AWS Health events (`health_event_to_message`)
- GuardDuty findings (`guardduty_event_to_message`)
- CloudWatch alarms (`cw_alarm_event_to_message`)
- CloudFormation events (`cfn_event_to_message`)
- CloudWatch logs (`cw_log_event_to_message`)

**Features**:
- Event source-based message routing
- Severity-based color coding
- Rich formatting with emojis and colors
- Account metadata integration

### 4.3 Report Notifier (`src/adapters/notifiers/report.py`)

**Purpose**: Generates and sends daily monitoring reports.

**Key Classes**:
- `ReportNotifier`: Implements `IReportNotifier` port

**Features**:
- Event categorization by account and type
- Statistical aggregation
- Template-based report generation
- Time period reporting

## 5. Log Query Adapter (`src/adapters/logs.py`)

**Purpose**: Provides comprehensive log querying capabilities across multiple AWS services.

**Key Classes**:
- `LogService`: Implements `ILogService` port
- `CwQueryResult`: Log query result structure
- `CwLog`: Individual log entry model

**Features**:
- Multi-service log discovery (Lambda, ECS)
- Tag-based log group filtering
- Chunk-based querying for performance
- Result categorization and aggregation

**Discovery Logic**:
- Lambda functions: Filter by tags, extract log groups from logging config
- ECS clusters: Filter by tags, extract log groups from execute command config

## 6. Event Publisher Adapter (`src/adapters/publisher.py`)

**Purpose**: Provides event publishing capabilities to EventBridge.

**Key Classes**:
- `Message`: Event message model
- `Publisher`: Implements `IPublisher` port

**Features**:
- Message validation and serialization
- Batch event publishing
- Automatic timestamp handling
- EventBridge integration

## 7. Domain Ports Implementation

### 7.1 Repository Ports (`src/domain/ports/repositories.py`)
- `IAgentRepository`: Agent CRUD operations
- `IEventRepository`: Event query and persistence operations

### 7.2 Notifier Ports (`src/domain/ports/notifier.py`)
- `IEventNotifier`: Event notification interface
- `IReportNotifier`: Report notification interface

### 7.3 Service Ports (`src/domain/ports/`)
- `ILogService`: Log query interface
- `IPublisher`: Event publishing interface

## 8. External Service Integration

### 8.1 AWS Services
- **CloudWatch Logs**: Log querying and monitoring
- **EventBridge**: Event publishing and receiving
- **ECS**: Container service discovery
- **Lambda**: Serverless function discovery
- **DynamoDB**: Data persistence

### 8.2 External Notifications
- **Slack**: Real-time event notifications and reports
- **Webhook Integration**: Configurable via environment variables

### 8.3 Template System
- **Jinja2 Templates**: Dynamic message formatting
- **Context-based Rendering**: Account metadata and event-specific data
- **Template Files**: Separate templates for different event types

## 9. Key Design Patterns

### 9.1 Dependency Inversion Principle
- Domain layer defines interfaces (ports)
- Adapters provide concrete implementations
- Decouples domain logic from infrastructure

### 9.2 Repository Pattern
- Abstract data access through repository interfaces
- Handles pagination, error handling, and data mapping
- Consistent CRUD operations across different entities

### 9.3 Adapter Pattern
- Wraps external service calls with domain-friendly interfaces
- Normalizes different service responses
- Provides consistent error handling

### 9.4 Mapper Pattern
- Clear separation between domain and persistence models
- Bidirectional mapping with validation
- Handles serialization/deserialization concerns

## 10. Configuration and Environment

### 10.1 Environment Variables
- `AWS_REGION`: AWS region for service clients
- `AWS_ENDPOINT`: Local endpoint for testing (LocalStack)
- `AWS_DYNAMODB_TABLE`: DynamoDB table name
- `AWS_DYNAMODB_TTL`: Event expiration time in seconds
- Various webhook URLs for different notification types

### 10.2 Metadata System
- Account metadata mapping for human-readable names
- Template context integration
- Configurable via environment or database

## 11. Error Handling

### 11.1 Custom Exceptions
- `NotFoundError`: Resource not found in database
- `ConflictError`: Data conflict during operations
- `InternalServerError`: Generic service errors
- `UnprocessedError`: AWS service unprocessed items

### 11.2 Error Propagation
- Consistent error handling across adapters
- Meaningful error messages with context
- Proper exception wrapping and logging

## 12. Testing Strategy

### 12.1 Unit Testing
- Repository methods with mocked DynamoDB
- Mapper validation
- Service client mocking

### 12.2 Integration Testing
- End-to-end event processing
- Template rendering validation
- Webhook integration testing

## 13. Performance Considerations

### 13.1 Pagination
- Built-in pagination for large result sets
- Cursor-based pagination for efficient data access
- Configurable page sizes

### 13.2 Caching
- No explicit caching in current implementation
- Consider adding for frequently accessed metadata

### 13.3 Chunking
- Log query chunking for performance
- Batch event publishing
- Processing large datasets in manageable chunks

## 14. Future Enhancements

### 14.1 Additional AWS Services
- S3 monitoring integration
- RDS database monitoring
- Network service monitoring

### 14.2 Notification Channels
- Email notifications
- SMS notifications
- Multiple Slack channels

### 14.3 Data Enrichment
- Additional metadata integration
- Event correlation
- Trend analysis

### 14.4 Monitoring and Observability
- Adapter-level metrics
- Performance monitoring
- Error tracking

---

## Conclusion

The adapters layer demonstrates a well-structured implementation of dependency inversion principle with clear separation of concerns. Each adapter provides a clean interface for external service integration while maintaining domain independence. The use of design patterns like Repository, Adapter, and Mapper ensures maintainability and testability. The system is designed for extensibility, making it easy to add new AWS services, notification channels, or database backends without affecting domain logic.

The current implementation provides solid foundations for AWS monitoring with good error handling, pagination support, and template-based notifications. The architecture supports the clean separation needed for scaling the system while maintaining code quality and maintainability.

# System Design Document

## Overview

The AWS Monitoring System is a serverless application built using hexagonal architecture (ports and adapters pattern) that provides centralized monitoring and alerting for AWS infrastructure across multiple accounts. The system collects, processes, and reports on monitoring events from various AWS services including CloudWatch, GuardDuty, and Health Dashboard.

## Architecture

### Design Principles

- **Hexagonal Architecture**: Clean separation between business logic and external dependencies
- **Serverless-First**: Built entirely on AWS Lambda and managed services
- **Event-Driven**: Utilizes EventBridge for decoupled event processing
- **Multi-Account**: Supports monitoring across multiple AWS accounts
- **Scalable**: Pay-per-use model with automatic scaling

### Core Components

The system follows a hexagonal architecture with clear layer separation:

#### 1. Domain Layer (`src/domain/`)
**Purpose**: Contains the core business logic and rules

- **Models**: Core business entities
  - `Event`: Monitoring event with metadata (account, region, source, severity)
  - `Agent`: Represents monitoring agents deployed in each AWS account
- **Use Cases**: Business logic orchestration
  - `insert_monitoring_event`: Process and store incoming monitoring events
  - `daily_report`: Generate and send daily monitoring reports
  - `query_error_logs`: Query CloudWatch logs for error patterns
  - `update_deployment`: Track deployment status of monitoring agents
- **Ports**: Interfaces defining contracts for external dependencies
  - `IEventRepository`, `IAgentRepository`: Data persistence interfaces
  - `IEventNotifier`, `IReportNotifier`: Notification interfaces
  - `IEventPublisher`: Event publishing interface
  - `ILogQueryAdapter`: Log querying interface

#### 2. Adapters Layer (`src/adapters/`)
**Purpose**: Implements domain interfaces and handles external dependencies

- **Database Adapters** (`src/adapters/db/`):
  - DynamoDB repositories implementing domain repository interfaces
  - Model mappers for domain ↔ database conversion
  - Query result abstractions
- **AWS Service Adapters** (`src/adapters/aws/`):
  - CloudWatch adapter for log querying and metrics
  - EventBridge adapter for event publishing
  - Lambda function utilities
  - ECS service monitoring
- **Notification Adapters** (`src/adapters/notifiers/`):
  - Event notification handlers (Slack, email, etc.)
  - Report generation and distribution
- **External Service Adapters**:
  - Log adapters for CloudWatch integration
  - Event publishers for EventBridge

#### 3. Entry Points Layer (`src/entrypoints/`)
**Purpose**: Application entry points and API handlers

- **Lambda Functions** (`src/entrypoints/functions/`):
  - `HandleMonitoringEvents`: Process incoming monitoring events
  - `DailyReport`: Generate and send daily reports
  - `QueryErrorLogs`: Query CloudWatch logs for errors
  - `UpdateDeployment`: Handle deployment status updates
- **API Gateway Handlers** (`src/entrypoints/apigw/`):
  - Agent management endpoints
  - Event querying endpoints

#### 4. Common Layer (`src/common/`)
**Purpose**: Shared utilities and cross-cutting concerns

- Configuration management
- Logging utilities
- Date/time utilities
- Exception handling
- Utility functions

## Deployment Architecture

### Two-Stack Approach

The system is deployed as two separate serverless stacks:

#### Master Stack
**Deployment**: Single deployment in central monitoring account
**Components**:
- EventBridge custom event bus for monitoring events
- DynamoDB table for event and agent persistence
- Lambda functions for event processing and reporting
- API Gateway for external access
- SQS dead letter queues for failed events

**Functions**:
- `HandleMonitoringEvents`: Processes all incoming monitoring events
- `DailyReport`: Generates daily monitoring reports (scheduled)
- `UpdateDeployment`: Tracks agent deployment status

#### Agent Stack
**Deployment**: Deployed to each monitored AWS account
**Components**:
- EventBridge rules for local event capture
- Lambda function for log querying
- IAM roles for cross-account access

**Functions**:
- `QueryErrorLogs`: Queries CloudWatch logs and publishes events to master

### Data Flow

```
AWS Services (CloudWatch, GuardDuty, Health)
    ↓
EventBridge (Agent Account)
    ↓
QueryErrorLogs (Agent Lambda)
    ↓
EventBridge (Master Event Bus)
    ↓
HandleMonitoringEvents (Master Lambda)
    ↓
DynamoDB + Notifications
```

## Infrastructure

### Data Storage

#### DynamoDB Table Schema
Single table design with composite primary key:

**Events**:
- `pk`: `EVENT` (partition key)
- `sk`: `EVENT#{timestamp}#{event_id}` (sort key)
- Additional attributes: account, region, source, detail, severity, resources

**Agents**:
- `pk`: `AGENT` (partition key)
- `sk`: `AGENT#{account_id}` (sort key)
- Additional attributes: region, status, deployed_at, created_at

**Access Patterns**:
- List all events (time-ordered)
- Query events by time range
- Get/update agent by account ID
- List all agents

### Event Processing

#### EventBridge Configuration
**Custom Event Bus**: `monitoring-master-{stage}-MonitoringEventBus`

**Event Sources**:
- `aws.cloudwatch`: CloudWatch alarms and metrics
- `aws.guardduty`: Security findings
- `aws.health`: Service health events
- `monitoring.agent.*`: Agent-generated events

**Event Routing**:
- Monitoring events → `HandleMonitoringEvents`
- Deployment events → `UpdateDeployment`
- Failed events → SQS dead letter queue

### Security

#### IAM Roles and Policies
- **Lambda Execution Role**: Basic Lambda permissions + DynamoDB access
- **EventBridge Role**: Cross-account event publishing permissions
- **Cross-Account Access**: Agent stacks can publish to master event bus

#### Data Security
- DynamoDB encryption at rest
- Lambda environment variable encryption
- VPC isolation (when required)
- Least privilege IAM policies

## Monitoring and Observability

### Logging
- Structured logging using AWS Lambda Powertools
- CloudWatch log groups per Lambda function
- Log retention policies (configurable)

### Metrics
- Built-in Lambda metrics (duration, errors, invocations)
- Custom business metrics via CloudWatch
- DynamoDB performance metrics

### Error Handling
- Dead letter queues for failed event processing
- Retry mechanisms with exponential backoff
- Error notifications via configured channels

### Daily Reports
- Scheduled Lambda function for daily report generation
- Configurable notification channels (Slack, email)
- Summary of events, errors, and system health

## Scalability and Performance

### Auto-Scaling
- Lambda functions scale automatically based on demand
- DynamoDB on-demand billing scales with usage
- EventBridge handles high throughput event processing

### Performance Considerations
- Single table design for efficient DynamoDB queries
- Optimized Lambda memory allocation (256MB default)
- Connection pooling for database connections
- Efficient event payload processing

### Cost Optimization
- Pay-per-use serverless model
- DynamoDB TTL for automatic data cleanup (90 days default)
- Optimized Lambda memory and timeout settings
- Event filtering to reduce unnecessary processing

## Configuration Management

### Environment-Specific Configs
- Stage-based configuration files (`infra/{stack}/configs/{stage}.yml`)
- Environment variables for runtime configuration
- Serverless Framework variable resolution

### Deployment
- Infrastructure as Code using Serverless Framework
- Separate deployment processes for master and agent stacks
- CloudFormation for AWS resource management

## Development and Testing

### Local Development
- LocalStack for local AWS service emulation
- Docker Compose for development environment
- Make commands for common operations

### Testing Strategy
- Unit tests for domain logic
- Integration tests for adapters
- End-to-end tests for complete workflows
- Coverage reporting with pytest-cov

### CI/CD Considerations
- Separate pipelines for master and agent deployments
- Environment promotion strategy
- Automated testing before deployment
- Blue-green deployment capability

## Future Enhancements

### Potential Improvements
- Real-time dashboards with WebSocket API
- Machine learning for anomaly detection
- Custom metrics and alerting rules
- Multi-region deployment support
- Enhanced security with AWS WAF and Shield

### Extensibility Points
- Plugin architecture for new event sources
- Configurable notification channels
- Custom report formats and templates
- Integration with external monitoring tools

## Technology Stack

### Core Technologies
- **Runtime**: Python 3.13
- **Framework**: Serverless Framework
- **Database**: Amazon DynamoDB
- **Event Processing**: Amazon EventBridge
- **Compute**: AWS Lambda
- **API**: Amazon API Gateway
- **Notifications**: Amazon SNS/SQS

### Development Tools
- **Package Management**: Poetry
- **Testing**: Pytest
- **Code Quality**: Ruff, isort, bandit
- **Local Development**: LocalStack, Docker
- **Documentation**: Markdown

### AWS Services Used
- Lambda (compute)
- DynamoDB (database)
- EventBridge (event routing)
- API Gateway (REST API)
- CloudWatch (logging, monitoring)
- SNS (notifications)
- SQS (dead letter queues)
- IAM (security)
- CloudFormation (infrastructure)

This design provides a robust, scalable, and maintainable monitoring solution that follows cloud-native best practices while maintaining clean architecture principles.
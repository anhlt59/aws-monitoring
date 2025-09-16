# AWS Monitoring System - DDD & Hexagonal Architecture Refactoring Plan

## Executive Summary

This document outlines a comprehensive refactoring plan to transform the current AWS monitoring system from its existing layered architecture to a Domain-Driven Design (DDD) approach with hexagonal architecture principles. The refactoring will improve maintainability, testability, and domain clarity while preserving all existing functionality.

## Current Architecture Analysis

### Current Structure
The project currently follows a hybrid approach with some DDD concepts but lacks clear domain boundaries and proper hexagonal architecture:

```
src/
├── common/              # Shared utilities and cross-cutting concerns
├── infras/             # Infrastructure layer (AWS services, DB)
├── modules/            # Business modules (master, agent)
└── entrypoints/        # Lambda handlers and API endpoints
```

### Identified Issues
1. **Mixed Responsibilities**: Business logic scattered across handlers and services
2. **Infrastructure Coupling**: Domain models directly dependent on infrastructure
3. **Unclear Domain Boundaries**: Master and Agent modules lack clear domain separation
4. **Missing Aggregate Roots**: No clear aggregate boundaries for data consistency
5. **Weak Domain Language**: Generic names like "Event" don't express business intent

## Domain Analysis

### Bounded Contexts

#### 1. Monitoring Context
**Ubiquitous Language:**
- **Monitoring Event**: A significant occurrence in the monitored infrastructure
- **Event Stream**: Continuous flow of monitoring events
- **Alert Rule**: Business rule that determines when to trigger notifications
- **Severity Level**: Business classification of event importance

**Core Entities:**
- `MonitoringEvent` (Aggregate Root)
- `AlertRule`
- `EventSeverity` (Value Object)

#### 2. Agent Management Context
**Ubiquitous Language:**
- **Monitoring Agent**: A deployed monitoring component in an AWS account
- **Agent Deployment**: The process and state of deploying an agent
- **Account Monitoring**: The monitoring capability for a specific AWS account

**Core Entities:**
- `MonitoringAgent` (Aggregate Root)
- `AgentDeployment`
- `AwsAccount` (Value Object)

#### 3. Notification Context
**Ubiquitous Language:**
- **Alert**: A notification triggered by monitoring events
- **Notification Channel**: A destination for alerts (Slack, email, etc.)
- **Alert Template**: Predefined format for different types of notifications

**Core Entities:**
- `Alert` (Aggregate Root)
- `NotificationChannel`
- `AlertTemplate` (Value Object)

### Domain Services
- `EventClassificationService`: Determines event severity and classification
- `AlertingService`: Orchestrates alert generation and delivery
- `AgentDeploymentService`: Manages agent lifecycle

## Target Hexagonal Architecture

### Core Architecture Principles

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Use Cases     │  │   Application   │  │    DTOs      │ │
│  │   (Commands/    │  │    Services     │  │              │ │
│  │    Queries)     │  │                 │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                               │
┌───────────────────────────────────────────────────────────────┐
│                     Domain Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │   Aggregates    │  │  Domain Events  │  │ Value Objects │  │
│  │   - Entities    │  │                 │  │               │  │
│  │   - Root        │  │                 │  │               │  │
│  └─────────────────┘  └─────────────────┘  └───────────────┘  │
│  ┌─────────────────┐  ┌─────────────────────────────────────┐ │
│  │ Domain Services │  │          Repositories (Ports)       │ │
│  │                 │  │                                     │ │
│  └─────────────────┘  └─────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Repository    │  │   External      │  │   Message    │ │
│  │  Implementations│  │   Services      │  │   Handlers   │ │
│  │                 │  │  (AWS APIs)     │  │   (Lambda)   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### New Directory Structure

```
src/
├── shared/                                 # Shared kernel
│   ├── domain/
│   │   ├── value_objects/
│   │   ├── events/
│   │   └── exceptions/
│   └── infrastructure/
│       ├── persistence/
│       ├── messaging/
│       └── aws_clients/
│
├── contexts/                              # Bounded contexts
│   ├── monitoring/
│   │   ├── domain/
│   │   │   ├── aggregates/
│   │   │   │   ├── monitoring_event.py
│   │   │   │   └── alert_rule.py
│   │   │   ├── value_objects/
│   │   │   │   ├── event_severity.py
│   │   │   │   ├── event_source.py
│   │   │   │   └── aws_resource.py
│   │   │   ├── services/
│   │   │   │   └── event_classification_service.py
│   │   │   ├── events/
│   │   │   │   ├── monitoring_event_received.py
│   │   │   │   └── alert_triggered.py
│   │   │   └── repositories/
│   │   │       ├── monitoring_event_repository.py
│   │   │       └── alert_rule_repository.py
│   │   ├── application/
│   │   │   ├── use_cases/
│   │   │   │   ├── process_monitoring_event.py
│   │   │   │   ├── query_events.py
│   │   │   │   └── create_alert_rule.py
│   │   │   ├── services/
│   │   │   │   └── monitoring_application_service.py
│   │   │   └── dtos/
│   │   │       ├── event_query_dto.py
│   │   │       └── alert_rule_dto.py
│   │   └── infrastructure/
│   │       ├── persistence/
│   │       │   ├── dynamodb_monitoring_event_repository.py
│   │       │   └── monitoring_event_mapper.py
│   │       ├── messaging/
│   │       │   └── eventbridge_event_publisher.py
│   │       └── external_services/
│   │           └── cloudwatch_log_service.py
│   │
│   ├── agent_management/
│   │   ├── domain/
│   │   │   ├── aggregates/
│   │   │   │   └── monitoring_agent.py
│   │   │   ├── value_objects/
│   │   │   │   ├── aws_account.py
│   │   │   │   ├── deployment_status.py
│   │   │   │   └── aws_region.py
│   │   │   ├── services/
│   │   │   │   └── agent_deployment_service.py
│   │   │   ├── events/
│   │   │   │   ├── agent_deployed.py
│   │   │   │   └── agent_deployment_failed.py
│   │   │   └── repositories/
│   │   │       └── monitoring_agent_repository.py
│   │   ├── application/
│   │   │   ├── use_cases/
│   │   │   │   ├── deploy_agent.py
│   │   │   │   ├── update_agent_status.py
│   │   │   │   └── list_agents.py
│   │   │   └── services/
│   │   │       └── agent_management_service.py
│   │   └── infrastructure/
│   │       ├── persistence/
│   │       │   └── dynamodb_agent_repository.py
│   │       └── external_services/
│   │           └── cloudformation_service.py
│   │
│   └── notification/
│       ├── domain/
│       │   ├── aggregates/
│       │   │   └── alert.py
│       │   ├── value_objects/
│       │   │   ├── notification_channel.py
│       │   │   └── alert_template.py
│       │   ├── services/
│       │   │   └── alerting_service.py
│       │   └── events/
│       │       └── alert_sent.py
│       ├── application/
│       │   ├── use_cases/
│       │   │   ├── send_alert.py
│       │   │   └── configure_notification_channel.py
│       │   └── services/
│       │       └── notification_application_service.py
│       └── infrastructure/
│           ├── notification_channels/
│           │   ├── slack_notifier.py
│           │   └── email_notifier.py
│           └── templates/
│               └── alert_template_renderer.py
│
└── entrypoints/                           # Infrastructure adapters
    ├── lambda_handlers/
    │   ├── monitoring/
    │   │   ├── handle_monitoring_events.py
    │   │   └── query_events_api.py
    │   ├── agent_management/
    │   │   ├── deploy_agent_api.py
    │   │   └── update_deployment.py
    │   └── notification/
    │       └── daily_report.py
    └── api_gateway/
        ├── monitoring/
        └── agent_management/
```

## Detailed Refactoring Plan

### Phase 1: Establish Domain Foundation (Week 1-2)

#### 1.1 Create Shared Kernel
- **Create `src/shared/domain/value_objects/`**
  - `AwsAccountId`: Strongly-typed AWS account identifier
  - `AwsRegion`: AWS region value object with validation
  - `Timestamp`: UTC timestamp with domain operations
  - `ResourceArn`: AWS resource ARN with parsing capabilities

- **Create `src/shared/domain/events/`**
  - `DomainEvent`: Base class for all domain events
  - `DomainEventPublisher`: Event publishing infrastructure

- **Create `src/shared/domain/exceptions/`**
  - `DomainException`: Base domain exception
  - `AggregateNotFoundException`
  - `BusinessRuleViolationException`

#### 1.2 Migration Strategy for Shared Kernel
```python
# Before (in src/common/models.py)
class BaseModel(BaseModel):
    pass

# After (in src/shared/domain/value_objects/aws_account_id.py)
@dataclass(frozen=True)
class AwsAccountId:
    value: str

    def __post_init__(self):
        if not re.match(r'^\d{12}$', self.value):
            raise ValueError("AWS Account ID must be 12 digits")
```

### Phase 2: Monitoring Context Refactoring (Week 3-4)

#### 2.1 Domain Layer Implementation

**MonitoringEvent Aggregate Root:**
```python
# src/contexts/monitoring/domain/aggregates/monitoring_event.py
class MonitoringEvent:
    def __init__(
        self,
        event_id: EventId,
        account: AwsAccountId,
        source: EventSource,
        occurred_at: Timestamp,
        raw_data: dict
    ):
        self._id = event_id
        self._account = account
        self._source = source
        self._occurred_at = occurred_at
        self._raw_data = raw_data
        self._severity = self._classify_severity()
        self._domain_events: List[DomainEvent] = []

    def classify_severity(self, classification_service: EventClassificationService) -> None:
        """Business logic for event classification"""
        self._severity = classification_service.classify(self)
        self._domain_events.append(
            MonitoringEventClassified(self._id, self._severity)
        )

    def trigger_alert_if_needed(self, alert_rules: List[AlertRule]) -> None:
        """Business logic for alert triggering"""
        for rule in alert_rules:
            if rule.matches(self):
                self._domain_events.append(
                    AlertTriggered(self._id, rule.id, self._severity)
                )
```

**Value Objects:**
```python
# src/contexts/monitoring/domain/value_objects/event_severity.py
@dataclass(frozen=True)
class EventSeverity:
    level: int  # 0-4
    label: str  # Unknown, Low, Medium, High, Critical

    @classmethod
    def from_level(cls, level: int) -> 'EventSeverity':
        labels = ["Unknown", "Low", "Medium", "High", "Critical"]
        if not 0 <= level <= 4:
            raise ValueError("Severity level must be between 0 and 4")
        return cls(level=level, label=labels[level])
```

#### 2.2 Application Layer Implementation

**Use Cases:**
```python
# src/contexts/monitoring/application/use_cases/process_monitoring_event.py
class ProcessMonitoringEventUseCase:
    def __init__(
        self,
        event_repository: MonitoringEventRepository,
        classification_service: EventClassificationService,
        alert_rule_repository: AlertRuleRepository,
        event_publisher: DomainEventPublisher
    ):
        self._event_repository = event_repository
        self._classification_service = classification_service
        self._alert_rule_repository = alert_rule_repository
        self._event_publisher = event_publisher

    def execute(self, command: ProcessMonitoringEventCommand) -> None:
        # Create domain object
        event = MonitoringEvent.from_aws_event(command.aws_event_data)

        # Apply business logic
        event.classify_severity(self._classification_service)

        # Check alert rules
        alert_rules = self._alert_rule_repository.find_by_source(event.source)
        event.trigger_alert_if_needed(alert_rules)

        # Persist
        self._event_repository.save(event)

        # Publish domain events
        for domain_event in event.domain_events:
            self._event_publisher.publish(domain_event)
```

#### 2.3 Infrastructure Layer Implementation

**Repository Implementation:**
```python
# src/contexts/monitoring/infrastructure/persistence/dynamodb_monitoring_event_repository.py
class DynamoDbMonitoringEventRepository(MonitoringEventRepository):
    def __init__(self, table_name: str, mapper: MonitoringEventMapper):
        self._table_name = table_name
        self._mapper = mapper

    def save(self, event: MonitoringEvent) -> None:
        persistence_model = self._mapper.to_persistence(event)
        persistence_model.save()

    def find_by_id(self, event_id: EventId) -> Optional[MonitoringEvent]:
        try:
            persistence_model = EventPersistence.get(
                hash_key="EVENT",
                range_key=f"EVENT#{event_id.value}"
            )
            return self._mapper.to_domain(persistence_model)
        except DoesNotExist:
            return None
```

### Phase 3: Agent Management Context (Week 5-6)

#### 3.1 Domain Implementation

**MonitoringAgent Aggregate:**
```python
# src/contexts/agent_management/domain/aggregates/monitoring_agent.py
class MonitoringAgent:
    def __init__(
        self,
        account: AwsAccountId,
        region: AwsRegion,
        deployment_config: AgentDeploymentConfig
    ):
        self._account = account
        self._region = region
        self._deployment_config = deployment_config
        self._status = DeploymentStatus.PENDING
        self._deployed_at: Optional[Timestamp] = None
        self._domain_events: List[DomainEvent] = []

    def deploy(self, deployment_service: AgentDeploymentService) -> None:
        """Business logic for agent deployment"""
        if self._status != DeploymentStatus.PENDING:
            raise BusinessRuleViolationException(
                "Agent can only be deployed when in PENDING status"
            )

        try:
            deployment_service.deploy(self._account, self._region, self._deployment_config)
            self._status = DeploymentStatus.DEPLOYING
            self._domain_events.append(
                AgentDeploymentStarted(self._account, self._region)
            )
        except DeploymentException as e:
            self._status = DeploymentStatus.FAILED
            self._domain_events.append(
                AgentDeploymentFailed(self._account, self._region, str(e))
            )

    def mark_deployed(self, deployed_at: Timestamp) -> None:
        """Called when deployment completes successfully"""
        self._status = DeploymentStatus.DEPLOYED
        self._deployed_at = deployed_at
        self._domain_events.append(
            AgentDeployed(self._account, self._region, deployed_at)
        )
```

### Phase 4: Notification Context (Week 7-8)

#### 4.1 Domain Implementation

**Alert Aggregate:**
```python
# src/contexts/notification/domain/aggregates/alert.py
class Alert:
    def __init__(
        self,
        alert_id: AlertId,
        monitoring_event: MonitoringEvent,
        alert_rule: AlertRule,
        notification_channels: List[NotificationChannel]
    ):
        self._id = alert_id
        self._monitoring_event = monitoring_event
        self._alert_rule = alert_rule
        self._notification_channels = notification_channels
        self._status = AlertStatus.PENDING
        self._created_at = Timestamp.now()
        self._domain_events: List[DomainEvent] = []

    def send(self, alerting_service: AlertingService) -> None:
        """Business logic for sending alerts"""
        if self._status != AlertStatus.PENDING:
            raise BusinessRuleViolationException("Alert has already been processed")

        try:
            for channel in self._notification_channels:
                alerting_service.send_to_channel(self, channel)

            self._status = AlertStatus.SENT
            self._domain_events.append(
                AlertSent(self._id, self._monitoring_event.id, self._created_at)
            )
        except Exception as e:
            self._status = AlertStatus.FAILED
            self._domain_events.append(
                AlertSendFailed(self._id, str(e))
            )
```

### Phase 5: Infrastructure Adapters (Week 9-10)

#### 5.1 Lambda Handler Refactoring

**Event Processing Handler:**
```python
# src/entrypoints/lambda_handlers/monitoring/handle_monitoring_events.py
def handler(event, context):
    # Dependency injection setup
    container = create_container()
    use_case = container.get(ProcessMonitoringEventUseCase)

    # Parse AWS event
    aws_event = AwsEventBridgeEvent.from_lambda_event(event)
    command = ProcessMonitoringEventCommand.from_aws_event(aws_event)

    # Execute use case
    try:
        use_case.execute(command)
        return {"statusCode": 200}
    except DomainException as e:
        logger.error(f"Domain error: {e}")
        return {"statusCode": 400, "body": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"statusCode": 500}
```

#### 5.2 Dependency Injection Container

```python
# src/shared/infrastructure/container.py
class Container:
    def __init__(self):
        self._services = {}
        self._configure_monitoring_context()
        self._configure_agent_management_context()
        self._configure_notification_context()

    def _configure_monitoring_context(self):
        # Repositories
        self.register(
            MonitoringEventRepository,
            lambda: DynamoDbMonitoringEventRepository(
                table_name=os.getenv("EVENTS_TABLE"),
                mapper=MonitoringEventMapper()
            )
        )

        # Services
        self.register(
            EventClassificationService,
            lambda: EventClassificationService()
        )

        # Use cases
        self.register(
            ProcessMonitoringEventUseCase,
            lambda: ProcessMonitoringEventUseCase(
                event_repository=self.get(MonitoringEventRepository),
                classification_service=self.get(EventClassificationService),
                alert_rule_repository=self.get(AlertRuleRepository),
                event_publisher=self.get(DomainEventPublisher)
            )
        )
```

## Migration Strategy

### Step-by-Step Migration Process

#### Phase 1: Parallel Implementation
1. **Create new structure alongside existing code**
2. **Implement shared kernel without touching existing code**
3. **Create domain models parallel to existing models**
4. **Write comprehensive tests for new domain logic**

#### Phase 2: Gradual Migration
1. **Start with monitoring context**
2. **Create adapters to convert between old and new models**
3. **Update one handler at a time to use new structure**
4. **Maintain backward compatibility during transition**

#### Phase 3: Legacy Cleanup
1. **Remove old models once all handlers are migrated**
2. **Update tests to use new structure**
3. **Clean up unused infrastructure code**

### Data Migration Strategy

```python
# Migration script example
class EventModelMigration:
    def migrate_existing_events(self):
        # Read existing events using old repository
        old_repo = EventRepository()  # Current implementation
        events = old_repo.list()

        # Convert to new domain model
        new_repo = DynamoDbMonitoringEventRepository()
        for old_event in events:
            new_event = self._convert_to_domain_model(old_event)
            new_repo.save(new_event)

    def _convert_to_domain_model(self, old_event) -> MonitoringEvent:
        return MonitoringEvent(
            event_id=EventId(old_event.id),
            account=AwsAccountId(old_event.account),
            source=EventSource(old_event.source),
            occurred_at=Timestamp(old_event.published_at),
            raw_data=old_event.detail
        )
```

## Testing Strategy

### Domain Testing
```python
# Test example for MonitoringEvent aggregate
class TestMonitoringEvent:
    def test_high_severity_event_triggers_alert(self):
        # Arrange
        event = MonitoringEvent.create(
            event_id=EventId("test-123"),
            account=AwsAccountId("123456789012"),
            source=EventSource("aws.cloudwatch"),
            occurred_at=Timestamp.now(),
            raw_data={"alarm": "CPU_HIGH"}
        )

        alert_rule = AlertRule.for_high_severity_events()
        classification_service = MockEventClassificationService()
        classification_service.setup_classification(event, EventSeverity.HIGH)

        # Act
        event.classify_severity(classification_service)
        event.trigger_alert_if_needed([alert_rule])

        # Assert
        assert event.severity == EventSeverity.HIGH
        domain_events = event.domain_events
        assert len(domain_events) == 2
        assert isinstance(domain_events[0], MonitoringEventClassified)
        assert isinstance(domain_events[1], AlertTriggered)
```

### Integration Testing
```python
# Test example for use case
class TestProcessMonitoringEventUseCase:
    def test_processes_cloudwatch_alarm_event(self):
        # Arrange
        container = create_test_container()
        use_case = container.get(ProcessMonitoringEventUseCase)

        command = ProcessMonitoringEventCommand(
            aws_event_data={
                "source": "aws.cloudwatch",
                "account": "123456789012",
                "detail": {"alarm": "test"}
            }
        )

        # Act
        use_case.execute(command)

        # Assert
        event_repo = container.get(MonitoringEventRepository)
        saved_events = event_repo.find_by_account(AwsAccountId("123456789012"))
        assert len(saved_events) == 1
```

## Benefits of the Refactored Architecture

### 1. Domain Clarity
- **Clear Ubiquitous Language**: Business concepts are explicitly modeled
- **Domain Expertise Captured**: Business rules are encapsulated in domain objects
- **Better Communication**: Developers and business stakeholders share common language

### 2. Maintainability
- **Separation of Concerns**: Business logic separated from infrastructure
- **Testable Design**: Domain logic can be tested in isolation
- **Flexible Infrastructure**: Easy to swap out AWS services or databases

### 3. Extensibility
- **New Event Sources**: Easy to add new monitoring sources
- **New Notification Channels**: Simple to add email, SMS, or other channels
- **New Business Rules**: Alert rules can be modified without changing infrastructure

### 4. Technical Benefits
- **Dependency Inversion**: Infrastructure depends on domain, not vice versa
- **Event-Driven Architecture**: Domain events enable loose coupling
- **SOLID Principles**: All SOLID principles are properly applied

## Conclusion

This refactoring plan transforms the AWS monitoring system into a robust, maintainable architecture that clearly expresses business intent while remaining flexible for future changes. The migration strategy ensures minimal disruption to existing functionality while establishing a solid foundation for future development.

The new structure will make it easier to:
- Add new types of monitoring events
- Implement complex alerting rules
- Test business logic independently
- Scale individual contexts separately
- Onboard new team members with clear domain boundaries

**Estimated Timeline**: 10 weeks with 1-2 developers
**Risk Level**: Medium (due to comprehensive testing and gradual migration strategy)
**Business Impact**: Minimal disruption during migration, significant long-term benefits

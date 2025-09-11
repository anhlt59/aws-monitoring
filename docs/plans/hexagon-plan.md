# Hexagonal Architecture Improvement Plan

## Current State Analysis

The AWS monitoring application currently follows a layered architecture with some hexagonal principles but lacks strict enforcement of dependency inversion and interface-based abstractions. The codebase is organized into:

- **Handlers** (Presentation Layer): Lambda entry points
- **Services** (Application Layer): Business logic orchestration  
- **Repositories** (Infrastructure): Data access patterns
- **Infrastructure** (External Adapters): AWS service abstractions

## Identified Violations

### 1. Direct Infrastructure Dependencies
- **Issue**: Handlers and services directly import and instantiate concrete AWS clients
- **Examples**:
  - `src/modules/master/handlers/handle_monitoring_events/main.py:16-17` - Direct instantiation of `EventRepository()` and `SlackClient()`
  - `src/infras/aws/cloudwatch.py:16` - Direct boto3 client creation
  - `src/infras/aws/eventbridge.py:15` - Direct boto3 client instantiation

### 2. Missing Interfaces (Ports)
- **Issue**: No interface definitions for external dependencies
- **Missing Interfaces**:
  - Database repository interface
  - Notification service interface
  - AWS service interfaces (CloudWatch, EventBridge, etc.)
  - External HTTP client interface

### 3. Tight Coupling in Service Layer
- **Issue**: Services directly depend on concrete implementations
- **Examples**:
  - `src/modules/agent/services/publisher.py:24` - Direct dependency on `EventBridgeService`
  - `src/modules/master/services/repositories/event.py:10` - Inherits from concrete `DynamoRepository`

### 4. Configuration Coupling
- **Issue**: Infrastructure components directly access global config
- **Examples**:
  - `src/infras/aws/cloudwatch.py:7` - Direct import of AWS_ENDPOINT, AWS_REGION
  - Multiple AWS services have hardcoded configuration dependencies

### 5. Limited Dependency Injection
- **Issue**: No formal DI container or pattern
- **Impact**: Difficult to test, tight coupling, inflexible configuration

## Improvement Plan

### Phase 1: Define Core Interfaces (Ports)

#### 1.1 Create Database Interfaces
```python
# src/common/interfaces/repository.py
from typing import Protocol, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class Repository(Protocol, Generic[T]):
    def get(self, id: str) -> T: ...
    def create(self, entity: T) -> None: ...
    def update(self, id: str, entity: T) -> None: ...
    def delete(self, id: str) -> None: ...

class EventRepositoryInterface(Repository[Event], Protocol):
    def list(self, dto: ListEventsDTO | None = None) -> EventQueryResult: ...

class AgentRepositoryInterface(Repository[Agent], Protocol):
    def list(self) -> list[Agent]: ...
```

#### 1.2 Create Notification Interfaces
```python
# src/common/interfaces/notifier.py
from typing import Protocol
from src.infras.aws.data_classes import EventBridgeEvent

class NotificationClientInterface(Protocol):
    def send(self, message: Any) -> None: ...

class EventNotifierInterface(Protocol):
    def notify(self, event: EventBridgeEvent) -> None: ...
```

#### 1.3 Create AWS Service Interfaces
```python
# src/common/interfaces/aws.py
from typing import Protocol
from types_boto3_logs.type_defs import ResultFieldTypeDef
from types_boto3_events.type_defs import PutEventsRequestEntryTypeDef

class CloudWatchLogsInterface(Protocol):
    def query_logs(self, log_group_names: list[str], query_string: str, 
                   start_time: int, end_time: int) -> list[ResultFieldTypeDef]: ...

class EventBridgeInterface(Protocol):
    def put_events(self, *events: PutEventsRequestEntryTypeDef) -> None: ...
```

### Phase 2: Implement Service Adapters

#### 2.1 Refactor Repository Layer
```python
# src/infras/db/services/event_repository.py
from src.common.interfaces.repository import EventRepositoryInterface
from src.infras.db.repository import DynamoRepository

class DynamoEventRepositoryService(DynamoRepository, EventRepositoryInterface):
    # Implementation using existing DynamoRepository as base
    pass
```

#### 2.2 Refactor AWS Services
```python
# src/infras/aws/services/cloudwatch_service.py
from src.common.interfaces.aws import CloudWatchLogsInterface

class CloudWatchLogsService(CloudWatchLogsInterface):
    def __init__(self, endpoint_url: str, region: str):
        self.client = boto3.client("logs", endpoint_url=endpoint_url, region_name=region)
    # Implementation
```

#### 2.3 Refactor Notification Services
```python
# src/infras/notification/services/slack_service.py
from src.common.interfaces.notifier import NotificationClientInterface

class SlackNotificationService(NotificationClientInterface):
    def __init__(self, webhook_url: str, timeout: int = 10):
        # Implementation
```

### Phase 3: Implement Dependency Injection

#### 3.1 Create DI Container
```python
# src/common/container.py
from typing import Dict, Any, TypeVar, Type
from src.common.interfaces import *

T = TypeVar('T')

class DIContainer:
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Any] = {}
    
    def register(self, interface: Type[T], implementation: T) -> None: ...
    def register_factory(self, interface: Type[T], factory: callable) -> None: ...
    def get(self, interface: Type[T]) -> T: ...
```

#### 3.2 Configuration-Based Registration
```python
# src/common/container_config.py
def configure_container(container: DIContainer, config: dict) -> None:
    # Register AWS services
    container.register_factory(
        CloudWatchLogsInterface,
        lambda: CloudWatchLogsService(config['aws_endpoint'], config['aws_region'])
    )
    
    # Register repositories
    container.register_factory(
        EventRepositoryInterface,
        lambda: DynamoEventRepositoryService()
    )
    
    # Register notification services
    container.register_factory(
        NotificationClientInterface,
        lambda: SlackNotificationService(config['slack_webhook'])
    )
```

### Phase 4: Refactor Handlers and Services

#### 4.1 Update Handlers for DI
```python
# src/modules/master/handlers/handle_monitoring_events/main.py
from src.common.container import get_container
from src.common.interfaces.repository import EventRepositoryInterface
from src.common.interfaces.notifier import NotificationClientInterface

def handler(event: EventBridgeEvent, context):
    container = get_container()
    event_repo = container.get(EventRepositoryInterface)
    slack_client = container.get(NotificationClientInterface)
    
    # Business logic using interfaces
```

#### 4.2 Update Services
```python
# src/modules/agent/services/publisher.py
from src.common.interfaces.aws import EventBridgeInterface

class Publisher:
    def __init__(self, client: EventBridgeInterface):
        self.client = client
    
    def publish(self, *events: Event):
        # Implementation using interface
```

### Phase 5: Testing Infrastructure

#### 5.1 Create Mock Implementations
```python
# tests/mocks/repositories.py
from src.common.interfaces.repository import EventRepositoryInterface

class MockEventRepository(EventRepositoryInterface):
    def __init__(self):
        self._events = {}
    
    def get(self, id: str) -> Event: ...
    def create(self, entity: Event) -> None: ...
    # Other methods
```

#### 5.2 Test Container Configuration
```python
# tests/conftest.py
@pytest.fixture
def test_container():
    container = DIContainer()
    container.register(EventRepositoryInterface, MockEventRepository())
    container.register(NotificationClientInterface, MockSlackClient())
    return container
```

## Implementation Priority

### High Priority (Phase 1-2)
1. **Repository Interfaces** - Core data access abstraction
2. **AWS Service Interfaces** - External service abstraction
3. **Notification Interfaces** - External communication abstraction

### Medium Priority (Phase 3-4)
1. **DI Container** - Dependency management
2. **Handler Refactoring** - Entry point decoupling
3. **Service Layer Updates** - Business logic isolation

### Low Priority (Phase 5)
1. **Advanced Testing** - Enhanced test infrastructure
2. **Configuration Management** - Environment-specific setup
3. **Documentation** - Architecture guidelines

## Expected Benefits

### 1. Testability
- Easy mocking of external dependencies
- Isolated unit testing
- Faster test execution

### 2. Flexibility
- Easy swapping of implementations
- Environment-specific configurations
- Multiple provider support

### 3. Maintainability
- Clear separation of concerns
- Reduced coupling
- Interface-driven development

### 4. Extensibility
- New features without core changes
- Plugin-style architecture
- Clean integration points

## Migration Strategy

### 1. Backward Compatibility
- Implement interfaces alongside existing code
- Gradual migration per module
- Maintain existing functionality

### 2. Testing Strategy
- Create interface implementations first
- Test new interfaces with existing functionality
- Migrate tests incrementally

### 3. Rollout Plan
- Start with agent module (smaller scope)
- Move to master module repositories
- Update handlers last (highest risk)

## Success Metrics

1. **Code Coverage**: Maintain >90% coverage during migration
2. **Performance**: No degradation in handler response times
3. **Complexity**: Reduce cyclomatic complexity by 20%
4. **Dependencies**: Eliminate direct boto3 imports from business logic
5. **Testing**: Reduce test execution time by 50% with mocking

## Risks and Mitigation

### Risk: Over-Engineering
- **Mitigation**: Focus on actual pain points, avoid unnecessary abstractions

### Risk: Performance Impact
- **Mitigation**: Benchmark critical paths, optimize DI container

### Risk: Team Adoption
- **Mitigation**: Gradual rollout, documentation, training sessions

### Risk: Breaking Changes
- **Mitigation**: Maintain backward compatibility, feature flags for new code
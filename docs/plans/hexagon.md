# Hexagonal Architecture Refactoring Plan

This document outlines a plan to refactor the project's `src` directory to follow the principles of Hexagonal (Ports and Adapters) Architecture. The goal is to better isolate the core application logic from external concerns like AWS services, databases, and API endpoints.

## 1. Analysis of Current Structure

The current `src` directory is organized as follows:

- `src/common`: Contains shared code like models, exceptions, and utilities.
- `src/infras`: Contains infrastructure-specific code, primarily for interacting with AWS (CloudWatch, EventBridge) and DynamoDB (`repository.py`). This is a good separation of infrastructure code.
- `src/modules`: Contains the main business logic, split into `master` and `agent` modules.
  - Inside each module, `handlers` act as entry points (e.g., for Lambda), and `services` contain the business logic.

This structure is a hybrid of feature and layer-based organization. While it provides some separation, the core business logic in `services` is not fully isolated and may have direct dependencies on infrastructure code, making it harder to test in isolation.

## 2. Proposed Hexagonal Architecture

We will reorganize the code into three distinct layers:

1.  **Domain Layer (The Core):** Contains the heart of the application. It has no dependencies on any other layer.
    - **Entities & Domain Models:** Business objects and their rules.
    - **Ports:** Interfaces that define contracts for how the application layer communicates with the outside world (e.g., a `EventRepositoryPort` that defines methods like `save_event`).

2.  **Application Layer:** Orchestrates the domain logic to perform specific tasks (use cases).
    - **Use Cases/Services:** Implements application-specific business rules. It depends on the Domain Layer's ports but not on their concrete implementations.

3.  **Adapter Layer (Infrastructure):** Contains all the code that interacts with external systems. It depends on the Application and Domain layers.
    - **Primary/Driving Adapters:** Code that drives the application, such as Lambda handlers or API endpoints. They call the application layer's use cases.
    - **Secondary/Driven Adapters:** Implementations of the domain layer's ports. This includes database repositories, AWS service clients, notification services, etc.

## 3. Proposed Directory Structure

The `src` directory will be restructured as follows to reflect the hexagonal layers. The `master` and `agent` contexts will be preserved within this new structure.

```
src/
├── adapters/
│   ├── primary/
│   │   ├── agent/
│   │   │   └── event_handler/       # Was modules/agent/handlers
│   │   └── master/
│   │       ├── api/                 # Was modules/master/handlers/api
│   │       └── event_handler/       # Was modules/master/handlers/*
│   └── secondary/
│       ├── __init__.py
│       ├── aws/                     # Was infras/aws
│       ├── db/                      # Was infras/db
│       └── notifications/           # Was modules/master/services/notifiers
├── application/
│   ├── __init__.py
│   ├── agent/
│   │   └── use_cases/               # Was modules/agent/services
│   └── master/
│       └── use_cases/               # Was modules/master/services
├── common/
│   ├── __init__.py
│   ├── constants.py
│   ├── exceptions.py
│   └── logger.py
└── domain/
    ├── __init__.py
    ├── agent/
    │   ├── models.py
    │   └── ports.py
    └── master/
        ├── models.py
        └── ports.py
```

## 4. Step-by-Step Refactoring Plan

### Step 1: Establish the Domain Layer

1.  **Create `src/domain` directory.**
2.  **Identify and Move Domain Models:**
    - Move pure business models from `src/common/models.py`, `src/modules/agent/models/`, and `src/modules/master/models/` into `src/domain/agent/models.py` and `src/domain/master/models.py`. These models should not contain any infrastructure-specific details.
3.  **Define Ports (Interfaces):**
    - Create `src/domain/agent/ports.py` and `src/domain/master/ports.py`.
    - Define abstract base classes (using `abc.ABC`) for all secondary adapters. For example, in `ports.py`:
      ```python
      from abc import ABC, abstractmethod
      from .models import DomainEvent # Example import

      class EventRepository(ABC):
          @abstractmethod
          def save(self, event: DomainEvent) -> None:
              pass

      class EventPublisher(ABC):
          @abstractmethod
          def publish(self, event: DomainEvent) -> None:
              pass
      ```

### Step 2: Relocate and Refactor the Application Layer

1.  **Create `src/application` directory.**
2.  **Move Services to Use Cases:**
    - Move the contents of `src/modules/agent/services/` to `src/application/agent/use_cases/`.
    - Move the contents of `src/modules/master/services/` to `src/application/master/use_cases/`.
3.  **Implement Dependency Inversion:**
    - Refactor the use cases to depend on the ports (interfaces) defined in the domain layer, not on concrete implementations.
    - Use dependency injection to provide the concrete adapters at runtime.

    *Example Use Case (`HandleMonitoringEvent`):*
    ```python
    # application/master/use_cases/handle_monitoring_event.py
    from domain.master.ports import EventRepository, Notifier
    from domain.master.models import MonitoringEvent

    class HandleMonitoringEvent:
        def __init__(self, repo: EventRepository, notifier: Notifier):
            self.repo = repo
            self.notifier = notifier

        def execute(self, event_data: dict):
            event = MonitoringEvent.from_dict(event_data)
            self.repo.save(event)
            if event.is_critical():
                self.notifier.notify(event)
    ```

### Step 3: Relocate and Isolate Adapters

1.  **Create `src/adapters` directory.**
2.  **Relocate Primary Adapters (Handlers):**
    - Move Lambda handlers from `src/modules/agent/handlers/` to `src/adapters/primary/agent/`.
    - Move Lambda handlers from `src/modules/master/handlers/` to `src/adapters/primary/master/`.
3.  **Relocate Secondary Adapters (Infrastructure):**
    - Move `src/infras/aws/` to `src/adapters/secondary/aws/`.
    - Move `src/infras/db/` to `src/adapters/secondary/db/`.
    - Move `src/modules/master/services/notifiers/` to `src/adapters/secondary/notifications/`.
4.  **Implement Ports:**
    - Make the concrete adapter classes implement the corresponding port interfaces from the domain layer. For example, `DynamoDBEventRepository` in `src/adapters/secondary/db/event_repository.py` will implement `EventRepository` from `src/domain/master/ports.py`.

### Step 4: Composition Root (Wiring Dependencies)

The primary adapters (e.g., Lambda handlers) will now act as the "Composition Root". They are responsible for instantiating and wiring together the application.

*Example Handler (`handle_monitoring_events/main.py`):*
```python
# adapters/primary/master/event_handler/handle_monitoring_events.py

# Secondary Adapter Implementations
from adapters.secondary.db.dynamodb_repository import DynamoDBEventRepository
from adapters.secondary.notifications.slack_notifier import SlackNotifier

# Application Layer
from application.master.use_cases.handle_monitoring_event import HandleMonitoringEvent

def handler(event, context):
    # 1. Instantiate Adapters
    event_repository = DynamoDBEventRepository()
    notifier = SlackNotifier()

    # 2. Instantiate Use Case and inject dependencies
    use_case = HandleMonitoringEvent(repo=event_repository, notifier=notifier)

    # 3. Execute Use Case
    for record in event['Records']:
        use_case.execute(record)

    return {"status": "ok"}
```

This refactoring will result in a more modular, decoupled, and testable codebase that clearly separates business logic from infrastructure concerns.

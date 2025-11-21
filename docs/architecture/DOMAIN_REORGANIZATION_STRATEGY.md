# Domain Layer Reorganization Strategy

**Problem:** As business logic grows, the domain layer becomes hard to manage with too many models, ports, and use cases mixed together. The Event entity is shared across multiple subdomains.

**Solution:** Apply Domain-Driven Design (DDD) Bounded Contexts with a Shared Kernel approach.

---

## 1. Current State Analysis

### Current Structure (Monolithic Domain)
```
backend/src/domain/
├── models/
│   ├── event.py
│   ├── agent.py
│   ├── user.py
│   ├── task.py
│   ├── config.py
│   └── ... (growing)
├── use_cases/
│   ├── events/
│   ├── auth/
│   ├── tasks/
│   ├── users/
│   └── ... (growing)
└── ports/
    ├── repositories/
    └── services/
```

### Problems
- ❌ All domains mixed together
- ❌ Unclear boundaries between business capabilities
- ❌ Shared entities create coupling
- ❌ Hard to understand what belongs where
- ❌ Difficult to assign team ownership
- ❌ Risky refactoring (change ripples everywhere)

---

## 2. Proposed Architecture: Bounded Contexts

### 2.1 Identify Bounded Contexts

Based on your system, I recommend these bounded contexts:

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS MONITORING SYSTEM                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │   MONITORING     │  │   TASK MGMT      │                │
│  │    Context       │  │    Context       │                │
│  │                  │  │                  │                │
│  │  - Event         │  │  - Task          │                │
│  │  - Agent         │  │  - Comment       │                │
│  │  - Alert         │  │  - Assignment    │                │
│  └────────┬─────────┘  └────────┬─────────┘                │
│           │                     │                           │
│           │    ┌────────────────┴────────┐                  │
│           │    │   IDENTITY & ACCESS     │                  │
│           └────│      Context (IAM)      │                  │
│                │                          │                  │
│                │  - User                  │                  │
│                │  - Role                  │                  │
│                │  - Permission            │                  │
│                └────────┬─────────────────┘                  │
│                         │                                    │
│                ┌────────┴─────────┐                          │
│                │   CONFIGURATION  │                          │
│                │     Context      │                          │
│                │                  │                          │
│                │  - AwsAccount    │                          │
│                │  - MonitoringCfg │                          │
│                │  - ServiceConfig │                          │
│                └──────────────────┘                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘

         ┌──────────────────────────────┐
         │     SHARED KERNEL            │
         │  (Common primitives)         │
         │  - ValueObjects              │
         │  - Common Types              │
         │  - Datetime Utils            │
         └──────────────────────────────┘
```

### 2.2 Bounded Context Definitions

#### A. Monitoring Context
**Responsibility:** Monitor AWS resources, collect events, process alerts

**Domain Entities:**
- Event (monitoring event)
- Agent (deployed monitor)
- Alert (processed notification)
- MetricThreshold
- ResourceFilter

**Use Cases:**
- CollectEvent
- ProcessAlert
- DeployAgent
- UpdateAgentStatus
- QueryEventHistory
- GenerateReport

**Owns:** Event data collection and alert processing

---

#### B. Task Management Context
**Responsibility:** Manage work items, track progress, collaborate

**Domain Entities:**
- Task
- TaskComment
- TaskAssignment
- TaskStatusHistory
- Workflow

**Use Cases:**
- CreateTask
- UpdateTaskStatus
- AssignTask
- AddComment
- CloseTask
- GetMyTasks

**Depends on:** Event ID from Monitoring Context (not the full Event entity)

---

#### C. Identity & Access Management (IAM) Context
**Responsibility:** Authenticate users, authorize actions, manage permissions

**Domain Entities:**
- User
- Role
- Permission
- Session
- RefreshToken

**Use Cases:**
- Login
- Logout
- GetProfile
- RefreshToken
- CreateUser
- UpdateUserRole
- CheckPermission

**Owns:** All user authentication and authorization

---

#### D. Configuration Context
**Responsibility:** Configure AWS accounts, monitoring settings, system parameters

**Domain Entities:**
- AwsAccount
- MonitoringConfig
- ServiceConfig
- NotificationSettings

**Use Cases:**
- RegisterAwsAccount
- TestConnection
- UpdateMonitoringConfig
- EnableService
- ConfigureThresholds

**Owns:** All system and monitoring configuration

---

## 3. Handling Shared Entities (The Event Problem)

### Problem
Event is used by both:
- **Monitoring Context** (creates and owns events)
- **Task Management Context** (references events when creating tasks)

### Solution Options

#### Option 1: Shared Kernel (Recommended for your case)

Create a shared kernel with minimal, stable entities that multiple contexts depend on.

```
backend/src/
├── shared_kernel/           # Shared across contexts
│   ├── primitives/
│   │   ├── event_id.py     # Value object for Event ID
│   │   ├── user_id.py      # Value object for User ID
│   │   └── timestamps.py   # Common timestamp utilities
│   ├── types/
│   │   ├── severity.py     # Severity enum
│   │   └── status.py       # Common status enums
│   └── utils/
│       └── datetime_utils.py
│
└── domain/
    ├── monitoring/          # Monitoring Context
    │   ├── models/
    │   │   ├── event.py    # Full Event entity (owns it)
    │   │   └── agent.py
    │   ├── use_cases/
    │   └── ports/
    │
    ├── task_management/     # Task Management Context
    │   ├── models/
    │   │   ├── task.py
    │   │   │   # References EventId, not full Event
    │   │   │   # Stores minimal event metadata
    │   │   └── comment.py
    │   ├── use_cases/
    │   └── ports/
    │
    ├── iam/                 # IAM Context
    │   ├── models/
    │   │   └── user.py
    │   ├── use_cases/
    │   └── ports/
    │
    └── configuration/       # Configuration Context
        ├── models/
        ├── use_cases/
        └── ports/
```

**How Task references Event:**

```python
# shared_kernel/primitives/event_id.py
class EventId(BaseModel):
    value: str

    @property
    def persistence_id(self) -> str:
        return self.value

# domain/task_management/models/task.py
from shared_kernel.primitives import EventId, Severity

class Task(BaseModel):
    id: str
    title: str

    # Reference to event (not full event)
    source_event_id: EventId | None = None

    # Denormalized snapshot of event data (at creation time)
    event_snapshot: dict | None = None
    # {
    #   "account": "123456789012",
    #   "region": "us-east-1",
    #   "source": "aws.guardduty",
    #   "severity": "critical",
    #   "detail_type": "GuardDuty Finding"
    # }
```

**Benefits:**
- ✅ Task context doesn't depend on full Event entity
- ✅ Loose coupling via EventId value object
- ✅ Event data snapshot prevents queries across contexts
- ✅ Monitoring context can evolve Event without breaking Task

---

#### Option 2: Anti-Corruption Layer (ACL)

Each context has its own model of Event, translated at the boundary.

```
domain/
├── monitoring/
│   └── models/
│       └── event.py        # Full monitoring event
│
└── task_management/
    ├── models/
    │   ├── task.py
    │   └── source_event.py  # Task's view of an event
    │
    └── adapters/
        └── event_translator.py  # Translates Monitoring.Event → Task.SourceEvent
```

**Translation at boundary:**

```python
# domain/task_management/adapters/event_translator.py
from domain.monitoring.models import Event as MonitoringEvent
from domain.task_management.models import SourceEvent

class EventTranslator:
    @staticmethod
    def to_source_event(monitoring_event: MonitoringEvent) -> SourceEvent:
        """
        Translate Monitoring Context's Event to Task Context's SourceEvent.
        This protects Task context from changes in Monitoring context.
        """
        return SourceEvent(
            event_id=monitoring_event.id,
            account=monitoring_event.account,
            region=monitoring_event.region,
            source=monitoring_event.source,
            severity=monitoring_event.severity,
            detail_type=monitoring_event.detail_type,
            occurred_at=monitoring_event.published_at
        )
```

**Benefits:**
- ✅ Complete isolation between contexts
- ✅ Each context has its own ubiquitous language
- ✅ Changes in one context don't affect others
- ❌ More code (translation layers)
- ❌ Potential for desynchronization

---

#### Option 3: Domain Events (Event-Driven)

Contexts communicate via domain events (messages), not shared entities.

```
Monitoring Context              Task Management Context
      │                                  │
      │  EventOccurred                   │
      │  (domain event)                  │
      ├──────────────────────────────────>
      │                                  │
      │                         CreateTaskFromEvent
      │                              (use case)
```

**Implementation:**

```python
# shared_kernel/events/domain_events.py
class DomainEvent(BaseModel):
    event_id: str
    occurred_at: int

class EventOccurred(DomainEvent):
    """Published when a monitoring event is created."""
    account: str
    region: str
    source: str
    severity: Severity
    detail_type: str
    # Minimal data, not full event

# domain/monitoring/use_cases/collect_event.py
class CollectEvent:
    def execute(self, event_data: dict):
        event = Event.from_dict(event_data)
        self.event_repository.save(event)

        # Publish domain event
        self.event_bus.publish(
            EventOccurred(
                event_id=event.id,
                account=event.account,
                region=event.region,
                source=event.source,
                severity=event.severity,
                detail_type=event.detail_type,
                occurred_at=event.published_at
            )
        )

# domain/task_management/event_handlers/event_occurred_handler.py
class EventOccurredHandler:
    def handle(self, event: EventOccurred):
        # Auto-create task for critical events
        if event.severity == Severity.CRITICAL:
            self.create_task_use_case.execute(
                CreateTaskDTO(
                    title=f"Critical Event: {event.detail_type}",
                    source_event_id=event.event_id,
                    event_snapshot={
                        "account": event.account,
                        "severity": event.severity,
                        ...
                    }
                )
            )
```

**Benefits:**
- ✅ Completely decoupled contexts
- ✅ Asynchronous communication
- ✅ Easy to add new contexts that react to events
- ✅ Event sourcing possible
- ❌ Increased complexity
- ❌ Eventual consistency

---

## 4. Recommended Approach for Your System

### Hybrid Strategy

Use a combination based on relationship type:

```
┌────────────────────────────────────────────────────────────────┐
│                      RELATIONSHIP TYPES                         │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Shared Kernel (Shared primitives)                             │
│  ├─ EventId, UserId, TaskId (value objects)                    │
│  ├─ Severity, Status enums                                     │
│  └─ Datetime utilities                                         │
│                                                                 │
│  Anti-Corruption Layer (Different views)                       │
│  ├─ Task's view of Event (SourceEvent)                         │
│  ├─ Monitoring's view of User (EventOwner)                     │
│  └─ Translation at context boundaries                          │
│                                                                 │
│  Domain Events (Async communication)                           │
│  ├─ EventOccurred → triggers task creation                     │
│  ├─ TaskCompleted → updates monitoring stats                   │
│  └─ UserCreated → initialize user preferences                  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Applied to Your System

**1. Event Reference in Task (Use Shared Kernel + Snapshot)**

```python
# Task stores EventId (shared kernel) + denormalized snapshot
class Task(BaseModel):
    source_event_id: EventId | None
    event_snapshot: dict | None  # Frozen at task creation
```

**2. User Reference in Task (Use UserId + Denormalization)**

```python
# Task stores UserId (shared kernel) + user name
class Task(BaseModel):
    assigned_user_id: UserId
    assigned_user_name: str  # Denormalized, may become stale
```

**3. Cross-Context Queries (Use Repository Facades)**

```python
# Application layer orchestrates across contexts
class TaskApplicationService:
    def get_task_with_event(self, task_id: str):
        # Get task from Task Management context
        task = self.task_repository.get(task_id)

        # Get event from Monitoring context (if linked)
        event = None
        if task.source_event_id:
            event = self.event_repository.get(task.source_event_id.value)

        # Combine for presentation
        return TaskDetailDTO(
            task=task,
            source_event=event
        )
```

---

## 5. New Directory Structure

```
backend/src/
│
├── shared_kernel/                    # Shared primitives
│   ├── __init__.py
│   ├── primitives/
│   │   ├── __init__.py
│   │   ├── event_id.py              # Value object
│   │   ├── user_id.py               # Value object
│   │   ├── task_id.py               # Value object
│   │   └── account_id.py            # Value object
│   ├── types/
│   │   ├── __init__.py
│   │   ├── severity.py              # Shared enum
│   │   └── pagination.py            # Shared pagination types
│   └── utils/
│       ├── __init__.py
│       └── datetime_utils.py
│
├── domain/                           # Bounded contexts
│   │
│   ├── monitoring/                   # MONITORING CONTEXT
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── event.py             # Owns Event entity
│   │   │   ├── agent.py
│   │   │   └── alert.py
│   │   ├── use_cases/
│   │   │   ├── __init__.py
│   │   │   ├── collect_event.py
│   │   │   ├── process_alert.py
│   │   │   └── query_events.py
│   │   ├── ports/
│   │   │   ├── repositories/
│   │   │   │   ├── event_repository.py
│   │   │   │   └── agent_repository.py
│   │   │   └── services/
│   │   │       └── alert_service.py
│   │   └── events/                   # Domain events published
│   │       ├── event_occurred.py
│   │       └── agent_deployed.py
│   │
│   ├── task_management/              # TASK MANAGEMENT CONTEXT
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── task.py              # References EventId
│   │   │   ├── comment.py
│   │   │   └── source_event.py      # Task's view of event
│   │   ├── use_cases/
│   │   │   ├── __init__.py
│   │   │   ├── create_task.py
│   │   │   ├── update_task.py
│   │   │   └── add_comment.py
│   │   ├── ports/
│   │   │   ├── repositories/
│   │   │   │   ├── task_repository.py
│   │   │   │   └── comment_repository.py
│   │   │   └── services/
│   │   ├── adapters/                 # Anti-corruption layer
│   │   │   └── event_translator.py
│   │   └── event_handlers/           # Domain event handlers
│   │       └── event_occurred_handler.py
│   │
│   ├── iam/                          # IAM CONTEXT
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py              # Owns User entity
│   │   │   ├── role.py
│   │   │   └── session.py
│   │   ├── use_cases/
│   │   │   ├── __init__.py
│   │   │   ├── authenticate.py
│   │   │   ├── authorize.py
│   │   │   └── manage_user.py
│   │   ├── ports/
│   │   │   ├── repositories/
│   │   │   │   └── user_repository.py
│   │   │   └── services/
│   │   │       ├── jwt_service.py
│   │   │       └── password_service.py
│   │   └── events/
│   │       ├── user_created.py
│   │       └── user_logged_in.py
│   │
│   └── configuration/                # CONFIGURATION CONTEXT
│       ├── __init__.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── aws_account.py
│       │   └── monitoring_config.py
│       ├── use_cases/
│       │   ├── __init__.py
│       │   ├── register_account.py
│       │   └── update_config.py
│       ├── ports/
│       │   ├── repositories/
│       │   │   └── config_repository.py
│       │   └── services/
│       │       └── aws_connection_service.py
│       └── events/
│           └── account_registered.py
│
├── application/                      # Application services
│   ├── __init__.py
│   ├── task_app_service.py          # Orchestrates across contexts
│   ├── monitoring_app_service.py
│   └── event_bus.py                 # Domain event dispatcher
│
├── adapters/                         # Infrastructure (unchanged structure)
│   ├── db/
│   │   ├── models/                  # Persistence models (all contexts)
│   │   ├── mappers/                 # Persistence mappers
│   │   └── repositories/            # Repository implementations
│   └── services/                    # External service adapters
│
└── entrypoints/                      # API handlers (unchanged structure)
    └── apigw/
```

---

## 6. Dependency Rules

### Context Independence Rule

```
✅ ALLOWED:
Monitoring → Shared Kernel
Task Mgmt  → Shared Kernel
IAM        → Shared Kernel

❌ FORBIDDEN:
Task Mgmt → Monitoring (direct dependency)
Monitoring → Task Mgmt
IAM → Task Mgmt
```

### Communication Patterns

```
Context A needs data from Context B:

Option 1: Application Service orchestration
  Application Service → Context A Repository
                     → Context B Repository
                     → Combine results

Option 2: Domain Events
  Context A → Publish Event → Event Bus → Context B Handler

Option 3: Anti-Corruption Layer
  Context A → ACL Translator → Context B (translated view)
```

---

## 7. Migration Strategy

### Phase 1: Identify Context Boundaries (Week 1)
- Map existing models to contexts
- Identify shared entities
- Define context responsibilities
- Document context map

### Phase 2: Create Shared Kernel (Week 2)
- Extract value objects (EventId, UserId, etc.)
- Extract common enums (Severity, etc.)
- Extract utilities (datetime_utils)
- No breaking changes yet

### Phase 3: Reorganize File Structure (Week 3)
- Create new directory structure
- Move files into contexts
- Update imports
- Tests should still pass

### Phase 4: Introduce Anti-Corruption Layers (Week 4-5)
- Create context-specific models for shared entities
- Add translators at boundaries
- Update use cases to use translated models

### Phase 5: Implement Domain Events (Week 6-7)
- Create event bus
- Define domain events
- Add event handlers
- Migrate cross-context calls to events

### Phase 6: Cleanup and Documentation (Week 8)
- Remove old dependencies
- Update documentation
- Add context diagrams
- Train team

---

## 8. Testing Strategy

### Unit Tests (Isolated Contexts)
```python
# test/unit/domain/monitoring/test_collect_event.py
def test_collect_event_use_case():
    # Test monitoring context in isolation
    use_case = CollectEvent(mock_repository)
    result = use_case.execute(event_data)
    assert result.success
```

### Integration Tests (Cross-Context)
```python
# test/integration/test_task_from_event.py
def test_create_task_from_critical_event():
    # Test interaction between contexts
    # 1. Create event in Monitoring context
    # 2. Verify domain event published
    # 3. Verify task created in Task Management context
    pass
```

### Context Map Tests
```python
# test/architecture/test_context_dependencies.py
def test_no_forbidden_dependencies():
    # Ensure contexts only depend on allowed modules
    # Use import analysis tools
    pass
```

---

## 9. Key Benefits

### Before (Monolithic Domain)
- ❌ 50+ models in one directory
- ❌ Unclear ownership
- ❌ Tight coupling via shared entities
- ❌ Hard to understand business boundaries
- ❌ Risky refactoring

### After (Bounded Contexts)
- ✅ 4 clear contexts with ~10-15 models each
- ✅ Clear ownership per context
- ✅ Loose coupling via events and value objects
- ✅ Business boundaries explicit
- ✅ Safe refactoring within context
- ✅ Can assign teams to contexts
- ✅ Easier to reason about
- ✅ Scalable to microservices later

---

## 10. Context Map Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CONTEXT MAP                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐                 ┌──────────────┐              │
│  │ Monitoring   │◄────────────────┤     IAM      │              │
│  │   Context    │   Conformist    │   Context    │              │
│  │              │   (uses UserId)  │              │              │
│  └───────┬──────┘                 └──────┬───────┘              │
│          │                                │                      │
│          │ Publisher                      │ Publisher            │
│          │ (EventOccurred)                │ (UserCreated)        │
│          │                                │                      │
│          │        ┌──────────────┐        │                      │
│          └───────>│  Event Bus   │<───────┘                      │
│                   │  (Mediator)  │                               │
│                   └──────┬───────┘                               │
│                          │ Subscriber                            │
│                          │                                       │
│                   ┌──────▼──────┐                                │
│                   │ Task Mgmt   │                                │
│                   │  Context    │                                │
│                   │             │                                │
│                   └─────────────┘                                │
│                                                                  │
│  ┌──────────────┐                                                │
│  │Configuration │◄───────────────────────────────────────────┐  │
│  │   Context    │  Customer-Supplier                         │  │
│  │              │  (provides AWS accounts to all)            │  │
│  └──────────────┘                                            │  │
│         │                                                     │  │
│         └─────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────┐       │
│  │             SHARED KERNEL                             │       │
│  │  (EventId, UserId, Severity, Pagination, Utils)       │       │
│  │  - All contexts depend on this                        │       │
│  │  - Evolves with consensus                             │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Relationship Types:
- Shared Kernel: Shared primitives and utilities
- Publisher-Subscriber: Domain events via event bus
- Customer-Supplier: One context provides service to others
- Conformist: One context conforms to other's model (uses value objects)
- Anti-Corruption Layer: Translation at boundary (not shown)
```

---

## 11. Decision Matrix: When to Use Each Pattern

| Scenario | Shared Kernel | Anti-Corruption Layer | Domain Events |
|----------|--------------|----------------------|---------------|
| Simple value objects (IDs) | ✅ Best | ❌ Overkill | ❌ Not applicable |
| Complex shared entities | ❌ Tight coupling | ✅ Best | ⚠️ Consider |
| Cross-context reactions | ❌ Wrong tool | ❌ Wrong tool | ✅ Best |
| Reference data lookup | ✅ Good | ⚠️ Consider | ❌ Async issues |
| Synchronized writes | ⚠️ Consider | ⚠️ Consider | ✅ Best |
| Read-heavy operations | ✅ Good (denormalize) | ✅ Good | ❌ Eventual consistency |

---

## 12. Conclusion

### Recommended Strategy for Your System

1. **Use Shared Kernel** for:
   - EventId, UserId, TaskId (value objects)
   - Severity, Status enums
   - Common utilities (datetime)

2. **Use Denormalization** for:
   - User names in tasks (snapshot at creation)
   - Event metadata in tasks (frozen view)

3. **Use Domain Events** for:
   - Critical event → auto-create task
   - Task completion → update monitoring stats
   - Cross-context notifications

4. **Use Anti-Corruption Layer** for:
   - Complex entities with different views
   - When you want complete isolation

### Next Steps

1. ✅ **Review this architecture** with your team
2. ✅ **Map current models to contexts** (create context map)
3. ✅ **Start with Shared Kernel** (extract value objects)
4. ✅ **Gradually reorganize** (one context at a time)
5. ✅ **Add domain events** (event bus infrastructure)
6. ✅ **Document context boundaries** (update README)

This approach will make your domain layer:
- **More maintainable** - Clear boundaries
- **More scalable** - Independent contexts
- **More testable** - Isolated units
- **More evolvable** - Safe refactoring
- **Team-friendly** - Clear ownership

---

**Last Updated:** 2025-11-20
**Status:** Architectural Guidance - Ready for Discussion

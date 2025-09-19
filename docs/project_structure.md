# Layer Structure

The codebase follows a hexagonal architecture (ports and adapters) pattern with clear separation of concerns across multiple layers:

## Entry Points Layer (`src/entrypoints/`)

- **Functions**: Lambda function handlers for business operations
  - `HandleMonitoringEvents`, `QueryErrorLogs`, `DailyReport`, `UpdateDeployment`
- **API Gateway**: REST API endpoints for agents and events
- Minimal business logic, primarily input validation and response formatting
- Delegates to domain use cases for business logic execution

## Domain Layer (`src/domain/`)

- **Models**: Core business entities (Event, Agent) with domain logic and validation
- **Ports**: Interfaces defining contracts for external dependencies
  - Repository interfaces for data persistence
  - Notifier interfaces for external communications
  - Publisher interfaces for event publishing
  - Log query interfaces for external log systems
- **Use Cases**: Business logic orchestration and workflows
  - `daily_report`, `insert_monitoring_event`, `query_error_logs`, `update_deployment`

## Adapters Layer (`src/adapters/`)

- **Database** (`src/adapters/db/`): DynamoDB implementations
  - Models: Database-specific entity representations
  - Mappers: Convert between domain and database models
  - Repositories: Implement domain repository interfaces
- **AWS Services** (`src/adapters/aws/`): AWS service abstractions
  - CloudWatch, EventBridge, ECS, Lambda function adapters
- **External Services**: Implementation of domain ports
  - Notifiers (Slack, email, etc.)
  - Log adapters for CloudWatch
  - Event publishers for EventBridge

## Common Layer (`src/common/`)

- Shared utilities, configurations, and cross-cutting concerns
- Logger configuration, exception handling, utility functions
- Base models and common data structures
- Environment and application configuration

## Dependency Flow

```
entrypoints → domain (use_cases) → domain (ports) ← adapters
    ↓              ↓                    ↓              ↑
  common      domain (models)      common        common
```

**Key Principles:**
- Dependencies flow inward toward the domain layer
- Domain layer has no dependencies on external frameworks
- Adapters implement domain interfaces (dependency inversion)
- Entry points orchestrate use cases but contain no business logic
- Common utilities are used across all layers

# 📁 Folder structure

```
.
├── docs
├── infra               # Serverless Framework configuration split by stack (master/agent)
│   ├── master            # Master stack infrastructure
│   │   ├── configs          # Stage configurations
│   │   ├── functions        # Lambda functions
│   │   ├── plugins          # Serverless Framework plugins
│   │   └── resources        # CloudFormation templates
│   ├── agent             # Agent stack infrastructure
│   │   ├── configs
│   │   ├── plugins
│   │   └── resources
│   └── roles             # IAM roles and policies for deployment
├── ops
│   ├── deployment        # Deployment scripts (package, deploy, delete, etc.)
│   ├── development       # Development scripts (install, start, tests, etc.)
│   ├── local             # Local development scripts (LocalStack, Docker, etc.)
│   ├── postman           # Postman collections
│   └── base.sh
├── src
│   ├── adapters          # Implementation of domain ports (hexagonal architecture adapters)
│   │   ├── aws             # AWS service adapters
│   │   │   ├── cloudwatch.py
│   │   │   ├── data_classes.py
│   │   │   ├── ecs.py
│   │   │   ├── eventbridge.py
│   │   │   └── lambda_function.py
│   │   ├── db              # Database adapters implementing repository ports
│   │   │   ├── mappers       # Domain ↔ Database model conversion
│   │   │   │   ├── agent.py
│   │   │   │   ├── base.py
│   │   │   │   └── event.py
│   │   │   ├── models        # Database-specific entity representations
│   │   │   │   ├── agent.py
│   │   │   │   ├── base.py
│   │   │   │   └── event.py
│   │   │   └── repositories  # Repository pattern implementations
│   │   │       ├── agent.py
│   │   │       ├── base.py
│   │   │       └── event.py
│   │   ├── notifiers       # Notification service adapters (Slack, email, etc.)
│   │   │   ├── base.py
│   │   │   ├── events.py
│   │   │   └── report.py
│   │   ├── logs.py         # Log query adapter for CloudWatch
│   │   └── publisher.py    # Event publisher adapter for EventBridge
│   ├── common            # Shared utilities, configurations, and cross-cutting concerns
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── logger.py
│   │   ├── meta.py
│   │   ├── models.py
│   │   └── utils
│   │       ├── datetime_utils.py
│   │       ├── encoding.py
│   │       ├── objects.py
│   │       └── template.py
│   ├── domain            # Core business logic (hexagonal architecture core)
│   │   ├── models          # Business entities with domain logic
│   │   │   ├── agent.py
│   │   │   ├── base.py
│   │   │   └── event.py
│   │   ├── ports           # Interfaces/contracts for external dependencies
│   │   │   ├── logs.py       # Log query interfaces
│   │   │   ├── notifier.py   # Notification interfaces
│   │   │   ├── publisher.py  # Event publishing interfaces
│   │   │   └── repositories.py # Data persistence interfaces
│   │   └── use_cases       # Business logic orchestration
│   │       ├── daily_report.py
│   │       ├── insert_monitoring_event.py
│   │       ├── query_error_logs.py
│   │       └── update_deployment.py
│   └── entrypoints       # Application entry points (hexagonal architecture drivers)
│       ├── apigw           # API Gateway handlers
│       │   ├── agents
│       │   │   └── main.py
│       │   ├── base.py
│       │   ├── configs.py
│       │   └── events
│       │       └── main.py
│       └── functions       # Lambda function handlers
│           ├── daily_report
│           │   └── main.py
│           ├── handle_monitoring_events
│           │   └── main.py
│           ├── query_error_logs
│           │   └── main.py
│           └── update_deployment
│               └── main.py
├── tests
├── docker-compose.yaml
├── Makefile
├── package.json                        # Node.js dependencies
├── pyproject.toml                      # Python dependencies
├── README.md
├── serverless.agent.local.yml
├── serverless.master.local.yml
├── serverless.agent.yml                # Serverless Framework template for agent stack
└── serverless.master.yml               # Serverless Framework template for master stack
```

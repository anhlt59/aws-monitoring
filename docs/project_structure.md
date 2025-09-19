# Layer Structure

The codebase follows a hexagonal architecture pattern with clear separation of concerns across multiple layers:

## Presentation Layer (`src/entrypoints/`)

- Lambda function handlers that serve as entry points
- Process incoming events (EventBridge, API Gateway, scheduled events)
- Minimal business logic, primarily input validation and response formatting
- Examples: `HandleMonitoringEvents`, `QueryErrorLogs`, `DailyReport`

## Service Layer (`src/modules/*/services/`)

- Contains business logic and orchestrates data flow
- Coordinates between different components (repositories, notifiers, external APIs)
- Domain-specific services like `EventRepository`, `SlackClient`, notification services
- Handles complex workflows and business rules

## Infrastructure Layer (`src/infra/`)

- Abstracts external dependencies and technical concerns
- **AWS Services** (`src/infra/aws/`): CloudWatch, EventBridge, ECS, Lambda abstractions
- **Database** (`src/infra/db/`): DynamoDB models, repository pattern, data mapping
- Provides clean interfaces for external service interactions

## Domain Layer (`src/modules/*/models/`)

- Business entities and domain models (Event, Agent)
- Data transfer objects (DTOs) for API contracts
- Domain-specific validation and business rules
- Separated by business domain (master vs agent)

## Common Layer (`src/common/`)

- Shared utilities, configurations, and cross-cutting concerns
- Logger configuration, exception handling, utility functions
- Base models and common data structures
- Environment and application configuration

## Dependency Flow

```
entrypoints → Services → Repositories → Infrastructure
    ↓         ↓           ↓
  Models ← Models ← Models ← Common
```

- Dependencies flow inward (handlers depend on services, services on repositories)
- Common utilities are used across all layers
- Infrastructure layer handles all external system interactions

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
│   ├── common            # Shared utilities, configurations, and cross-cutting concerns
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── logger.py
│   │   ├── meta.py
│   │   ├── models.py
│   │   └── utils
│   ├── entrypoints
│   │   ├── apigw           # API Gateway handlers
│   │   └── functions       # Lambda function handlers
│   ├── infra             # Abstracts external dependencies and technical concerns
│   │   ├── aws             # AWS service abstractions
│   │   │   ├── cloudwatch.py
│   │   │   ├── data_classes.py
│   │   │   ├── ecs.py
│   │   │   ├── eventbridge.py
│   │   │   └── lambda_function.py
│   │   └── db              # Database models and repository patterns
│   │       ├── mapper
│   │       ├── models
│   │       └── repository
│   └── modules
│       ├── agent           # Deployed to each monitored AWS account
│       │   └── services
│       │       ├── cloudwatch.py
│       │       └── publisher.py
│       └── master          # Central monitoring system
│           ├── models        # Business entities and domain models
│           │   ├── agent.py
│           │   ├── base.py
│           │   └── event.py
│           ├── services
│           │   ├── api.py        # API Gateway interactions
│           │   ├── notifiers     # Notification services (e.g., Slack)
│           │   └── repositories  # Database interaction services
│           │       ├── agent.py
│           │       ├── event.py
│           │       └── mappers
│           │           ├── agent.py
│           │           └── event.py
│           └── utils
│               └── template.py
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

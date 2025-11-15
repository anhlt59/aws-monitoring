# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository

## Rules

- At the end of each task, summarize what has been completed and what remains
- Follow hexagonal architecture principles: Domain → Ports → Adapters
- Maintain test coverage above 90%
- Use specific exception types, avoid broad `except Exception` handlers
- All new code must include type hints and Pydantic validation where applicable

## Commands

- `make install` - Install all dependencies (Python via Poetry, Node.js packages)
- `make activate` - Activate the Python virtual environment
- `make test` - Run tests with pytest (including coverage reporting)
- `make coverage` - Generate an HTML coverage report and update the README badge
- `make start` - Start the LocalStack container for local AWS services
- `make start-master` / `make start-agent` - Start the local serverless stacks
- `make deploy-local` - Deploy both master and agent stacks to LocalStack

## Tech Stack

- Backend: Python 3.13, Serverless Framework 4.x
- Database: DynamoDB (single-table design with PynamoDB ORM)
- Infrastructure: AWS (Lambda, API Gateway, EventBridge, SNS, S3, CloudWatch)
- Validation: Pydantic v2.11.0 with strict type safety
- Testing: Pytest, Coverage, Moto (AWS mocking)
- Local Development: LocalStack, Docker

## Architecture

This is a serverless AWS monitoring application built using hexagonal architecture (ports and adapters pattern) with clean separation of concerns:

### Core Architecture Layers

#### Domain Layer (`src/domain/`)
- **Models**: Core business entities (Event, Agent) with domain logic
- **Ports**: Interfaces defining contracts for external dependencies (repositories, notifiers, publishers)
- **Use Cases**: Business logic orchestration (daily_report, insert_monitoring_event, query_error_logs, update_deployment)

#### Adapters Layer (`src/adapters/`)
- **Database**: DynamoDB repositories, models, and mappers for data persistence
- **AWS Services**: CloudWatch, EventBridge, Lambda function abstractions
- **External Services**: Notifiers (Slack, etc.), log adapters, event publishers

#### Entry Points (`src/entrypoints/`)
- **Functions**: Lambda function handlers for business operations
- **API Gateway**: REST API endpoints for agents and events

#### Common Layer (`src/common/`)
- Shared utilities, configurations, logger, exceptions, and cross-cutting concerns

### Deployment Architecture

The application consists of two serverless stacks:

#### Master Stack
- Central monitoring system deployed once
- Processes monitoring events, sends notifications, provides APIs
- Lambda functions: HandleMonitoringEvents, UpdateDeployment, DailyReport
- API Gateway endpoints for agent management and event querying

#### Agent Stack
- Deployed to each monitored AWS account
- Queries CloudWatch logs and publishes events to master stack
- Lambda function: QueryErrorLogs

### Infrastructure (`infra/`)

- Serverless Framework configuration split by stack (master/agent) with environment-specific configs
- CloudFormation templates for IAM, EventBridge, DynamoDB, and SQS

## Development Best Practices

### Error Handling Pattern
```python
# ❌ AVOID: Broad exception handling
try:
    operation()
except Exception as err:
    raise InternalServerError(f"Error: {err}")

# ✅ PREFERRED: Specific exception types
try:
    operation()
except DoesNotExist as err:
    raise NotFoundError(f"Resource not found: {err}")
except PutError as err:
    raise UnprocessedError(f"Database error: {err}")
except Exception as err:
    logger.exception("Unexpected error")
    raise InternalServerError(f"Internal error: {err}")
```

### Repository Pattern Usage
- Base repository: `src/adapters/db/repositories/base.py`
- Use generic methods: `_get()`, `_query()`, `_create()`, `_update()`, `_delete()`
- Always use mappers to convert between domain and persistence models
- Example: `src/adapters/db/repositories/event.py`, `src/adapters/db/repositories/agent.py`

### Type Safety with Pydantic
```python
# All domain models use Pydantic v2
from pydantic import BaseModel, Field, field_validator

class Event(BaseModel):
    id: str
    account: str
    region: str | None = None
    detail: dict
    published_at: int = Field(default_factory=current_utc_timestamp)

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not value:
            raise ValueError("ID cannot be empty")
        return value
```

### Batch Processing Pattern
```python
# Use chunking utility for batch operations
from src.common.utils.objects import chunks

for chunk in chunks(log_groups, chunk_size=10):
    # Process in batches to avoid rate limits
    results = process_batch(chunk)
```

## Testing Guidelines

### Test Structure
- Test files mirror source structure in `tests/`
- Integration tests: `tests/integrations/`
- Adapter tests: `tests/adapters/`
- Test fixtures in `tests/conftest.py`
- Mock data in `tests/data/`

### Coverage Expectations
- Minimum: 88% overall coverage (current baseline)
- Target: >90% coverage for new features
- Critical paths: 100% coverage (repositories, use cases)

### Test Commands
```bash
# Run all tests with coverage
make test

# Run specific test file
poetry run pytest tests/integrations/api/test_events.py -v

# Generate HTML coverage report
make coverage

# Run tests with moto for AWS mocking
poetry run pytest tests/ --cov=src --cov-report=html
```

### AWS Service Mocking
- Use `moto` library for AWS service mocking
- Example: `tests/conftest.py` for DynamoDB table setup
- LocalStack for integration testing

## Performance Considerations

### CloudWatch Log Queries
- Current implementation: Synchronous polling with timeout (15s default)
- Location: `src/adapters/aws/cloudwatch.py:18-46`
- Chunk size: 10 log groups per query (configurable)
- Consideration: May timeout with large log volumes

### DynamoDB Access Patterns
- Single-table design with PynamoDB ORM
- Query optimization with GSI (Global Secondary Indexes)
- Cursor-based pagination for large result sets
- Location: `src/adapters/db/repositories/base.py`

### Batch Processing
- EventBridge publishing: Batched messages to reduce API calls
- CloudWatch queries: Chunked to 10 log groups (configurable)
- Location: `src/domain/use_cases/query_error_logs.py:45-66`

## Security Guidelines

### Secrets Management
- ✅ No hardcoded credentials in source code
- ✅ Webhook URLs loaded from environment variables (`src/common/constants.py:26-28`)
- ✅ AWS credentials managed by IAM roles (Lambda execution roles)

### Input Validation
- All API inputs validated with Pydantic models
- CloudWatch query strings validated: `src/domain/use_cases/query_error_logs.py:19-26`
- API Gateway validation enabled: `src/entrypoints/apigw/base.py:11`

### IAM Best Practices
- Least privilege principle documented: `docs/overview.md:216-221`
- Cross-account roles for EventBridge access
- Resource-based policies for DynamoDB and EventBridge

### Data Protection
- DynamoDB encryption at rest (AWS KMS)
- TLS 1.2+ for all API calls
- Log sanitization for PII (documented in overview)

## Common Tasks

### Adding a New Event Type
1. Define event model in `src/domain/models/`
2. Create mapper in `src/adapters/db/mappers/`
3. Update repository in `src/adapters/db/repositories/`
4. Add use case in `src/domain/use_cases/`
5. Create entrypoint handler in `src/entrypoints/functions/`
6. Update Serverless Framework config in `infra/`

### Adding a New Notifier
1. Create notifier class in `src/adapters/notifiers/`
2. Implement `INotifier` port from `src/domain/ports/notifier.py`
3. Add Jinja2 template in `statics/templates/`
4. Update use case to inject notifier

### Modifying DynamoDB Schema
1. Update domain model in `src/domain/models/`
2. Update persistence model in `src/adapters/db/models/`
3. Update mapper in `src/adapters/db/mappers/`
4. Update CloudFormation in `infra/master/resources/dynamodb.yml`
5. Write migration script if needed

## File Reference Guide

### Key Files by Function

**Error Handling**:
- Exception definitions: `src/common/exceptions.py`
- Repository error handling: `src/adapters/db/repositories/base.py:32-122`

**Configuration**:
- Environment variables: `src/common/constants.py`
- Serverless configs: `infra/master/configs/`, `infra/agent/configs/`

**Core Business Logic**:
- Event processing: `src/domain/use_cases/insert_monitoring_event.py`
- Log querying: `src/domain/use_cases/query_error_logs.py`
- Daily reports: `src/domain/use_cases/daily_report.py`

**AWS Service Adapters**:
- CloudWatch: `src/adapters/aws/cloudwatch.py`
- EventBridge: `src/adapters/aws/eventbridge.py`
- ECS: `src/adapters/aws/ecs.py`
- Lambda: `src/adapters/aws/lambda_function.py`

**Notification Templates**:
- Template directory: `statics/templates/`
- Template constants: `src/common/constants.py:31-37`

## Additional Instructions

### Backend Documentation
- Project structure: @docs/project_structure.md
- Database schema: @docs/db.md
- Architecture overview: @docs/overview.md
- Development guide: @docs/development.md
- Deployment guide: @docs/deployment.md

### Frontend Documentation
- Frontend overview: @docs/frontend-overview.md
- Frontend architecture: @docs/frontend-design.md
- TypeScript types reference: @docs/frontend-types-reference.md
- Implementation guide: @docs/frontend-implementation-guide.md
- Quick start guide: @docs/frontend-quick-start.md

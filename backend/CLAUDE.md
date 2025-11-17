# Backend Development Guide

This guide provides detailed instructions for working with the Python backend codebase.

## Tech Stack

- **Runtime**: Python 3.13
- **Framework**: Serverless Framework 4.x
- **Database**: DynamoDB (single-table design with PynamoDB ORM)
- **Infrastructure**: AWS Lambda, API Gateway, EventBridge, SNS, S3, CloudWatch
- **Validation**: Pydantic v2.11.0 with strict type safety
- **Testing**: Pytest, Coverage, Moto (AWS mocking)
- **Local Development**: LocalStack, Docker

## Architecture

The backend follows hexagonal architecture (ports and adapters pattern):

### Domain Layer (`src/domain/`)

**Core business logic with zero dependencies on external frameworks**

- **Models**: Business entities (Event, Agent) with domain logic
  - `event.py` - Event domain model with validation
  - `agent.py` - Agent domain model
  - `logs.py` - Log query result models
  - `messages.py` - Message templates
- **Ports**: Interfaces defining contracts for external dependencies
  - `repositories.py` - Data persistence interfaces
  - `notifier.py` - Notification interfaces
  - `publisher.py` - Event publishing interfaces
  - `logs.py` - Log query interfaces
- **Use Cases**: Business logic orchestration
  - `daily_report.py` - Generate daily monitoring reports
  - `insert_monitoring_event.py` - Process incoming events
  - `query_error_logs.py` - Query CloudWatch logs for errors
  - `update_deployment.py` - Handle deployment updates

### Adapters Layer (`src/adapters/`)

**Implementations of domain ports**

- **Database** (`src/adapters/db/`):
  - `models/` - DynamoDB-specific entity representations (PynamoDB)
  - `mappers/` - Convert between domain and database models
  - `repositories/` - Implement domain repository interfaces
- **AWS Services** (`src/adapters/aws/`):
  - `cloudwatch.py` - CloudWatch Logs Insights queries
  - `eventbridge.py` - Event publishing
  - `ecs.py` - ECS task management
  - `lambda_function.py` - Lambda invocations
- **External Services**:
  - `notifiers/` - Slack, email notifications
  - `logs.py` - CloudWatch log adapter
  - `publisher.py` - EventBridge publisher

### Entry Points (`src/entrypoints/`)

**Application entry points (Lambda handlers, API Gateway)**

- **Functions** (`src/entrypoints/functions/`):
  - Lambda handlers for business operations
  - Minimal logic, delegates to use cases
  - Dependency injection and error handling
- **API Gateway** (`src/entrypoints/apigw/`):
  - REST API endpoints for events and agents
  - Request validation and response formatting

### Common Layer (`src/common/`)

**Shared utilities and cross-cutting concerns**

- `constants.py` - Environment variables and configuration
- `exceptions.py` - Custom exception types
- `logger.py` - Structured logging setup
- `utils/` - Utility functions (datetime, encoding, objects, templates)

## Commands

### From Project Root

```bash
# Development
make install        # Install Python & Node.js dependencies
make test           # Run backend tests with coverage
make coverage       # Generate HTML coverage report
make start          # Start LocalStack and deploy backend
make deploy         # Deploy to environment (stage=local by default)
make mon            # Launch monitoring profile manager

# Deployment
make package        # Create deployment artifacts
make destroy        # Remove deployed stack
make bootstrap      # Prepare S3 buckets and IAM roles
```

### From Backend Directory

```bash
cd backend

# Testing
poetry run pytest tests/integrations/api/test_events.py -v
poetry run pytest tests/ --cov=src --cov-report=html

# Code Quality
poetry run mypy src/
poetry run ruff check src/ --fix

# Dependency Management
poetry install
poetry add <package>
poetry update
```

## Best Practices

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

```python
# Base repository provides generic methods
from src.adapters.db.repositories.base import BaseRepository
from src.adapters.db.models.event import EventModel
from src.adapters.db.mappers.event import EventMapper
from src.domain.models.event import Event

class EventRepository(BaseRepository[EventModel, Event]):
    def __init__(self):
        super().__init__(
            model_class=EventModel,
            mapper=EventMapper()
        )

    def get_by_id(self, event_id: str) -> Event:
        # Use base repository methods
        model = self._get(hash_key=event_id)
        return self.mapper.to_domain(model)
```

**Key principles**:
- Always use mappers to convert between domain and persistence models
- Use base repository methods: `_get()`, `_query()`, `_create()`, `_update()`, `_delete()`
- Handle exceptions at repository level and convert to domain exceptions

### Type Safety with Pydantic

```python
# All domain models use Pydantic v2
from pydantic import BaseModel, Field, field_validator
from src.common.utils.datetime_utils import current_utc_timestamp

class Event(BaseModel):
    id: str
    account: str
    region: str | None = None
    detail: dict
    detail_type: str
    severity: str
    published_at: int = Field(default_factory=current_utc_timestamp)

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not value:
            raise ValueError("ID cannot be empty")
        return value

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: str) -> str:
        allowed = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        if value.upper() not in allowed:
            raise ValueError(f"Severity must be one of {allowed}")
        return value.upper()
```

### Batch Processing Pattern

```python
# Use chunking utility for batch operations
from src.common.utils.objects import chunks

log_groups = ["group1", "group2", "group3", ...]

# Process in batches to avoid rate limits
for chunk in chunks(log_groups, chunk_size=10):
    results = cloudwatch_client.query_logs(chunk)
    process_results(results)
```

### Dependency Injection Pattern

```python
# Use cases should receive dependencies via constructor
from src.domain.ports.repositories import IEventRepository
from src.domain.ports.notifier import INotifier

class InsertMonitoringEvent:
    def __init__(
        self,
        event_repository: IEventRepository,
        notifier: INotifier
    ):
        self.event_repository = event_repository
        self.notifier = notifier

    def execute(self, event_data: dict) -> Event:
        # Validate and create domain model
        event = Event(**event_data)

        # Persist to database
        saved_event = self.event_repository.create(event)

        # Send notification
        self.notifier.send_event_notification(saved_event)

        return saved_event
```

## Testing

### Test Structure

```
backend/tests/
├── adapters/           # Adapter tests
│   └── repositories/   # Repository tests with moto
├── integrations/       # Integration tests
│   ├── api/           # API Gateway tests
│   └── functions/     # Lambda function tests
├── data/              # Mock event data (JSON)
├── conftest.py        # Pytest fixtures
└── mock.py            # Mock utilities
```

### Coverage Expectations

- **Minimum**: 88% overall coverage (current baseline)
- **Target**: >90% coverage for new features
- **Critical paths**: 100% coverage (repositories, use cases)

### Test Examples

```python
# tests/adapters/repositories/test_event.py
import pytest
from moto import mock_aws
from src.adapters.db.repositories.event import EventRepository
from src.domain.models.event import Event

@mock_aws
def test_create_event():
    # Arrange
    repo = EventRepository()
    event = Event(
        id="test-123",
        account="000000000000",
        detail_type="CloudWatch Alarm",
        severity="HIGH",
        detail={"AlarmName": "Test"}
    )

    # Act
    saved_event = repo.create(event)

    # Assert
    assert saved_event.id == event.id
    assert saved_event.account == event.account

    # Verify persistence
    retrieved = repo.get_by_id("test-123")
    assert retrieved.id == "test-123"
```

### AWS Service Mocking

```python
# Use moto for AWS service mocking
from moto import mock_aws
import boto3

@mock_aws
def test_cloudwatch_query():
    # Setup mock CloudWatch
    logs_client = boto3.client("logs", region_name="us-east-1")
    logs_client.create_log_group(logGroupName="/aws/lambda/test")

    # Your test code
    from src.adapters.aws.cloudwatch import CloudWatchAdapter
    adapter = CloudWatchAdapter()
    results = adapter.query_logs(["/aws/lambda/test"], "ERROR")

    assert results is not None
```

## File Reference

### Error Handling
- Exception definitions: `src/common/exceptions.py`
- Repository error handling: `src/adapters/db/repositories/base.py`

### Configuration
- Environment variables: `src/common/constants.py`
- Serverless configs: `../infra/configs/`
- Local environment: `.env.local`

### Core Business Logic
- Event processing: `src/domain/use_cases/insert_monitoring_event.py`
- Log querying: `src/domain/use_cases/query_error_logs.py`
- Daily reports: `src/domain/use_cases/daily_report.py`
- Deployment updates: `src/domain/use_cases/update_deployment.py`

### AWS Service Adapters
- CloudWatch: `src/adapters/aws/cloudwatch.py`
- EventBridge: `src/adapters/aws/eventbridge.py`
- ECS: `src/adapters/aws/ecs.py`
- Lambda: `src/adapters/aws/lambda_function.py`

### Notification Templates
- Template directory: `statics/templates/`
- Template constants: `src/common/constants.py`

## Common Development Tasks

### Adding a New Event Type

1. **Define domain model** in `src/domain/models/`
   ```python
   # src/domain/models/custom_event.py
   from pydantic import BaseModel

   class CustomEvent(BaseModel):
       id: str
       custom_field: str
   ```

2. **Create database model** in `src/adapters/db/models/`
   ```python
   # src/adapters/db/models/custom_event.py
   from pynamodb.models import Model
   from pynamodb.attributes import UnicodeAttribute

   class CustomEventModel(Model):
       class Meta:
           table_name = "monitoring-events"

       id = UnicodeAttribute(hash_key=True)
       custom_field = UnicodeAttribute()
   ```

3. **Create mapper** in `src/adapters/db/mappers/`
4. **Update repository** in `src/adapters/db/repositories/`
5. **Add use case** in `src/domain/use_cases/`
6. **Create entrypoint handler** in `src/entrypoints/functions/`
7. **Update Serverless config** in `../infra/functions/`

### Adding a New Notifier

1. **Create notifier class** in `src/adapters/notifiers/`
   ```python
   # src/adapters/notifiers/custom_notifier.py
   from src.domain.ports.notifier import INotifier
   from src.domain.models.event import Event

   class CustomNotifier(INotifier):
       def send_event_notification(self, event: Event) -> None:
           # Implementation
           pass
   ```

2. **Implement `INotifier` port** from `src/domain/ports/notifier.py`
3. **Add Jinja2 template** in `statics/templates/`
4. **Update use case** to inject notifier
5. **Add configuration** in `src/common/constants.py`

### Modifying DynamoDB Schema

1. **Update domain model** in `src/domain/models/`
2. **Update persistence model** in `src/adapters/db/models/`
3. **Update mapper** in `src/adapters/db/mappers/`
4. **Update CloudFormation** in `../infra/resources/dynamodb.yml`
5. **Write migration script** if needed (in `ops/pyscripts/`)

### Adding a New Lambda Function

1. **Create handler** in `src/entrypoints/functions/`
2. **Define function config** in `../infra/functions/`
3. **Add IAM permissions** in `../infra/resources/iam.yml`
4. **Reference in serverless.yml**
5. **Write integration test** in `tests/integrations/functions/`

## Security Guidelines

- ✅ No hardcoded credentials in source code
- ✅ Webhook URLs loaded from environment variables
- ✅ AWS credentials managed by IAM roles
- ✅ All API inputs validated with Pydantic models
- ✅ DynamoDB encryption at rest (AWS KMS)
- ✅ TLS 1.2+ for all API calls
- ✅ Principle of least privilege for IAM roles
- ✅ Secrets rotation via AWS Secrets Manager

## Performance Considerations

### CloudWatch Log Queries
- Chunked to 10 log groups per query (configurable)
- Synchronous polling with 15s timeout default
- Consider timeout with large log volumes
- Location: `src/adapters/aws/cloudwatch.py`

### DynamoDB Access Patterns
- Single-table design with PynamoDB ORM
- Query optimization with GSI (Global Secondary Indexes)
- Cursor-based pagination for large result sets
- Batch operations where possible
- Location: `src/adapters/db/repositories/base.py`

### Lambda Optimization
- Minimize dependencies in handlers
- Use Lambda layers for common dependencies
- Connection pooling for external services
- Cold start optimization (keep handlers thin)

### Batch Processing
- EventBridge publishing: Batched messages
- CloudWatch queries: Chunked to avoid rate limits
- DynamoDB batch operations for bulk writes
- Location: `src/domain/use_cases/query_error_logs.py`

## Troubleshooting

### Poetry Issues
**Problem**: Virtual environment not found or corrupted
```bash
# Solution
rm -rf .venv
cd .. && make install
```

### LocalStack Issues
**Problem**: LocalStack container not starting
```bash
# Check Docker is running
docker ps

# Restart LocalStack
docker compose restart localstack

# Check logs
docker logs -f localstack
```

### Import Errors
**Problem**: Module not found errors
```bash
# Ensure virtual environment is activated
cd backend
poetry shell

# Or run with poetry
poetry run python -m src.entrypoints.functions.handle_monitoring_events.main
```

### Test Failures
**Problem**: Integration tests failing
```bash
# Ensure LocalStack is running
docker ps | grep localstack

# Check DynamoDB table exists
aws dynamodb list-tables --endpoint-url=http://localhost:4566 --region us-east-1

# Run tests with verbose output
poetry run pytest tests/integrations/ -v -s
```

### DynamoDB Connection Issues
**Problem**: Cannot connect to DynamoDB
```bash
# Check LocalStack endpoint
echo $LOCALSTACK_ENDPOINT  # Should be http://localhost:4566

# Verify table exists
aws dynamodb describe-table \
  --table-name monitoring-local \
  --endpoint-url=http://localhost:4566 \
  --region us-east-1
```

## Environment Setup

### Required Environment Variables

Located in `backend/.env.local`:
```bash
# Logging
POWERTOOLS_LOG_LEVEL=DEBUG

# Notifications
MONITORING_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Database
DYNAMODB_TABLE=monitoring-local

# AWS (for local development)
AWS_DEFAULT_REGION=us-east-1
```

### Python Version

Ensure Python 3.13 is installed:
```bash
python3.13 --version
# Python 3.13.x

# If not installed (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3.13 python3.13-venv
```

### Poetry Setup

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Configure Poetry to create virtualenvs in project
poetry config virtualenvs.in-project true

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

## Additional Resources

- Main documentation: `../docs/`
- Project structure: `../docs/project_structure.md`
- Database schema: `../docs/db.md`
- Architecture overview: `../docs/overview.md`
- Deployment guide: `../docs/deployment.md`

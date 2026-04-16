# Code Standards & Development Guidelines

## 📋 Overview

This document outlines the coding standards, architectural patterns, and development guidelines for the AWS Monitoring project. These standards ensure code quality, maintainability, and consistency across the entire codebase.

## 🏗️ Architectural Patterns

### Hexagonal Architecture (Ports and Adapters)

The codebase follows hexagonal architecture principles to achieve clean separation of concerns and testability.

#### Core Principles

1. **Domain-Centric Design**
   - Business logic resides in the domain layer
   - External dependencies are abstracted through ports
   - No direct dependencies on external frameworks

2. **Dependency Inversion**
   - High-level modules depend on abstractions
   - Low-level modules depend on abstractions
   - Concrete implementations depend on abstractions

3. **Separation of Concerns**
   - Each layer has distinct responsibilities
   - Clear interfaces between layers
   - Minimal coupling between components

#### Layer Responsibilities

| Layer | Responsibility | Key Components |
|-------|----------------|----------------|
| **Domain** | Business logic and rules | Models, Use Cases, Ports |
| **Adapters** | External integrations | Repositories, Services, APIs |
| **Entry Points** | Application interface | Lambda handlers, API endpoints |
| **Common** | Shared utilities | Configuration, Logging, Utils |

### Clean Architecture Implementation

#### Dependency Rules

```
Entry Points → Domain → Adapters → External Services
```

- **Entry Points** depend only on Domain and Common layers
- **Domain** layer has no external dependencies
- **Adapters** implement Domain interfaces and handle external services
- **Common** utilities are used across all layers

### Design Patterns Used

#### Repository Pattern
- **Purpose**: Abstract data access operations
- **Implementation**: Interface-based with concrete implementations
- **Benefits**: Testability, flexibility, and separation of concerns
- **Usage**: All data access operations through repositories

#### Adapter Pattern
- **Purpose**: Convert interfaces to match expected contracts
- **Implementation**: Port interface implementations
- **Benefits**: Integration flexibility and testability
- **Usage**: AWS service integrations, database access, notifications

#### Publisher-Subscriber Pattern
- **Purpose**: Decoupled event-driven communication
- **Implementation**: EventBridge integration
- **Benefits**: Scalability, resilience, and loose coupling
- **Usage**: Event processing and notification systems

#### Strategy Pattern
- **Purpose**: Algorithm encapsulation and runtime selection
- **Implementation**: Service interfaces with multiple implementations
- **Benefits**: Flexibility and extensibility
- **Usage**: Different notification channels, query strategies

#### Factory Pattern
- **Purpose**: Object creation encapsulation
- **Implementation**: Factory classes for complex object creation
- **Benefits**: Creation logic centralization and flexibility
- **Usage**: Service instantiation, model creation

## 📝 Coding Conventions

### Python Coding Standards

#### General Guidelines

- **PEP 8 Compliance**: Follow Python Enhancement Proposal 8 guidelines
- **Line Length**: Maximum 88 characters per line
- **Indentation**: 4 spaces per level
- **Quotes**: Use double quotes for strings, single quotes for constants
- **Naming**: Follow PEP 8 naming conventions

#### Variable Naming

```python
# Snake_case for variables and functions
event_processor = EventProcessor()
query_duration = 300
max_retries = 3

# PascalCase for classes and exceptions
class EventProcessor:
    class ProcessingError(Exception):
        pass

# UPPER_CASE for constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
```

#### Function and Method Definitions

```python
def process_monitoring_event(
    event_data: dict, 
    max_retries: int = 3
) -> dict:
    """Process a monitoring event with retry logic.
    
    Args:
        event_data: Raw event data from EventBridge
        max_retries: Maximum number of retry attempts
        
    Returns:
        Processed event data
        
    Raises:
        ProcessingError: If event processing fails
    """
    pass
```

#### Class Definitions

```python
class EventProcessor:
    """Process monitoring events and generate notifications."""
    
    def __init__(
        self, 
        event_repository: IEventRepository,
        notifier: IEventNotifier
    ) -> None:
        """Initialize the event processor.
        
        Args:
            event_repository: Repository for event data access
            notifier: Service for event notifications
        """
        self._event_repository = event_repository
        self._notifier = notifier
```

### Type Hints

#### Full Type Annotations

```python
from typing import Dict, List, Optional, Union
from datetime import datetime

def process_events(
    events: List[Dict[str, Union[str, int, float]]],
    start_time: Optional[datetime] = None
) -> Dict[str, Union[bool, List[str]]]:
    """Process a list of monitoring events.
    
    Args:
        events: List of events to process
        start_time: Optional start time for filtering
        
    Returns:
        Dictionary with processing results
    """
    pass
```

#### Generic Types

```python
from typing import Generic, TypeVar, Protocol

T = TypeVar('T')

class Repository(Protocol[T]):
    """Generic repository interface."""
    
    def get(self, id: str) -> Optional[T]:
        """Get an entity by ID."""
        pass
    
    def save(self, entity: T) -> None:
        """Save an entity."""
        pass
```

### Error Handling

#### Exception Hierarchy

```python
class MonitoringError(Exception):
    """Base exception for monitoring system errors."""
    pass

class ProcessingError(MonitoringError):
    """Error during event processing."""
    pass

class DatabaseError(MonitoringError):
    """Error during database operations."""
    pass

class AWSClientError(MonitoringError):
    """Error during AWS service calls."""
    pass
```

#### Error Handling Patterns

```python
def process_event(event: dict) -> dict:
    """Process an event with comprehensive error handling."""
    try:
        # Validate input
        if not event.get('account'):
            raise ValueError("Missing account field")
            
        # Process event
        processed = _process_event_data(event)
        
        # Save to database
        self._event_repository.save(processed)
        
        return processed
        
    except (ValueError, ProcessingError) as e:
        # Log error and re-raise
        self._logger.error(f"Event processing failed: {e}")
        raise
        
    except DatabaseError as e:
        # Handle database errors specifically
        self._logger.error(f"Database error: {e}")
        raise MonitoringError("Failed to save event") from e
```

### Logging Standards

#### Structured Logging

```python
import structlog
from structlog.types import FilteringBoundLogger

logger: FilteringBoundLogger = structlog.get_logger()

def process_event(event: dict) -> dict:
    """Process an event with structured logging."""
    logger.info(
        "Processing event",
        event_id=event.get('id'),
        account=event.get('account'),
        source=event.get('source')
    )
    
    try:
        # Processing logic
        result = _process_event_data(event)
        
        logger.info(
            "Event processed successfully",
            event_id=event.get('id'),
            processing_time=result.get('processing_time')
        )
        
        return result
        
    except Exception as e:
        logger.error(
            "Event processing failed",
            event_id=event.get('id'),
            error=str(e),
            exc_info=True
        )
        raise
```

#### Log Levels Usage

```python
# DEBUG: Detailed information for debugging
logger.debug("Querying CloudWatch logs", query=cloudwatch_query)

# INFO: General information about system operation
logger.info("Daily report generated", report_id=report_id)

# WARNING: Something unexpected but recoverable
logger.warning("Retrying failed operation", attempt=retry_count)

# ERROR: Serious problems that need attention
logger.error("Database connection failed", error=str(e))

# CRITICAL: Critical errors that may cause system failure
logger.critical("System critical failure", error=str(e))
```

### Testing Standards

#### Test Organization

```
tests/
├── unit/                    # Unit tests
│   ├── domain/
│   ├── adapters/
│   └── common/
├── integration/             # Integration tests
│   ├── repositories/
│   ├── aws_services/
│   └── api_endpoints/
└── e2e/                    # End-to-end tests
    ├── complete_workflows/
    └── deployment_tests/
```

#### Unit Test Example

```python
import pytest
from unittest.mock import Mock, patch
from src.domain.use_cases.daily_report import DailyReportUseCase
from src.domain.models.event import Event

class TestDailyReportUseCase:
    """Test cases for DailyReportUseCase."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_repository = Mock()
        self.mock_notifier = Mock()
        self.use_case = DailyReportUseCase(
            event_repository=self.mock_repository,
            notifier=self.mock_notifier
        )
    
    def test_generate_report_success(self):
        """Test successful daily report generation."""
        # Arrange
        test_events = [
            Event(
                id="event1",
                account="123456789012",
                severity=1,
                published_at=1735689600
            ),
            Event(
                id="event2",
                account="123456789012", 
                severity=2,
                published_at=1735689600
            )
        ]
        
        self.mock_repository.get_events.return_value = test_events
        
        # Act
        result = self.use_case.generate_report()
        
        # Assert
        assert result['total_events'] == 2
        assert result['high_severity_events'] == 1
        self.mock_notifier.send_report.assert_called_once()
    
    def test_generate_report_empty_events(self):
        """Test report generation with no events."""
        # Arrange
        self.mock_repository.get_events.return_value = []
        
        # Act
        result = self.use_case.generate_report()
        
        # Assert
        assert result['total_events'] == 0
        self.mock_notifier.send_report.assert_called_once()
```

#### Integration Test Example

```python
import pytest
from src.adapters.db.repositories.event_repository import EventRepository
from src.domain.models.event import Event

class TestEventRepositoryIntegration:
    """Integration tests for EventRepository."""
    
    @pytest.fixture
    def repository(self):
        """Create repository instance for testing."""
        return EventRepository(table_name='test-events')
    
    def test_save_and_retrieve_event(self, repository):
        """Test saving and retrieving an event."""
        # Arrange
        event = Event(
            id="test-event-id",
            account="123456789012",
            severity=1,
            published_at=1735689600
        )
        
        # Act
        repository.save(event)
        retrieved = repository.get_by_id("test-event-id")
        
        # Assert
        assert retrieved is not None
        assert retrieved.id == "test-event-id"
        assert retrieved.account == "123456789012"
```

### Documentation Standards

#### Docstring Format

```python
"""Process monitoring events and generate notifications.

This module provides functionality for processing monitoring events received
from various AWS services. It includes event validation, enrichment, 
storage, and notification generation.

Example:
    >>> processor = EventProcessor(
    ...     event_repository=EventRepository(),
    ...     notifier=SlackNotifier()
    ... )
    >>> result = processor.process_event(event_data)
"""

from typing import Dict, List, Optional
from datetime import datetime

class EventProcessor:
    """Process monitoring events and generate notifications.
    
    This class handles the complete event processing pipeline including:
    - Event validation and enrichment
    - Database storage
    - Notification generation
    
    Args:
        event_repository: Repository for event data access
        notifier: Service for event notifications
        
    Attributes:
        logger: Structured logger for this component
    """
    
    def process_events(
        self, 
        events: List[Dict[str, any]],
        start_time: Optional[datetime] = None
    ) -> Dict[str, any]:
        """Process a list of monitoring events.
        
        Args:
            events: List of events to process
            start_time: Optional start time for event filtering
            
        Returns:
            Dictionary containing processing results:
            - 'processed_count': Number of successfully processed events
            - 'failed_count': Number of failed events
            - 'errors': List of error messages
            
        Raises:
            ProcessingError: If event processing fails catastrophically
        """
        pass
```

### Configuration Management

#### Environment Variables

```python
import os
from typing import Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application configuration settings."""
    
    # AWS Configuration
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    
    # Database Configuration
    dynamodb_table_name: str = Field(default="monitoring-events", env="DYNAMODB_TABLE_NAME")
    dynamodb_endpoint_url: Optional[str] = Field(default=None, env="DYNAMODB_ENDPOINT_URL")
    
    # CloudWatch Configuration
    cloudwatch_query_string: str = Field(
        default="fields @message | filter @message like /(?i)(error|fail|exception)/",
        env="CLOUDWATCH_QUERY_STRING"
    )
    cloudwatch_query_duration: int = Field(default=300, env="CLOUDWATCH_QUERY_DURATION")
    
    # Notification Configuration
    slack_webhook_url: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    notification_enabled: bool = Field(default=True, env="NOTIFICATION_ENABLED")
    
    # Monitoring Configuration
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    timeout: int = Field(default=30, env="TIMEOUT")
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
```

### Code Quality Tools

#### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/bandit
    rev: 1.7.4
    hooks:
      - id: bandit
        args: [-r, src/]
```

#### Code Quality Metrics

| Metric | Target | Tool |
|--------|---------|------|
| Test Coverage | > 85% | pytest-cov |
| Code Complexity | < 10 | radon |
| Linter Issues | 0 | ruff |
| Format Issues | 0 | ruff-format |
| Security Issues | 0 | bandit |

### Security Standards

#### Input Validation

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class EventData(BaseModel):
    """Schema for event data validation."""
    
    account: str = Field(..., min_length=12, max_length=12, description="AWS Account ID")
    region: str = Field(..., description="AWS Region")
    source: str = Field(..., description="Event source")
    detail_type: str = Field(..., description="Type of event detail")
    severity: int = Field(..., ge=0, le=4, description="Severity level 0-4")
    resources: List[str] = Field(default_factory=list, description="Affected resources")
    
    @validator('account')
    def validate_account(cls, v):
        """Validate AWS Account ID format."""
        if not v.isdigit():
            raise ValueError("Account ID must be numeric")
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        """Validate severity level."""
        if v not in [0, 1, 2, 3, 4]:
            raise ValueError("Severity must be 0-4")
        return v
```

#### Security Best Practices

1. **Environment Variables**: Never hardcode secrets
2. **Input Validation**: Validate all external inputs
3. **Error Handling**: Don't expose sensitive error details
4. **Dependencies**: Use dependency scanning (safety)
5. **Secrets**: Use secrets manager for sensitive data

### Performance Standards

#### Database Optimization

```python
class EventRepository:
    """Optimized DynamoDB event repository."""
    
    def get_events_by_time_range(
        self,
        start_time: int,
        end_time: int,
        limit: int = 100
    ) -> List[Event]:
        """Get events within time range with optimized query."""
        
        # Use consistent query pattern
        response = self._table.query(
            KeyConditionExpression=Key('pk').eq('EVENT') & 
                               Key('sk').between(
                                   f'EVENT#{start_time}',
                                   f'EVENT#{end_time}'
                               ),
            Limit=limit,
            ScanIndexForward=False  # Most recent first
        )
        
        return [self._mapper.to_domain(item) for item in response['Items']]
```

#### Lambda Optimization

```python
import boto3
from botocore.config import Config

# Configure optimized boto3 client
dynamodb_client = boto3.resource(
    'dynamodb',
    config=Config(
        retries={'max_attempts': 3, 'mode': 'adaptive'},
        max_pool_connections=50,
        region_name='us-east-1'
    )
)

# Use connection pooling and reuse clients
class CloudWatchClient:
    """Optimized CloudWatch client with connection pooling."""
    
    def __init__(self):
        self._client = boto3.client(
            'logs',
            config=Config(
                retries={'max_attempts': 2, 'mode': 'standard'},
                max_pool_connections=10
            )
        )
    
    def query_logs(self, query: str, log_group: str, start_time: int):
        """Execute CloudWatch Logs Insights query."""
        return self._client.start_query_logs(
            logGroupName=log_group,
            startTime=start_time,
            endTime=start_time + 300,  # 5 minute window
            queryString=query
        )
```

These coding standards ensure high-quality, maintainable, and secure code across the entire AWS Monitoring project. All team members should follow these guidelines to maintain consistency and code quality.
---
description: Implement features with tests, documentation, and best practices
---

# Implementation Mode

I'll implement the requested feature or change following best practices. This command provides:

- **Complete implementation** - Code, tests, infrastructure, and documentation
- **Quality assurance** - Type safety, error handling, test coverage
- **Architectural compliance** - Follows hexagonal architecture
- **Production ready** - Includes monitoring, logging, error handling

## Implementation Checklist

### 1. Domain Layer
- [ ] Create/update domain models with Pydantic validation
- [ ] Define port interfaces (repositories, notifiers, etc.)
- [ ] Implement use case with business logic
- [ ] Add comprehensive type hints
- [ ] Write unit tests for use cases

### 2. Adapters Layer
- [ ] Implement repository adapters
- [ ] Create database models and mappers
- [ ] Implement external service adapters (AWS, notifications)
- [ ] Add error handling with specific exceptions
- [ ] Write adapter unit tests

### 3. Entrypoints Layer
- [ ] Create Lambda handlers or API endpoints
- [ ] Add input validation
- [ ] Implement error responses
- [ ] Add logging with context
- [ ] Write integration tests

### 4. Infrastructure
- [ ] Update serverless.yml configuration
- [ ] Add IAM permissions
- [ ] Configure environment variables
- [ ] Add CloudFormation resources if needed
- [ ] Update deployment scripts if needed

### 5. Testing
- [ ] Unit tests with >90% coverage
- [ ] Integration tests with mocks
- [ ] Edge case and error scenario tests
- [ ] Test fixtures and test data
- [ ] Run full test suite

### 6. Documentation
- [ ] Update CLAUDE.md if adding patterns
- [ ] Add docstrings to public functions
- [ ] Update API documentation if applicable
- [ ] Add inline comments for complex logic
- [ ] Update README.md if user-facing

### 7. Code Quality
- [ ] Type hints everywhere
- [ ] Pydantic models for all data
- [ ] Specific exception types
- [ ] No broad `except Exception` handlers
- [ ] Follow existing code style
- [ ] Run linter (ruff)

## Implementation Standards

### Code Style
```python
# ✅ Good: Typed, validated, specific errors
from pydantic import BaseModel, Field
from src.common.exceptions import NotFoundError

class Event(BaseModel):
    id: str = Field(..., description="Event ID")
    account: str

def get_event(event_id: str) -> Event:
    try:
        return repository.get(event_id)
    except DoesNotExist as err:
        raise NotFoundError(f"Event {event_id} not found") from err
```

### Test Style
```python
# ✅ Good: Descriptive, comprehensive, uses fixtures
def test_get_event_success(event_repository, sample_event):
    """Test successful event retrieval."""
    result = get_event(sample_event.id)
    assert result.id == sample_event.id

def test_get_event_not_found(event_repository):
    """Test event not found raises NotFoundError."""
    with pytest.raises(NotFoundError):
        get_event("nonexistent-id")
```

What would you like to implement?

Please provide:
- **Feature/Task**: What should be implemented?
- **Requirements**: Specific functionality needed
- **Acceptance Criteria**: How to verify it works?
- **Context**: Any related code or dependencies?

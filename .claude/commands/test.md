---
description: Run tests, analyze coverage, and improve test quality
---

# Testing Mode

I'll help you with testing tasks. This command provides:

- **Test execution** - Run tests and analyze results
- **Coverage analysis** - Identify gaps and improve coverage
- **Test improvement** - Enhance test quality and effectiveness
- **Test design** - Create comprehensive test strategies

## Testing Capabilities

### 1. Run Tests
```bash
# Run all tests with coverage
make test

# Run specific test file
poetry run pytest tests/path/to/test_file.py -v

# Run tests matching pattern
poetry run pytest -k "test_pattern" -v

# Run with verbose output
poetry run pytest -vv

# Run and show print statements
poetry run pytest -s
```

### 2. Coverage Analysis
```bash
# Generate coverage report
make coverage

# View coverage in terminal
poetry run pytest --cov=src --cov-report=term-missing

# Generate HTML report
poetry run pytest --cov=src --cov-report=html
```

### 3. Test Categories

**Unit Tests**
- Test individual functions and methods
- Mock external dependencies
- Fast execution
- High coverage of business logic

**Integration Tests**
- Test component interactions
- Use moto for AWS mocking
- Test database operations
- Test event flows

**End-to-End Tests**
- Test complete workflows
- Use LocalStack when possible
- Verify system behavior
- Test error scenarios

## Test Quality Standards

### Good Test Characteristics
- **Clear**: Descriptive names and structure
- **Independent**: No dependencies between tests
- **Repeatable**: Same result every time
- **Fast**: Quick feedback loop
- **Comprehensive**: Cover happy path and edge cases

### Test Structure (AAA Pattern)
```python
def test_feature_scenario():
    """Test description of what and why."""
    # Arrange - Set up test data
    event = Event(id="test-id", account="123456789012")

    # Act - Execute the code under test
    result = process_event(event)

    # Assert - Verify the outcome
    assert result.status == "success"
    assert result.processed_at is not None
```

### Coverage Expectations
- **Overall**: >90% coverage target
- **Domain layer**: 100% coverage (business logic)
- **Adapters**: >85% coverage
- **Entrypoints**: >80% coverage
- **New code**: Must maintain or improve overall coverage

## Testing Checklist

### Unit Tests
- [ ] Test happy path
- [ ] Test edge cases (empty, null, boundary values)
- [ ] Test error scenarios
- [ ] Test validation failures
- [ ] Mock external dependencies
- [ ] Use fixtures for test data

### Integration Tests
- [ ] Test component interactions
- [ ] Test database operations (CRUD)
- [ ] Test AWS service integrations
- [ ] Test event publishing and handling
- [ ] Test cross-layer interactions
- [ ] Use moto for AWS mocking

### Test Data
- [ ] Use realistic test data
- [ ] Create reusable fixtures
- [ ] Avoid hard-coded values
- [ ] Use factories for complex objects
- [ ] Keep test data in tests/data/

### Assertions
- [ ] Assert expected outcomes
- [ ] Assert error types and messages
- [ ] Assert side effects
- [ ] Use specific assertions (not just truthy)
- [ ] Test both positive and negative cases

## Common Testing Patterns

### Fixture Pattern
```python
@pytest.fixture
def sample_event():
    """Create a sample event for testing."""
    return Event(
        id="test-event-id",
        account="123456789012",
        region="us-east-1",
        source="aws.cloudwatch",
        detail={"test": "data"}
    )
```

### Parametrized Tests
```python
@pytest.mark.parametrize("severity,expected", [
    (0, "Unknown"),
    (1, "Low"),
    (2, "Medium"),
    (3, "High"),
    (4, "Critical"),
])
def test_severity_levels(severity, expected):
    """Test all severity level mappings."""
    assert get_severity_name(severity) == expected
```

### Mocking Pattern
```python
@patch('src.adapters.aws.cloudwatch.boto3.client')
def test_query_logs(mock_boto_client, sample_log_groups):
    """Test CloudWatch Logs query."""
    mock_client = Mock()
    mock_boto_client.return_value = mock_client

    result = query_logs(sample_log_groups)

    assert mock_client.start_query.called
    assert len(result) > 0
```

## What would you like to do?

- **Run tests**: Execute test suite and show results
- **Check coverage**: Analyze coverage and identify gaps
- **Improve tests**: Enhance existing tests or add missing ones
- **Debug failing test**: Investigate and fix test failures
- **Design test strategy**: Plan testing approach for new feature
- **Review test quality**: Assess and improve test effectiveness

Please specify:
- **What to test**: Specific file, module, or feature
- **Test type**: Unit, integration, or e2e
- **Goal**: What you want to achieve

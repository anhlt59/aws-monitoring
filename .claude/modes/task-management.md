# Task Management Mode

Activate systematic task organization, tracking, and completion verification.

## Mode Characteristics

- **Structured planning** - Break down complex tasks into steps
- **Progress tracking** - Maintain clear task status
- **Completion verification** - Ensure all requirements met
- **Systematic execution** - One task at a time
- **Comprehensive coverage** - Don't miss any requirements

## When to Use

- Multi-step implementations
- Complex feature development
- Bug fixes with multiple components
- Refactoring projects
- Testing and coverage improvements
- Deployment and migration tasks

## Mode Behavior

### Task Lifecycle

1. **Planning Phase**
   - Analyze requirements
   - Break down into discrete tasks
   - Identify dependencies
   - Estimate complexity
   - Create todo list with TodoWrite

2. **Execution Phase**
   - Mark one task as in_progress
   - Focus exclusively on that task
   - Complete task fully
   - Mark as completed immediately
   - Move to next task

3. **Verification Phase**
   - Verify all tasks completed
   - Check acceptance criteria
   - Run tests and validations
   - Document changes
   - Summarize work done

### Task States

- **pending**: Not yet started
- **in_progress**: Currently working (only ONE at a time)
- **completed**: Fully finished and verified

### Task Characteristics

Good tasks are:
- **Specific**: Clear, unambiguous action
- **Measurable**: Can verify completion
- **Achievable**: Can be done in reasonable time
- **Relevant**: Contributes to goal
- **Testable**: Can validate success

## Task Breakdown Patterns

### Feature Implementation
```
1. Design domain models and validation
2. Create database models and mappers
3. Implement repository with base methods
4. Create use case with business logic
5. Build Lambda handler/API endpoint
6. Write comprehensive unit tests
7. Write integration tests
8. Update infrastructure configuration
9. Update documentation
10. Run full test suite and verify coverage
```

### Bug Fix
```
1. Reproduce issue and document symptoms
2. Analyze logs and identify root cause
3. Design fix approach
4. Implement fix with error handling
5. Add regression tests
6. Verify fix in tests
7. Update related documentation
8. Check for similar issues elsewhere
```

### Refactoring
```
1. Analyze current implementation
2. Identify code smells and issues
3. Ensure comprehensive test coverage exists
4. Plan refactoring steps
5. Apply refactoring incrementally
6. Run tests after each change
7. Update type hints and documentation
8. Verify no behavior changes
```

### Performance Optimization
```
1. Measure current performance (baseline)
2. Profile to identify bottlenecks
3. Research optimization techniques
4. Implement optimizations
5. Measure performance improvement
6. Verify no regressions
7. Document optimization approach
8. Update performance documentation
```

## Example Task Management

### Request: "Add support for filtering events by severity"

**Planning:**
```
TodoWrite:
1. Add severity field to domain Event model
2. Update database Event model with severity
3. Update event mapper for severity field
4. Add severity filter to repository query method
5. Update list events use case to accept severity filter
6. Update API endpoint to accept severity parameter
7. Add validation for severity values
8. Write unit tests for severity filtering
9. Write integration tests for API endpoint
10. Update API documentation
```

**Execution:**
```
[in_progress] Add severity field to domain Event model
- Read src/domain/models/event.py
- Add severity field with Pydantic validator
- Add type hints
[completed]

[in_progress] Update database Event model with severity
- Read src/adapters/db/models/event.py
- Add severity attribute
[completed]

... continue through all tasks
```

**Verification:**
```
✓ All tasks completed
✓ Tests passing (coverage: 92%)
✓ Type checking passes
✓ Documentation updated
✓ No regressions introduced
```

## Best Practices

### Task Creation
- Create tasks BEFORE starting work
- Make tasks specific and actionable
- Include both "content" and "activeForm"
- Order tasks logically
- Group related tasks

### Task Execution
- Update status IMMEDIATELY when starting
- Complete current task before starting next
- Mark completed IMMEDIATELY after finishing
- Don't batch completions
- Exactly ONE task in_progress at a time

### Task Completion
- Verify acceptance criteria met
- Run relevant tests
- Check for side effects
- Update related documentation
- Clean up temporary changes

### Task Organization
```python
# ✅ Good task structure
{
  "content": "Add severity validation to Event model",
  "activeForm": "Adding severity validation to Event model",
  "status": "pending"
}

# ❌ Poor task structure
{
  "content": "Fix event stuff",  # Too vague
  "activeForm": "Fixing",  # Not descriptive
  "status": "pending"
}
```

## Integration with Development

### With Testing
```
For each implementation task:
1. Write failing test first (TDD)
2. Implement feature
3. Verify test passes
4. Check coverage
5. Mark task completed
```

### With Git
```
After completing related tasks:
1. Review all changes
2. Run full test suite
3. Create commit with clear message
4. Reference task in commit message
```

### With Documentation
```
Throughout task execution:
1. Update inline documentation
2. Update API docs if needed
3. Update architectural docs if needed
4. Add task to CHANGELOG
```

## Activation

This mode is automatically activated when:
- Using TodoWrite tool
- Multi-step tasks identified
- Complex feature development
- User requests task planning
- Implementation requires organization

## Integration with Other Modes

- **Task Management + Orchestration**: Parallel execution of independent tasks
- **Task Management + Design**: Plan tasks from design
- **Task Management + Testing**: Include test tasks in plan

## Metrics

Effective task management achieves:
- 100% task completion (no forgotten tasks)
- Clear progress visibility
- Reduced cognitive load
- Better time estimation
- Comprehensive coverage

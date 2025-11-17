# MCP Sequential Thinking

Integration with Sequential Thinking for multi-step reasoning, complex problem-solving, and systematic analysis.

## Capabilities

- **Multi-Step Reasoning**: Break down complex problems into sequential steps
- **Hypothesis Testing**: Form and test hypotheses systematically
- **Root Cause Analysis**: Trace issues through logical reasoning chains
- **Design Thinking**: Structure design decisions sequentially
- **Debugging**: Step-by-step problem isolation
- **Planning**: Create detailed implementation plans

## Use Cases for AWS Monitoring Project

### 1. Architecture Design
```
Step 1: Define requirements
  - Multi-account monitoring
  - Real-time notifications
  - Historical event storage

Step 2: Evaluate patterns
  - Hub-and-spoke vs peer-to-peer
  - Synchronous vs asynchronous
  - Centralized vs distributed

Step 3: Select AWS services
  - EventBridge for event routing
  - Lambda for processing
  - DynamoDB for storage

Step 4: Design data model
  - Single-table design
  - Access patterns
  - GSI requirements

Step 5: Plan deployment
  - Master stack deployment
  - Agent stack distribution
  - Cross-account permissions
```

### 2. Root Cause Analysis
```
Step 1: Identify symptoms
  - Events not appearing in DynamoDB
  - No errors in Lambda logs

Step 2: Check event delivery
  - Verify EventBridge rules
  - Check cross-account permissions
  - Inspect event patterns

Step 3: Trace event flow
  - Agent publishes to EventBridge
  - EventBridge routes to master account
  - Lambda processes event

Step 4: Isolate failure point
  - Check agent EventBridge logs
  - Verify cross-account role trust
  - Test IAM permissions

Step 5: Identify root cause
  - IAM policy missing PutEvents permission
```

### 3. Feature Implementation
```
Step 1: Analyze requirements
  - What data is needed?
  - What validations are required?
  - What are edge cases?

Step 2: Design domain model
  - Define Pydantic models
  - Specify validators
  - Plan relationships

Step 3: Design ports
  - Repository interface
  - External service interfaces
  - Define contracts

Step 4: Implement use case
  - Business logic
  - Error handling
  - Validation

Step 5: Implement adapters
  - Database repository
  - AWS service clients
  - External integrations

Step 6: Create entrypoint
  - Lambda handler
  - Input validation
  - Response formatting

Step 7: Add tests
  - Unit tests
  - Integration tests
  - Coverage verification
```

### 4. Performance Optimization
```
Step 1: Identify bottleneck
  - Measure Lambda execution time
  - Profile CloudWatch Logs queries
  - Check DynamoDB metrics

Step 2: Analyze causes
  - Cold start overhead
  - Inefficient queries
  - Large payload sizes

Step 3: Evaluate solutions
  - Provisioned concurrency
  - Query optimization
  - Payload compression

Step 4: Implement optimization
  - Refactor code
  - Update configuration
  - Add caching

Step 5: Measure improvement
  - Compare metrics
  - Validate performance gains
  - Check cost impact
```

## Configuration

The Sequential Thinking MCP enables:
- Structured problem decomposition
- Step-by-step reasoning visibility
- Systematic hypothesis testing
- Comprehensive planning
- Traceable decision making

## Integration Points

- Complex architectural decisions
- Multi-step implementation planning
- Systematic debugging and troubleshooting
- Performance optimization strategies
- Design pattern selection
- Migration planning
- Refactoring strategies

## Example Usage

When facing complex problems:
1. Activate Sequential Thinking mode
2. Break problem into discrete steps
3. Document reasoning at each step
4. Test hypotheses systematically
5. Trace conclusions back to evidence
6. Document decision rationale

This ensures:
- Thorough analysis
- Traceable reasoning
- Reproducible solutions
- Knowledge capture
- Team alignment

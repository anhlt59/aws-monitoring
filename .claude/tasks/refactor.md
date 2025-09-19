# Tasks

1. **Broad Exception Handling** (14 instances)

- Files: `src/adapters/db/repositories/base.py`, `src/adapters/logs.py`, `src/adapters/aws/data_classes.py`
- Action: Replace `except Exception` with specific exception types
- Impact: Better error diagnosis and handling

2. **Limited Unit Test Coverage**

- Current: 8 test files for 70 source files
- Target: 15+ test files, >90% coverage
- Focus: Domain use cases, adapter implementations


3. **Hardcoded Account Metadata** (`src/common/constants.py:43-47`)

- TODO comment present: "Restructure metadata, load from environment or database"
- Action: Move to DynamoDB or AWS Systems Manager Parameter Store
- Impact: Scalability and maintainability

4. **Synchronous CloudWatch Polling** (`src/adapters/aws/cloudwatch.py:40-44`)

- Current: Blocking while loop with `time.sleep()`
- Action: Consider async/await or Step Functions
- Impact: Lambda execution cost and timeout risk

5. **Potential N+1 Queries** (`src/adapters/logs.py:42-50`)

- Iterative log group processing in ECS cluster listing
- Action: Batch operations where possible
- Impact: Performance at scale

6. **Magic Strings for Event Types** (`src/adapters/notifiers/events.py`)

- Action: Refactor to enums or constants
- Impact: Type safety and maintainability

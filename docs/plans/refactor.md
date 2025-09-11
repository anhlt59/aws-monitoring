# Hexagonal Architecture

## Current State Analysis

The AWS monitoring application currently follows a layered architecture with some hexagonal principles but lacks strict enforcement of dependency inversion and interface-based abstractions. The codebase is organized into:

- **Handlers** (Presentation Layer): Lambda entry points and Business logic orchestration 
- **Services** (Application Layer): Data access patterns via repositories or infrastructure
- **Repositories** (Infrastructure): Data access patterns
- **Infrastructure** (External Adapters): AWS service abstractions

## Identified Violations

### 1. Configuration Coupling
- **Issue**: Infrastructure components directly access global config
- **Examples**:
  - `src/infras/aws/cloudwatch.py:7` - Direct import of AWS_ENDPOINT, AWS_REGION
  - Multiple AWS services have hardcoded configuration dependencies

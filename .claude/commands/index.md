---
description: Index and map the codebase for better understanding and navigation
---

# Repository Indexing Mode

I'll create a comprehensive index of the codebase. This command provides:

- **Codebase mapping** - Complete structure and organization
- **Pattern identification** - Common patterns and conventions
- **Dependency mapping** - How components relate and interact
- **Knowledge extraction** - Domain concepts and business logic

## Indexing Scope

### Structure Indexing
- Directory organization and module structure
- Entry points (Lambda functions, API endpoints)
- Core domain entities and use cases
- Adapter implementations
- Test organization

### Pattern Indexing
- Architectural patterns (hexagonal, repository)
- Design patterns (factory, builder, strategy)
- Code conventions and style
- Testing patterns
- Configuration patterns

### Dependency Indexing
- Module dependencies and imports
- AWS service integrations
- External library usage
- Internal component relationships
- Data flow between layers

### Documentation Indexing
- Existing documentation files
- Code comments and docstrings
- Configuration files
- Infrastructure definitions
- Test fixtures and data

## Index Outputs

### 1. Structure Map
```
src/
├── domain/          # Business logic layer
│   ├── models/      # Core entities
│   ├── ports/       # Interface contracts
│   └── use_cases/   # Business workflows
├── adapters/        # External integrations
│   ├── db/          # Database layer
│   ├── aws/         # AWS services
│   └── notifiers/   # Notification services
└── entrypoints/     # Application entry
    ├── functions/   # Lambda handlers
    └── apigw/       # API endpoints
```

### 2. Component Registry
- All domain models and their fields
- All use cases and their dependencies
- All repositories and adapters
- All Lambda functions and triggers
- All API endpoints and methods

### 3. Pattern Catalog
- How errors are handled
- How repositories are implemented
- How validation is performed
- How tests are structured
- How configuration is managed

### 4. Integration Map
- DynamoDB table access patterns
- EventBridge event schemas
- CloudWatch Logs queries
- API Gateway endpoints
- IAM roles and permissions

## Usage

Run this command to:
- Understand the codebase structure
- Locate specific functionality
- Identify where to add new code
- Find usage examples
- Map dependencies for changes

The index will help answer questions like:
- Where is X functionality implemented?
- How do I add a new Y?
- What are all the Z in the system?
- How does A interact with B?
- What tests exist for C?

Would you like me to index the entire codebase or focus on specific areas?

Options:
- **Full index**: Complete codebase mapping
- **Layer index**: Specific layer (domain, adapters, entrypoints)
- **Component index**: Specific component type (models, use cases, repositories)
- **Feature index**: Specific feature or module

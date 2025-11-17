---
description: Get help with the project, commands, agents, and modes
---

# Help & Guidance

Welcome to the AWS Monitoring project assistance! I can help you with:

## Available Commands

Invoke these with `/command-name`:

- **/brainstorm** - Facilitate creative brainstorming for features and solutions
- **/analyze** - Perform deep analysis of code, architecture, or issues
- **/research** - Research technologies, patterns, and best practices
- **/design** - Design new features or architectural solutions
- **/implement** - Implement features with tests and documentation
- **/index** - Map and index the codebase structure
- **/test** - Run tests, analyze coverage, and improve test quality
- **/help** - Show this help information

## Available Agents

Specialized expertise available (automatically activated or via @agent-name):

- **@backend-architect** - Serverless AWS architecture and hexagonal design
- **@frontend-architect** - Modern web applications and UI/UX
- **@python-expert** - Python best practices and optimization
- **@refactoring-expert** - Code improvement and technical debt reduction
- **@repo-index** - Codebase navigation and documentation
- **@requirements-analyst** - Requirements gathering and analysis
- **@root-cause-analyst** - Debugging and troubleshooting
- **@system-architect** - Distributed systems and cloud architecture
- **@technical-writer** - Documentation and API docs

## Available Modes

Behavioral modes for different contexts:

- **Brainstorming Mode** - Creative exploration and idea generation
- **Deep Research Mode** - Comprehensive investigation with web search
- **Orchestration Mode** - Efficient multi-tool coordination
- **Task Management Mode** - Systematic task organization
- **Token Efficiency Mode** - Optimize context usage

## Project Quick Reference

### Architecture
- **Pattern**: Hexagonal (domain → ports → adapters)
- **Deployment**: Master-agent serverless architecture
- **Database**: DynamoDB single-table design
- **Events**: EventBridge for cross-account communication

### Key Commands
```bash
make install        # Install dependencies
make test          # Run tests with coverage
make start         # Start LocalStack
make deploy-local  # Deploy to LocalStack
```

### Project Structure
```
src/
├── domain/         # Business logic (models, ports, use cases)
├── adapters/       # External integrations (db, aws, notifiers)
├── entrypoints/    # Application entry (functions, api)
└── common/         # Shared utilities
```

### Development Guidelines
- Follow hexagonal architecture strictly
- Maintain >90% test coverage
- Use Pydantic for all data validation
- Use specific exception types
- Type hints everywhere
- Follow CLAUDE.md guidelines

## Documentation

- **@CLAUDE.md** - Development guidelines and best practices
- **@docs/overview.md** - System architecture overview
- **@docs/project_structure.md** - Codebase structure
- **@docs/db.md** - Database schema
- **@docs/development.md** - Local development guide
- **@docs/deployment.md** - Deployment guide

## Getting Started

1. **Explore the codebase**: Use `/index` to map the structure
2. **Understand a component**: Use `/analyze` to deep-dive
3. **Add a feature**: Use `/design` then `/implement`
4. **Fix an issue**: Use `/analyze` to investigate
5. **Improve code**: Ask @refactoring-expert for help

## Common Tasks

- **Add new event type**: Domain model → Mapper → Repository → Use case → Entrypoint
- **Add notification**: Implement INotifier → Add template → Update use case
- **Modify schema**: Update domain → Update DB model → Update mapper → Migration
- **Debug issue**: Check CloudWatch Logs → Trace event flow → Review permissions

Need help with something specific? Just ask!

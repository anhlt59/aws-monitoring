# Claude Code Enhancement Framework

This directory contains specialized agents, commands, MCP integrations, and behavioral modes to enhance Claude Code's capabilities for the AWS Monitoring project.

## Overview

The framework provides:
- **8 Specialized Agents** - Domain experts for different aspects of development
- **7 Slash Commands** - Quick access to common workflows
- **4 MCP Integrations** - External tool and service integrations
- **5 Behavioral Modes** - Adaptive AI behavior for different contexts

## Quick Start

### Using Commands

Commands are invoked with a slash prefix:

```
/help              # Get help and guidance
/brainstorm        # Creative idea generation
/analyze           # Deep analysis of code or architecture
/research          # Research technologies and patterns
/design            # Design new features or solutions
/implement         # Implement with tests and docs
/index             # Map the codebase structure
/test              # Run and improve tests
```

### Using Agents

Agents are automatically activated based on context, or you can explicitly reference them:

```
@backend-architect     # Serverless AWS architecture
@python-expert         # Python best practices
@refactoring-expert    # Code improvement
@root-cause-analyst    # Debugging and troubleshooting
@system-architect      # Distributed systems design
@technical-writer      # Documentation
@requirements-analyst  # Requirements gathering
@repo-index           # Codebase navigation
@frontend-architect   # UI/UX and frontend
```

### Example Workflows

#### 1. Adding a New Feature

```bash
# Step 1: Understand requirements
@requirements-analyst "I need to add email notifications"

# Step 2: Design the solution
/design email notification system

# Step 3: Implement with best practices
/implement email notifications

# Step 4: Verify with tests
/test email notification functionality
```

#### 2. Debugging an Issue

```bash
# Step 1: Investigate the problem
@root-cause-analyst "Events not appearing in DynamoDB"

# Step 2: Analyze the root cause
/analyze event processing pipeline

# Step 3: Fix the issue
/implement fix for event delivery
```

#### 3. Exploring the Codebase

```bash
# Step 1: Map the structure
/index entire codebase

# Step 2: Find specific functionality
@repo-index "Where is error handling implemented?"

# Step 3: Analyze for improvements
/analyze error handling patterns
```

#### 4. Refactoring Code

```bash
# Step 1: Identify issues
/analyze code quality in src/domain/

# Step 2: Plan refactoring
@refactoring-expert "How to improve event processing?"

# Step 3: Execute refactoring
/implement refactoring plan
```

## Detailed Documentation

### Agents

Located in `.claude/agents/`, agents provide specialized expertise:

#### Backend & Architecture
- **backend-architect**: Serverless AWS architecture, hexagonal design, event-driven patterns
- **system-architect**: Distributed systems, scalability, reliability, cloud architecture
- **python-expert**: Python 3.13+, Pydantic, type safety, performance optimization

#### Development & Quality
- **refactoring-expert**: Code improvement, design patterns, technical debt reduction
- **requirements-analyst**: Requirements gathering, user stories, acceptance criteria
- **root-cause-analyst**: Debugging, troubleshooting, systematic investigation

#### Documentation & Navigation
- **technical-writer**: Documentation, API docs, architecture diagrams, guides
- **repo-index**: Codebase navigation, structure mapping, pattern identification
- **frontend-architect**: UI/UX, modern frameworks, API integration, accessibility

### Commands

Located in `.claude/commands/`, commands provide workflows:

#### Development Lifecycle
- **/brainstorm**: Generate and explore ideas using SCAMPER, Six Thinking Hats, First Principles
- **/design**: Create comprehensive designs with architecture diagrams and implementation plans
- **/implement**: Build features following hexagonal architecture with >90% test coverage
- **/test**: Run tests, analyze coverage, improve test quality

#### Analysis & Research
- **/analyze**: Deep dive into code, architecture, performance, or issues
- **/research**: Investigate technologies, patterns, AWS services, best practices
- **/index**: Map codebase structure, identify patterns, document components

#### Help & Guidance
- **/help**: Access all available commands, agents, modes, and project documentation

### MCP Integrations

Located in `.claude/mcp/`, MCP servers provide external capabilities:

#### Development Tools
- **playwright**: Cross-browser testing, API testing, visual regression, automation
- **chrome-devtools**: Performance profiling, network monitoring, debugging, console access

#### Knowledge & Research
- **context7**: Official AWS/Python/framework documentation, API references, best practices
- **sequential**: Multi-step reasoning, systematic analysis, complex problem-solving

### Behavioral Modes

Located in `.claude/modes/`, modes adapt AI behavior:

#### Creative & Analytical
- **brainstorming**: Divergent thinking, question-driven discovery, creative exploration
- **deep-research**: Thorough investigation, multi-source validation, comprehensive synthesis

#### Operational
- **orchestration**: Parallel execution, efficient tool coordination, batch operations
- **task-management**: Systematic planning, progress tracking, completion verification
- **token-efficiency**: Concise communication, optimized tool usage, 30-50% context savings

## Project-Specific Guidelines

### Architecture Principles

This project follows **hexagonal architecture** (ports and adapters):

```
src/
├── domain/          # Core business logic (models, ports, use cases)
├── adapters/        # External integrations (db, aws, notifiers)
├── entrypoints/     # Application entry points (functions, api)
└── common/          # Shared utilities
```

**Key Rules:**
- Dependencies flow inward toward domain
- Domain has no external dependencies
- Use dependency injection
- Maintain >90% test coverage

### Development Standards

#### Code Quality
- Type hints everywhere (Python 3.13)
- Pydantic v2 for all validation
- Specific exception types (no broad `except Exception`)
- Follow PEP 8 and project conventions

#### Testing
- Unit tests with pytest
- Integration tests with moto
- >90% coverage target
- Test fixtures in `tests/conftest.py`

#### AWS Services
- Lambda (Python 3.13 runtime)
- DynamoDB (single-table design with PynamoDB)
- EventBridge (cross-account event routing)
- API Gateway (REST endpoints)
- CloudWatch Logs Insights

### Common Tasks

#### Add New Event Type
```
1. Domain model (src/domain/models/)
2. Database model (src/adapters/db/models/)
3. Mapper (src/adapters/db/mappers/)
4. Repository method (src/adapters/db/repositories/)
5. Use case (src/domain/use_cases/)
6. Lambda handler (src/entrypoints/functions/)
7. Serverless config (infra/)
8. Tests (tests/)
```

#### Add Notification Channel
```
1. Implement INotifier (src/adapters/notifiers/)
2. Create template (statics/templates/)
3. Update use case to inject notifier
4. Add configuration (src/common/constants.py)
5. Add tests
```

#### Modify Database Schema
```
1. Update domain model (src/domain/models/)
2. Update DB model (src/adapters/db/models/)
3. Update mapper (src/adapters/db/mappers/)
4. Update CloudFormation (infra/master/resources/dynamodb.yml)
5. Write migration if needed
6. Update tests
```

## Configuration

The framework is configured via `.claude/settings.json`:

```json
{
  "agents": {"enabled": true, "auto_select": true},
  "commands": {"enabled": true, "prefix": "/"},
  "mcp": {"enabled": true},
  "modes": {"enabled": true, "auto_select": true}
}
```

### Auto-Selection

Agents and modes are automatically activated based on:
- **Keywords**: Trigger words in user requests
- **Context**: Type of task being performed
- **File patterns**: Files being edited or analyzed
- **Complexity**: Task complexity and scope

You can also explicitly activate:
- Agents: `@agent-name`
- Commands: `/command-name`
- Modes are implicit based on command/context

## File Structure

```
.claude/
├── README.md              # This file
├── settings.json          # Configuration
├── agents/                # Specialized agents
│   ├── backend-architect.md
│   ├── frontend-architect.md
│   ├── python-expert.md
│   ├── refactoring-expert.md
│   ├── repo-index.md
│   ├── requirements-analyst.md
│   ├── root-cause-analyst.md
│   ├── system-architect.md
│   └── technical-writer.md
├── commands/              # Slash commands
│   ├── analyze.md
│   ├── brainstorm.md
│   ├── design.md
│   ├── help.md
│   ├── implement.md
│   ├── index.md
│   ├── research.md
│   └── test.md
├── mcp/                   # MCP integrations
│   ├── chrome-devtools.md
│   ├── context7.md
│   ├── playwright.md
│   └── sequential.md
└── modes/                 # Behavioral modes
    ├── brainstorming.md
    ├── deep-research.md
    ├── orchestration.md
    ├── task-management.md
    └── token-efficiency.md
```

## Best Practices

### 1. Start with Help
```
/help
```
Get familiar with available commands and agents.

### 2. Plan Before Implementing
```
/design new feature
/implement feature
```
Design first, then implement.

### 3. Use Appropriate Agents
```
@backend-architect for AWS architecture
@python-expert for Python optimization
@root-cause-analyst for debugging
```

### 4. Leverage Modes
- Use **task-management** for complex implementations
- Use **token-efficiency** for large codebases
- Use **orchestration** for multi-step tasks
- Use **brainstorming** for creative solutions

### 5. Test Thoroughly
```
/test feature-name
```
Maintain >90% coverage.

### 6. Document Changes
```
@technical-writer update docs for new feature
```

## Troubleshooting

### Command Not Working
- Ensure commands start with `/`
- Check `.claude/settings.json` has `"enabled": true`
- Verify command file exists in `.claude/commands/`

### Agent Not Activating
- Try explicit reference: `@agent-name`
- Check keywords match agent configuration
- Verify `"auto_select": true` in settings

### Mode Not Activating
- Modes activate automatically based on context
- Check mode triggers in settings
- Some modes are implicit (e.g., task-management with TodoWrite)

## Resources

### Project Documentation
- **@CLAUDE.md** - Development guidelines
- **@docs/overview.md** - Architecture overview
- **@docs/project_structure.md** - Codebase structure
- **@docs/db.md** - Database schema
- **@docs/development.md** - Local development
- **@docs/deployment.md** - Deployment guide

### External Resources
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Serverless Framework](https://www.serverless.com/framework/docs)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)

## Contributing

When extending the framework:

### Adding a New Agent
1. Create `[agent-name].md` in `.claude/agents/`
2. Define expertise, responsibilities, and approach
3. Add to `settings.json` with keywords
4. Document in this README

### Adding a New Command
1. Create `[command-name].md` in `.claude/commands/`
2. Add frontmatter with description
3. Add to `settings.json` with usage
4. Update `/help` command

### Adding a New Mode
1. Create `[mode-name].md` in `.claude/modes/`
2. Define characteristics and behavior
3. Add to `settings.json` with triggers
4. Document activation criteria

## Support

For questions or issues:
1. Use `/help` for quick reference
2. Reference project documentation in `docs/`
3. Check `CLAUDE.md` for guidelines
4. Review relevant agent/command/mode documentation

---

**Version**: 1.0.0
**Last Updated**: 2025-11-17
**Framework**: Based on SuperClaude Framework
**Project**: AWS Monitoring (Serverless Multi-Account Monitoring Solution)

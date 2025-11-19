# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Rules

**IMPORTANT**: All behavioral rules, workflow patterns, and quality standards in that file MUST follow rules defined in [.claude/RULES.md](.claude/RULES.md)

## Project Overview

This is a full-stack serverless AWS monitoring application with:
- **Backend**: Python 3.13 serverless backend using hexagonal architecture
- **Frontend**: Vue 3 + TypeScript frontend with Tailwind CSS
- **Infrastructure**: AWS services (Lambda, DynamoDB, EventBridge, CloudWatch)

## Repository Structure

```
aws-monitoring/
├── backend/           # Python backend (serverless, domain-driven design)
│   ├── src/          # Source code (domain, adapters, entrypoints)
│   ├── tests/        # Test files
│   ├── statics/      # Jinja templates for notifications
│   ├── infra/        # Infrastructure as Code (Serverless Framework configs)
│   ├── CLAUDE.md     # 📖 Backend development guide
│   └── ...
├── frontend/         # Vue 3 frontend
│   ├── src/          # Frontend source (pages, components, store, etc.)
│   ├── CLAUDE.md     # 📖 Frontend development guide
│   └── ...
├── ops/             # Operations and deployment scripts
├── docs/            # Documentation
└── Makefile         # Common development commands
```

## Quick Start

### For Backend Development
👉 **See [backend/CLAUDE.md](backend/CLAUDE.md) for detailed backend guide**

```bash
make install        # Install dependencies
make start          # Start LocalStack
make deploy         # Deploy backend
make test           # Run tests
```

### For Frontend Development
👉 **See [frontend/CLAUDE.md](frontend/CLAUDE.md) for detailed frontend guide**

```bash
cd frontend
npm install         # Install dependencies
npm run dev         # Start dev server
npm run test        # Run tests
```

## Core Rules

- At the end of each task, summarize what has been completed and what remains
- **Backend**: Follow hexagonal architecture principles: Domain → Ports → Adapters
- **Frontend**: Follow composition API patterns and single responsibility components
- Maintain test coverage above 90% for both backend and frontend
- Use specific exception types in Python, avoid broad `except Exception` handlers
- All new code must include type hints (Python) and proper TypeScript types (Frontend)
- Use Pydantic validation for backend data models
- Follow Vue 3 Composition API with `<script setup>` syntax in frontend

## Architecture Overview

### Backend (Hexagonal Architecture)

```
backend/src/
├── domain/          # Core business logic (entities, use cases, ports)
├── adapters/        # External integrations (DB, AWS, notifications)
├── entrypoints/     # Entry points (Lambda handlers, API Gateway)
└── common/          # Shared utilities
```

**Key principle**: Dependencies flow inward toward the domain layer.

### Frontend (Layered Architecture)

```
frontend/src/
├── core/            # Domain layer (types, enums, constants)
├── api/             # Infrastructure layer (HTTP client, API services)
├── store/           # Application layer (Pinia stores)
├── composables/     # Application layer (reusable composition functions)
├── components/      # Presentation layer (UI components)
└── pages/           # Presentation layer (route entry points)
```

**Key principle**: Clear separation between domain, application, and presentation layers.

## Common Commands

### Development

```bash
# Full stack
make install                    # Install all dependencies
make start                      # Start backend (LocalStack)
cd frontend && npm run dev      # Start frontend

# Backend only
make test                       # Run backend tests
make coverage                   # Generate coverage report
make mon                        # Launch monitoring profile manager

# Frontend only
cd frontend
npm run test                    # Run frontend tests
npm run lint                    # Lint code
npm run type-check              # Check TypeScript types
```

### Deployment

```bash
make deploy stage=local         # Deploy to local (default)
make deploy stage=dev           # Deploy to dev
make package stage=prod         # Package for production
make destroy stage=local        # Destroy deployment
make bootstrap stage=dev        # Bootstrap S3 and IAM
```

## Development Workflows

### Full-Stack Development

1. **Start Backend**:
   ```bash
   make start        # Start LocalStack
   make deploy       # Deploy backend (stage=local)
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev       # http://localhost:3000
   ```

3. **Run Tests**:
   ```bash
   make test                     # Backend tests
   cd frontend && npm run test   # Frontend tests
   ```

### Backend-Only Development

```bash
make install      # Install dependencies
make start        # Start LocalStack
make deploy       # Deploy backend
make test         # Run tests
```

See [backend/CLAUDE.md](backend/CLAUDE.md) for detailed backend workflows.

### Frontend-Only Development

```bash
cd frontend
npm install       # Install dependencies
npm run dev       # Start dev server
npm run test      # Run tests
npm run lint      # Lint code
```

See [frontend/CLAUDE.md](frontend/CLAUDE.md) for detailed frontend workflows.

## Git Workflow

### Branch Naming

- Feature: `feat/feature-name`
- Bug fix: `fix/bug-description`
- Refactor: `refactor/what-changed`
- Documentation: `docs/what-documented`
- Claude Code: `claude/task-description-{sessionId}`

### Commit Messages

Follow conventional commits:
```
feat: add event filtering by severity
fix: resolve timezone issue in event timestamps
refactor: reorganize backend structure
docs: update API documentation
test: add tests for event repository
chore: update dependencies
```

## Documentation

### Backend Documentation
- **Development Guide**: [backend/CLAUDE.md](backend/CLAUDE.md)
- Project structure: [docs/project_structure.md](docs/project_structure.md)
- Database schema: [docs/db.md](docs/db.md)
- Architecture overview: [docs/overview.md](docs/overview.md)
- Deployment guide: [docs/deployment.md](docs/deployment.md)

### Frontend Documentation
- **Development Guide**: [frontend/CLAUDE.md](frontend/CLAUDE.md)
- Frontend overview: [docs/frontend-overview.md](docs/frontend-overview.md)
- Quick start: [docs/frontend-quick-start.md](docs/frontend-quick-start.md)
- Design documentation: [docs/frontend-design.md](docs/frontend-design.md)
- Implementation guide: [docs/frontend-implementation-guide.md](docs/frontend-implementation-guide.md)
- Types reference: [docs/frontend-types-reference.md](docs/frontend-types-reference.md)

### API Documentation
- API specification: [docs/api-specification.yaml](docs/api-specification.yaml)
- Screen-API mapping: [docs/screen-api-mapping.md](docs/screen-api-mapping.md)

## Quick Reference

### Key File Locations

- **Backend source**: `backend/src/`
- **Frontend source**: `frontend/src/`
- **Infrastructure**: `backend/infra/`
- **Tests**: `backend/tests/`, `frontend/src/__tests__/`
- **Documentation**: `docs/`
- **Configuration**: `backend/pyproject.toml`, `frontend/package.json`
- **Environment**: `backend/.env.local`, `frontend/.env.development`

### Common Issues

#### Backend Issues
- **Poetry issues**: Delete `.venv` and run `make install`
- **LocalStack not starting**: Check Docker, restart with `docker compose restart localstack`
- **Import errors**: Ensure virtual environment is activated
- **Test failures**: Check LocalStack is running

See [backend/CLAUDE.md](backend/CLAUDE.md) for detailed troubleshooting.

#### Frontend Issues
- **Dependency conflicts**: Delete `node_modules` and `package-lock.json`, run `npm install`
- **Type errors**: Run `npm run type-check` to see all type issues
- **Build failures**: Check for missing environment variables
- **API connection issues**: Verify backend is running on expected port

See [frontend/CLAUDE.md](frontend/CLAUDE.md) for detailed troubleshooting.

## Tech Stack Summary

### Backend
- Python 3.13, Serverless Framework 4.x
- DynamoDB (PynamoDB ORM), AWS Lambda, EventBridge
- Pydantic v2.11.0, Pytest, Moto, LocalStack

### Frontend
- Vue 3, TypeScript 5.9, Vite 7.x
- Pinia 3.x, Vue Router 4.x, Tailwind CSS 3.x
- Axios, Vitest, Vue Test Utils

### Infrastructure
- AWS (Lambda, DynamoDB, EventBridge, CloudWatch, SNS, S3)
- Serverless Framework with CloudFormation
- Docker, LocalStack (local development)

## Additional Resources

For detailed development guides:
- 📖 **Backend**: [backend/CLAUDE.md](backend/CLAUDE.md)
- 📖 **Frontend**: [frontend/CLAUDE.md](frontend/CLAUDE.md)
- 📚 **Documentation**: [docs/](docs/)

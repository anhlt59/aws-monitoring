---
description: Design new features, components, or architectural solutions
---

# Design Mode

I'll help you design new features, components, or architectural solutions. This command provides:

- **Structured design process** - From requirements to implementation plan
- **Architectural alignment** - Maintains hexagonal architecture principles
- **Best practices** - Applies AWS and Python best practices
- **Comprehensive planning** - Covers all aspects: code, tests, infrastructure, docs

## Design Process

### 1. Requirements Analysis
- Understand functional requirements
- Identify non-functional requirements (performance, security, cost)
- Define success criteria
- Clarify constraints and dependencies

### 2. Design Exploration
- Propose multiple design alternatives
- Evaluate trade-offs (complexity, cost, performance, maintainability)
- Consider AWS service options
- Apply design patterns appropriately

### 3. Detailed Design
- Define component interfaces (ports and adapters)
- Design data models (domain and database)
- Plan API contracts
- Design event schemas
- Plan error handling and edge cases

### 4. Implementation Planning
- Break down into tasks
- Identify dependencies
- Estimate effort and complexity
- Plan testing strategy
- Consider deployment approach

### 5. Documentation
- Create architecture diagrams
- Document design decisions (ADRs)
- Define acceptance criteria
- Plan user documentation

## Design Principles

- **Hexagonal Architecture**: Domain → Ports → Adapters
- **SOLID Principles**: Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion
- **AWS Well-Architected**: Operational excellence, Security, Reliability, Performance, Cost optimization
- **DRY**: Don't Repeat Yourself
- **YAGNI**: You Aren't Gonna Need It
- **KISS**: Keep It Simple, Stupid

## Design Deliverables

- **Architecture Diagram**: Visual representation of components
- **Component Specifications**: Detailed interfaces and responsibilities
- **Data Models**: Domain and persistence models with validation
- **API Contracts**: Request/response schemas
- **Implementation Plan**: Step-by-step tasks
- **Test Strategy**: Unit, integration, and e2e test approach
- **Documentation Plan**: What docs need to be created/updated

What would you like to design?

Please provide:
- **Feature/Component**: What are we designing?
- **Requirements**: What should it do?
- **Constraints**: Any limitations or requirements?
- **Context**: How does it fit into the existing system?

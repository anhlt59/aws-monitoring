# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository

## Rules

- At the end of each task, summarize what has been completed and what remains

## Commands

- `make install` - Install all dependencies (Python via Poetry, Node.js packages)
- `make activate` - Activate the Python virtual environment
- `make test` - Run tests with pytest (including coverage reporting)
- `make coverage` - Generate an HTML coverage report and update the README badge
- `make start` - Start the LocalStack container for local AWS services
- `make start-master` / `make start-agent` - Start the local serverless stacks
- `make deploy-local` - Deploy both master and agent stacks to LocalStack

## Tech Stack

- Backend: Python 3.13, Serverless Framework
- Database: DynamoDB
- Infrastructure: AWS (Lambda, API Gateway, EventBridge, SNS, S3, CloudWatch)
- Testing: Pytest, Coverage
- Local Development: LocalStack, Docker

## Architecture

This is a serverless AWS monitoring application built using hexagonal architecture (ports and adapters pattern) with clean separation of concerns:

### Core Architecture Layers

#### Domain Layer (`src/domain/`)
- **Models**: Core business entities (Event, Agent) with domain logic
- **Ports**: Interfaces defining contracts for external dependencies (repositories, notifiers, publishers)
- **Use Cases**: Business logic orchestration (daily_report, insert_monitoring_event, query_error_logs, update_deployment)

#### Adapters Layer (`src/adapters/`)
- **Database**: DynamoDB repositories, models, and mappers for data persistence
- **AWS Services**: CloudWatch, EventBridge, Lambda function abstractions
- **External Services**: Notifiers (Slack, etc.), log adapters, event publishers

#### Entry Points (`src/entrypoints/`)
- **Functions**: Lambda function handlers for business operations
- **API Gateway**: REST API endpoints for agents and events

#### Common Layer (`src/common/`)
- Shared utilities, configurations, logger, exceptions, and cross-cutting concerns

### Deployment Architecture

The application consists of two serverless stacks:

#### Master Stack
- Central monitoring system deployed once
- Processes monitoring events, sends notifications, provides APIs
- Lambda functions: HandleMonitoringEvents, UpdateDeployment, DailyReport
- API Gateway endpoints for agent management and event querying

#### Agent Stack
- Deployed to each monitored AWS account
- Queries CloudWatch logs and publishes events to master stack
- Lambda function: QueryErrorLogs

### Infrastructure (`infra/`)

- Serverless Framework configuration split by stack (master/agent) with environment-specific configs
- CloudFormation templates for IAM, EventBridge, DynamoDB, and SQS

## Additional Instructions

- Project structure: @docs/project_structure.md
- Database schema: @docs/db.md

## Development Notes

- Python 3.13 + Poetry, with pre-commit hooks (ruff, isort, bandit)
- Test structure mirrors the source code in `tests/`

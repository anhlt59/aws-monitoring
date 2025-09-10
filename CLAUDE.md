# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Instructions

- Always respond in English, starting with "Hi, boss".
- At the end of each task, summarize what has been completed and what remains.

## Commands

- `make install` - Install all dependencies (Python via Poetry, Node.js packages)
- `make activate` - Activate the Python virtual environment
- `make test` - Run tests with pytest (including coverage reporting)
- `make coverage` - Generate an HTML coverage report and update the README badge
- `make start` - Start the LocalStack container for local AWS services
- `make start-master` / `make start-agent` - Start the local serverless stacks
- `make deploy-local` - Deploy both master and agent stacks to LocalStack

## Tech Stack

- Backend: Python 3.12, Serverless Framework
- Database: DynamoDB
- Infrastructure: AWS (Lambda, API Gateway, EventBridge, SNS, S3, CloudWatch)
- Testing: Pytest, Coverage
- Local Development: LocalStack, Docker

## Architecture

This is a serverless AWS monitoring application with two main components:

### Master Stack (`src/modules/master/`)

- Central monitoring system deployed once
- Handles event processing, notifications, API endpoints, and stores data in DynamoDB
- Contains handlers:
  - `HandleMonitoringEvents` - Process incoming monitoring events
  - `UpdateDeployment` - Manage deployment updates
  - `DailyReport` - Generate daily monitoring reports
  - API endpoints for agents and events (currently commented out)

### Agent Stack (`src/modules/agent/`)

- Deployed to each monitored AWS account
- Queries logs and publishes events to the master stack
- Contains handlers:
  - `QueryErrorLogs` - Query CloudWatch logs for errors

### Infrastructure (`infra/`)

- Serverless Framework configuration split by stack (master/agent) with environment-specific configs
- CloudFormation templates for IAM, EventBridge, DynamoDB, and SQS

## Additional Instructions

- Project structure: @docs/project_structure.md
- Database schema: @docs/db.md

## Development Notes

- Python 3.12 + Poetry, with pre-commit hooks (ruff, isort, bandit)
- Test structure mirrors the source code in `tests/`

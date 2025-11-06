# Refactor: Multi-account → Single-account

This folder contains a planned, step-by-step refactor to migrate the project from a multi-AWS-account architecture (master + agents) to a single AWS account architecture.

Goals
- Simplify deployment and operations by consolidating master and agent stacks into a single account.
- Remove cross-account IAM roles, cross-account EventBridge configuration, and agent stacks.
- Keep existing business logic and domain boundaries; adapt only the infrastructure and entrypoints.

Usage
- Read `tasks.md` for a detailed task breakdown, priorities, estimates, and file targets.
- Follow the checklist in `tasks.md` and update task statuses in the file as you progress.

Assumptions
- Current codebase uses Serverless Framework with separate `serverless.master*.yml` and `serverless.agent*.yml` configs.
- Tests and CI currently reference both master and agent stacks; they will be updated incrementally.
- No irreversible data migrations are required; DynamoDB table will remain but access paths may change.

Next action
- Open `docs/refactor/tasks.md` for the full task list and start with Task 01: Assessment & tests.


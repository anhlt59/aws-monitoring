# Refactor Tasks: Convert to Single AWS Account

This document breaks the refactor into small, testable tasks with priorities, estimates, affected files, and acceptance criteria. Update this file as you complete tasks (mark status: TODO / IN-PROGRESS / DONE).

Format for each task:
- ID: short id
- Title
- Priority: High / Medium / Low
- Estimate: hours
- Description: what to change and why
- Files to change: list of paths (where applicable)
- Tests: unit/integration tests to add or update
- Acceptance criteria: how to validate the task is complete

---

## Task 01 - Assessment & baseline tests
- ID: T01
- Title: Run full test suite and collect failing tests
- Priority: High
- Estimate: 0.5h
- Description: Run `make test` to get a baseline. Record failures related to multi-account assumptions.
- Files to change: none (read only)
- Tests: N/A
- Acceptance criteria: Test run output saved to `docs/refactor/baseline-tests.txt` and T01 marked DONE.
---

## Task 02 - Consolidate serverless configs
- ID: T02
- Title: Merge `serverless.master*.yml` and `serverless.agent*.yml` into a single `serverless.yml`
- Priority: High
- Estimate: 3h
- Description: Create a unified `serverless.yml` that contains all resources and functions previously split between master and agents. Remove cross-account event permissions and roles.
- Files to change:
  - `serverless.master.yml` (read-only, references preserved)
  - `serverless.master.local.yml`
  - `serverless.agent.yml`
  - `serverless.agent.local.yml`
  - Added `serverless.yml` at project root (created)
  - Created `infra/resources/merged_manifest.yml` and `infra/resources/README.md`
- Tests:
  - Lint serverless configs (YAML syntax)
  - Run `serverless package` locally (if possible)
- Acceptance criteria: `serverless.yml` exists, infra fragments are staged for merge under `infra/resources/`, and old serverless files are still present as backups.
- Status: IN-PROGRESS
- Changes made: Created `serverless.yml`, `infra/resources/README.md`, and `infra/resources/merged_manifest.yml` as migration scaffolding.

---

## Task 03 - Remove cross-account IAM roles and policies
- ID: T03
- Title: Remove cross-account IAM role usage and assume-role patterns
- Priority: High
- Estimate: 2h
- Description: Find code and configs that create or assume cross-account roles (used by agents) and remove/adjust them to operate in the same account.
- Files to change (likely):
  - `infra/` (search for `Role`, `AssumeRole`, `sts:AssumeRole`)
  - `src/adapters/aws/` (code that assumes roles)
- Tests:
  - Unit tests for AWS adapter code to mock credentials
- Acceptance criteria: No code references to cross-account role ARNs or STS assume-role calls.

---

## Task 04 - Consolidate EventBridge topics/rules
- ID: T04
- Title: Use single-account EventBridge bus and rules
- Priority: High
- Estimate: 2h
- Description: Replace cross-account EventBridge event buses and rules with a single bus and rules in `serverless.yml` and update relevant code and resource names.
- Files to change:
  - `infra/master/` and `infra/agent/` eventbridge templates
  - `serverless.*.yml`
  - `src/adapters/aws/eventbridge.py`
- Tests:
  - Unit tests for event publishing (mock EventBridge)
- Acceptance criteria: Event publishing happens to the same account; no cross-account event bus references.

---

## Task 05 - Remove agent stack, merge agent functions into master stack
- ID: T05
- Title: Move agent Lambda functions into the main stack
- Priority: High
- Estimate: 4h
- Description: Move agent functions (e.g., `QueryErrorLogs`) into the unified stack. Update IAM roles and environment variables accordingly.
- Files to change:
  - `infra/agent/*` (remove/merge resources)
  - `src/entrypoints/functions/*` (ensure handlers are registered in `serverless.yml`)
- Tests:
  - Integration test to invoke former agent functions locally
- Acceptance criteria: Agent functions are available in the single stack and can be invoked.

---

## Task 06 - Update deployment and CI scripts
- ID: T06
- Title: Update `Makefile` and CI to deploy a single stack
- Priority: Medium
- Estimate: 1.5h
- Description: Modify `Makefile` targets and CI configs to reflect the single-stack deploy flow.
- Files to change:
  - `Makefile`
  - Any CI config (not in repo?)
- Tests:
  - Run `make deploy-local` or equivalent dry-run
- Acceptance criteria: Build and deploy commands work against single account setup.

---

## Task 07 - Update tests and mocks
- ID: T07
- Title: Remove multi-account test fixtures and update mocks
- Priority: High
- Estimate: 3h
- Description: Update the test suite to remove multi-account fixtures and adjust mocks to single account resources.
- Files to change:
  - `tests/conftest.py`
  - `tests/**/` fixtures referencing agent/master separation
- Tests:
  - Ensure full test suite passes
- Acceptance criteria: `make test` passes; coverage >= previous baseline.

---

## Task 08 - Update documentation and architecture diagrams
- ID: T08
- Title: Update docs to reflect single-account design
- Priority: Medium
- Estimate: 2h
- Description: Update `docs/` files that mention master/agent separation, diagrams, and any cross-account steps.
- Files to change:
  - `docs/overview.md`
  - `docs/deployment.md`
  - `README.md`
- Tests:
  - Manual review of docs
- Acceptance criteria: No doc mentions of master/agent cross-account architecture remain.

---

## Task 09 - Deprecate agent infra and clean-up
- ID: T09
- Title: Delete agent infra and related artifacts
- Priority: Low
- Estimate: 1h
- Description: Remove agent-specific artifacts, backups kept in `infra/agent/backup/`.
- Files to change:
  - Remove `infra/agent/` after verification
- Tests:
  - Confirm no build errors
- Acceptance criteria: No references to `infra/agent/` remain.

---

## Task 10 - Run end-to-end smoke test in a sandbox account
- ID: T10
- Title: E2E deploy & smoke test
- Priority: High
- Estimate: 3h
- Description: Deploy unified stack to a sandbox AWS account and run integration smoke tests covering event ingestion, DB writes, and notifications.
- Files to change: None
- Tests:
  - A set of smoke test scripts (add `tests/e2e/smoke.md`)
- Acceptance criteria: Smoke tests pass and logs show single-account operation.

---

# Next steps
1. Run Task T01 and save the baseline test output to `docs/refactor/baseline-tests.txt`.
2. Tackle T02 (serverless merge) and T03 (IAM cleanup) together.
3. Keep this `docs/refactor/tasks.md` updated as tasks progress.

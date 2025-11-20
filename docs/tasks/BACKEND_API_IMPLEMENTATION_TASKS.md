# Backend API Implementation - Task Checklist

Track progress on implementing missing backend API endpoints.

---

## Phase 1: Authentication API (Critical Priority)

**Goal:** Enable user login and authentication
**Timeline:** Week 1-2
**Estimated Effort:** 40-60 hours

### Task 1.1: Set Up Authentication Infrastructure
- [ ] Add dependencies to `pyproject.toml`
  - [ ] pyjwt ^2.8.0
  - [ ] bcrypt ^4.1.2
  - [ ] passlib ^1.7.4
- [ ] Run `poetry lock && poetry install`
- [ ] Create `.env` configuration for JWT secret
- [ ] Update DynamoDB schema in `backend/infra/resources/dynamodb.yml`
  - [ ] Add User table configuration
  - [ ] Add email-index GSI
  - [ ] Add role-index GSI

### Task 1.2: Create Domain Models
- [ ] Create `backend/src/domain/entities/user.py`
  - [ ] Define User dataclass with fields
  - [ ] Add UserRole enum (admin, manager, user)
  - [ ] Add validation methods
- [ ] Create `backend/src/domain/value_objects/password.py`
  - [ ] Password strength validation
  - [ ] Password hashing wrapper

### Task 1.3: Create Core Services
- [ ] Create `backend/src/adapters/services/password_service.py`
  - [ ] `hash_password(plain: str) -> str`
  - [ ] `verify_password(plain: str, hashed: str) -> bool`
  - [ ] Add tests
- [ ] Create `backend/src/adapters/services/jwt_service.py`
  - [ ] `generate_access_token(user_id: str, role: str) -> str`
  - [ ] `generate_refresh_token(user_id: str) -> str`
  - [ ] `verify_token(token: str) -> dict`
  - [ ] `decode_token(token: str) -> dict`
  - [ ] Add tests

### Task 1.4: Create User Repository
- [ ] Create `backend/src/adapters/repositories/user_repository.py`
  - [ ] `get_by_id(user_id: str) -> Optional[User]`
  - [ ] `get_by_email(email: str) -> Optional[User]`
  - [ ] `create(user: User) -> User`
  - [ ] `update(user: User) -> User`
  - [ ] `delete(user_id: str) -> None`
  - [ ] `list_users(filters: dict) -> List[User]`
- [ ] Add integration tests with LocalStack

### Task 1.5: Create Authentication Use Cases
- [ ] Create `backend/src/domain/use_cases/auth/login.py`
  - [ ] Validate credentials
  - [ ] Generate tokens
  - [ ] Update last_login timestamp
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/auth/logout.py`
  - [ ] Invalidate refresh token
  - [ ] Add to token blacklist
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/auth/get_profile.py`
  - [ ] Fetch user by ID
  - [ ] Return user profile
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/auth/refresh_token.py`
  - [ ] Verify refresh token
  - [ ] Generate new access token
  - [ ] Add unit tests

### Task 1.6: Create API Gateway Handlers
- [ ] Create `backend/src/entrypoints/apigw/auth/login_handler.py`
  - [ ] POST /api/auth/login handler
  - [ ] Request validation
  - [ ] Response formatting
  - [ ] Error handling
- [ ] Create `backend/src/entrypoints/apigw/auth/logout_handler.py`
  - [ ] POST /api/auth/logout handler
- [ ] Create `backend/src/entrypoints/apigw/auth/profile_handler.py`
  - [ ] GET /api/auth/me handler
  - [ ] Require authentication
- [ ] Create `backend/src/entrypoints/apigw/auth/refresh_handler.py`
  - [ ] POST /api/auth/refresh handler

### Task 1.7: Create Authentication Middleware
- [ ] Create `backend/src/entrypoints/apigw/middleware/auth_middleware.py`
  - [ ] Extract token from Authorization header
  - [ ] Verify token
  - [ ] Add user context to request
  - [ ] Handle token expiration
- [ ] Create decorator `@require_auth`
- [ ] Create decorator `@require_role(['admin'])`

### Task 1.8: Configure Serverless
- [ ] Create `backend/infra/functions/auth.yml`
  - [ ] Define auth Lambda functions
  - [ ] Configure API Gateway routes
  - [ ] Set environment variables
  - [ ] Configure CORS
- [ ] Update `backend/infra/functions/serverless.yml`
  - [ ] Include auth.yml
  - [ ] Configure API Gateway authorizer

### Task 1.9: Testing & Documentation
- [ ] Create seed script for initial admin user
  - [ ] File: `backend/scripts/seed_admin_user.py`
- [ ] Write integration tests
  - [ ] Test login flow
  - [ ] Test token refresh
  - [ ] Test protected routes
- [ ] Update API documentation
  - [ ] Add auth endpoints to `docs/api-specification.yaml`
- [ ] Create user guide
  - [ ] How to create initial admin
  - [ ] How to reset passwords

### Task 1.10: Deployment & Validation
- [ ] Deploy to local environment
  - [ ] `make deploy stage=local`
  - [ ] Verify DynamoDB tables created
- [ ] Test with frontend
  - [ ] Login page works
  - [ ] Token storage works
  - [ ] Protected routes work
- [ ] Deploy to dev environment
  - [ ] `make deploy stage=dev`

---

## Phase 2: Events API (High Priority)

**Goal:** Complete events API functionality
**Timeline:** Week 2
**Estimated Effort:** 8-12 hours

### Task 2.1: Enable Existing Endpoints
- [ ] Uncomment events API in `backend/infra/functions/serverless.yml`
  - [ ] Lines 78-86
- [ ] Deploy and test
  - [ ] `make deploy stage=local`
  - [ ] Test GET /api/events
  - [ ] Test GET /api/events/{id}

### Task 2.2: Implement Delete Event
- [ ] Create `backend/src/domain/use_cases/events/delete_event.py`
  - [ ] Soft delete logic (add deleted_at field)
  - [ ] Authorization check
  - [ ] Add unit tests
- [ ] Create `backend/src/entrypoints/apigw/events/delete_event_handler.py`
  - [ ] DELETE /api/events/{id} handler
  - [ ] Require admin role
- [ ] Update `backend/infra/functions/events.yml`
  - [ ] Add DELETE route
- [ ] Test with frontend

### Task 2.3: Implement Create Task from Event
- [ ] Create `backend/src/domain/use_cases/events/create_task_from_event.py`
  - [ ] Extract event details
  - [ ] Create task with event reference
  - [ ] Add unit tests
- [ ] Create `backend/src/entrypoints/apigw/events/create_task_handler.py`
  - [ ] POST /api/events/{id}/create-task handler
- [ ] Update `backend/infra/functions/events.yml`
  - [ ] Add POST route
- [ ] Test with frontend

---

## Phase 3: Tasks API (High Priority)

**Goal:** Implement complete task management system
**Timeline:** Week 3-4
**Estimated Effort:** 35-45 hours

### Task 3.1: Create Domain Models
- [ ] Create `backend/src/domain/entities/task.py`
  - [ ] Define Task dataclass
  - [ ] Add TaskStatus enum (open, in_progress, closed)
  - [ ] Add TaskPriority enum (critical, high, medium, low)
  - [ ] Add validation methods
- [ ] Create `backend/src/domain/entities/task_comment.py`
  - [ ] Define TaskComment dataclass
  - [ ] Add validation methods

### Task 3.2: Create Task Repository
- [ ] Create `backend/src/adapters/repositories/task_repository.py`
  - [ ] `get_by_id(task_id: str) -> Optional[Task]`
  - [ ] `list_tasks(filters: TaskFilters) -> PaginatedResult`
  - [ ] `create(task: Task) -> Task`
  - [ ] `update(task: Task) -> Task`
  - [ ] `delete(task_id: str) -> None`
  - [ ] `add_comment(comment: TaskComment) -> TaskComment`
  - [ ] `get_comments(task_id: str) -> List[TaskComment]`
- [ ] Add integration tests

### Task 3.3: Create Task Use Cases
- [ ] Create `backend/src/domain/use_cases/tasks/list_tasks.py`
  - [ ] Filter by status, priority, assigned_user, dates
  - [ ] Pagination support
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/tasks/get_task.py`
  - [ ] Fetch task with comments
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/tasks/create_task.py`
  - [ ] Validate input
  - [ ] Set created_by from auth context
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/tasks/update_task.py`
  - [ ] Validate permissions
  - [ ] Update allowed fields
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/tasks/delete_task.py`
  - [ ] Soft delete
  - [ ] Authorization check
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/tasks/add_comment.py`
  - [ ] Add comment with user context
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/tasks/update_status.py`
  - [ ] Update task status
  - [ ] Track status history
  - [ ] Add unit tests

### Task 3.4: Create API Gateway Handlers
- [ ] Create `backend/src/entrypoints/apigw/tasks/list_tasks_handler.py`
  - [ ] GET /api/tasks handler
  - [ ] Query parameter parsing
- [ ] Create `backend/src/entrypoints/apigw/tasks/get_task_handler.py`
  - [ ] GET /api/tasks/{id} handler
- [ ] Create `backend/src/entrypoints/apigw/tasks/create_task_handler.py`
  - [ ] POST /api/tasks handler
  - [ ] Request validation
- [ ] Create `backend/src/entrypoints/apigw/tasks/update_task_handler.py`
  - [ ] PUT /api/tasks/{id} handler
- [ ] Create `backend/src/entrypoints/apigw/tasks/delete_task_handler.py`
  - [ ] DELETE /api/tasks/{id} handler
  - [ ] Require appropriate permissions
- [ ] Create `backend/src/entrypoints/apigw/tasks/add_comment_handler.py`
  - [ ] POST /api/tasks/{id}/comments handler
- [ ] Create `backend/src/entrypoints/apigw/tasks/update_status_handler.py`
  - [ ] PUT /api/tasks/{id}/status handler

### Task 3.5: Configure Serverless
- [ ] Create `backend/infra/functions/tasks.yml`
  - [ ] Define all task Lambda functions
  - [ ] Configure API Gateway routes
  - [ ] Set permissions
- [ ] Update DynamoDB schema
  - [ ] Add Task table configuration
  - [ ] Add TaskComment table configuration
  - [ ] Add necessary GSIs

### Task 3.6: Testing & Deployment
- [ ] Write integration tests
- [ ] Update API documentation
- [ ] Deploy to local
- [ ] Test with frontend
- [ ] Deploy to dev

---

## Phase 4: Users API (High Priority)

**Goal:** Implement user management for admins
**Timeline:** Week 5
**Estimated Effort:** 25-35 hours

### Task 4.1: Create User Management Use Cases
- [ ] Create `backend/src/domain/use_cases/users/list_users.py`
  - [ ] Filter by role, active status, search
  - [ ] Require admin/manager role
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/users/get_user.py`
  - [ ] Fetch user details
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/users/create_user.py`
  - [ ] Require admin role
  - [ ] Generate initial password or send invite
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/users/update_user.py`
  - [ ] Update user fields
  - [ ] Validate permissions
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/users/delete_user.py`
  - [ ] Soft delete/deactivate
  - [ ] Require admin role
  - [ ] Add unit tests

### Task 4.2: Create API Gateway Handlers
- [ ] Create `backend/src/entrypoints/apigw/users/list_users_handler.py`
  - [ ] GET /api/users handler
  - [ ] Require admin/manager role
- [ ] Create `backend/src/entrypoints/apigw/users/get_user_handler.py`
  - [ ] GET /api/users/{id} handler
- [ ] Create `backend/src/entrypoints/apigw/users/create_user_handler.py`
  - [ ] POST /api/users handler
  - [ ] Require admin role
- [ ] Create `backend/src/entrypoints/apigw/users/update_user_handler.py`
  - [ ] PUT /api/users/{id} handler
- [ ] Create `backend/src/entrypoints/apigw/users/delete_user_handler.py`
  - [ ] DELETE /api/users/{id} handler
  - [ ] Require admin role

### Task 4.3: Configure & Deploy
- [ ] Create `backend/infra/functions/users.yml`
- [ ] Add RBAC validation
- [ ] Write tests
- [ ] Deploy and test with frontend

---

## Phase 5: Dashboard API (Medium Priority)

**Goal:** Provide dashboard statistics
**Timeline:** Week 6
**Estimated Effort:** 16-24 hours

### Task 5.1: Create Dashboard Use Cases
- [ ] Create `backend/src/domain/use_cases/dashboard/get_overview.py`
  - [ ] Aggregate all statistics
  - [ ] Add caching if needed
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/dashboard/get_event_stats.py`
  - [ ] Count by severity
  - [ ] Count by source
  - [ ] Recent events
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/dashboard/get_task_stats.py`
  - [ ] Count by status
  - [ ] Count by priority
  - [ ] My tasks count
  - [ ] Add unit tests
- [ ] Create `backend/src/domain/use_cases/dashboard/get_user_stats.py`
  - [ ] Total users
  - [ ] Active users
  - [ ] Count by role
  - [ ] Add unit tests

### Task 5.2: Create API Gateway Handlers
- [ ] Create `backend/src/entrypoints/apigw/dashboard/overview_handler.py`
  - [ ] GET /api/dashboard/overview handler
- [ ] Create `backend/src/entrypoints/apigw/dashboard/event_stats_handler.py`
  - [ ] GET /api/dashboard/events-stats handler
- [ ] Create `backend/src/entrypoints/apigw/dashboard/task_stats_handler.py`
  - [ ] GET /api/dashboard/tasks-stats handler
- [ ] Create `backend/src/entrypoints/apigw/dashboard/user_stats_handler.py`
  - [ ] GET /api/dashboard/users-stats handler

### Task 5.3: Optimize Queries
- [ ] Create efficient DynamoDB queries
- [ ] Add caching layer (optional)
- [ ] Add tests
- [ ] Deploy

---

## Phase 6: Configuration API (Medium Priority)

**Goal:** Manage AWS accounts and monitoring settings
**Timeline:** Week 7-8
**Estimated Effort:** 32-48 hours

### Task 6.1: Refactor Agents to AWS Accounts
- [ ] Rename `backend/src/domain/entities/agent.py` to `aws_account.py`
- [ ] Update all references
- [ ] Update repository methods

### Task 6.2: Create AWS Account Use Cases
- [ ] Create `backend/src/domain/use_cases/aws_accounts/list_accounts.py`
- [ ] Create `backend/src/domain/use_cases/aws_accounts/get_account.py`
- [ ] Create `backend/src/domain/use_cases/aws_accounts/create_account.py`
- [ ] Create `backend/src/domain/use_cases/aws_accounts/update_account.py`
- [ ] Create `backend/src/domain/use_cases/aws_accounts/delete_account.py`
- [ ] Create `backend/src/domain/use_cases/aws_accounts/test_connection.py`
  - [ ] Use boto3 STS to verify credentials
  - [ ] Add unit tests

### Task 6.3: Create Monitoring Config
- [ ] Create `backend/src/domain/entities/monitoring_config.py`
- [ ] Create `backend/src/adapters/repositories/config_repository.py`
- [ ] Create `backend/src/domain/use_cases/config/get_monitoring_config.py`
- [ ] Create `backend/src/domain/use_cases/config/update_monitoring_config.py`

### Task 6.4: Create API Handlers
- [ ] Create AWS accounts handlers
- [ ] Create monitoring config handlers
- [ ] Create `backend/infra/functions/config.yml`

### Task 6.5: Deploy & Test
- [ ] Update DynamoDB schema
- [ ] Add tests
- [ ] Deploy
- [ ] Test with frontend

---

## Testing Checklist

For each endpoint, ensure:

- [ ] Unit tests for use cases
- [ ] Integration tests for handlers
- [ ] E2E tests for critical flows
- [ ] Error handling tests
- [ ] Authorization tests
- [ ] Validation tests

---

## Documentation Checklist

- [ ] Update OpenAPI spec (`docs/api-specification.yaml`)
- [ ] Update README with new endpoints
- [ ] Document authentication flow
- [ ] Document RBAC permissions
- [ ] Add API usage examples
- [ ] Update deployment guide

---

## Deployment Checklist

For each phase:

- [ ] Update dependencies in `pyproject.toml`
- [ ] Update DynamoDB schema
- [ ] Update serverless.yml
- [ ] Run `make deploy stage=local`
- [ ] Test locally with frontend
- [ ] Run test suite
- [ ] Run `make deploy stage=dev`
- [ ] Smoke test in dev
- [ ] Create PR and get review
- [ ] Merge to main
- [ ] Deploy to production (when ready)

---

## Progress Tracking

**Phase 1 (Authentication):** ⬜ Not Started
**Phase 2 (Events):** ⬜ Not Started
**Phase 3 (Tasks):** ⬜ Not Started
**Phase 4 (Users):** ⬜ Not Started
**Phase 5 (Dashboard):** ⬜ Not Started
**Phase 6 (Configuration):** ⬜ Not Started

---

## Notes

- Each task should be a separate commit
- Create feature branches for each phase
- Keep PRs small and reviewable
- Run tests before committing
- Update documentation as you go

---

**Last Updated:** 2025-11-20
**Status:** Ready for Implementation

# Missing Backend API Endpoints - Implementation Tasks

## Overview

This document lists all API endpoints that the frontend expects but are not yet implemented in the backend.

**Status Summary:**
- ✅ **Partially Implemented**: 2 endpoints (events GET operations)
- ❌ **Missing**: 31 endpoints
- **Total Required**: 33 endpoints

---

## 1. Authentication API (4 endpoints)

**Priority: CRITICAL** - Required for app to function

### Endpoints:

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/api/auth/login` | User login with email/password | ❌ Missing |
| POST | `/api/auth/logout` | User logout | ❌ Missing |
| GET | `/api/auth/me` | Get current user profile | ❌ Missing |
| POST | `/api/auth/refresh` | Refresh access token | ❌ Missing |

### Implementation Steps:

1. **Create User domain model**
   - File: `backend/src/domain/entities/user.py`
   - Fields: id, email, password_hash, full_name, role, is_active, created_at, last_login
   - Roles: admin, manager, user

2. **Create authentication use cases**
   - File: `backend/src/domain/use_cases/auth/`
   - `login.py` - Authenticate user, generate JWT tokens
   - `logout.py` - Invalidate refresh token
   - `get_profile.py` - Retrieve current user
   - `refresh_token.py` - Generate new access token

3. **Create User repository**
   - File: `backend/src/adapters/repositories/user_repository.py`
   - Methods: get_by_email, get_by_id, create, update, delete
   - DynamoDB operations for User entity

4. **Create JWT token service**
   - File: `backend/src/adapters/services/jwt_service.py`
   - Methods: generate_access_token, generate_refresh_token, verify_token
   - Use PyJWT library

5. **Create password hashing service**
   - File: `backend/src/adapters/services/password_service.py`
   - Methods: hash_password, verify_password
   - Use bcrypt or argon2

6. **Create API Gateway handlers**
   - File: `backend/src/entrypoints/apigw/auth/`
   - `login_handler.py`
   - `logout_handler.py`
   - `profile_handler.py`
   - `refresh_handler.py`

7. **Add authentication middleware**
   - File: `backend/src/entrypoints/apigw/middleware/auth_middleware.py`
   - Verify JWT tokens on protected routes

8. **Update serverless.yml**
   - Add auth function configurations
   - Add API Gateway routes
   - Configure authorizer for protected routes

9. **Update DynamoDB schema**
   - Add User table/GSI configuration
   - Update `backend/infra/resources/dynamodb.yml`

10. **Add tests**
    - Unit tests for use cases
    - Integration tests for handlers
    - Test JWT token generation/validation

---

## 2. Events API (2 additional endpoints)

**Priority: HIGH** - Core feature

### Endpoints:

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/events` | List events with filters | ✅ Implemented (not deployed) |
| GET | `/api/events/{id}` | Get event details | ✅ Implemented (not deployed) |
| DELETE | `/api/events/{id}` | Delete event | ❌ Missing |
| POST | `/api/events/{id}/create-task` | Create task from event | ❌ Missing |

### Implementation Steps:

1. **Enable existing endpoints**
   - Uncomment lines 78-86 in `backend/infra/functions/serverless.yml`
   - Deploy to activate GET /events and GET /events/{id}

2. **Create delete event use case**
   - File: `backend/src/domain/use_cases/events/delete_event.py`
   - Soft delete or hard delete logic

3. **Create task from event use case**
   - File: `backend/src/domain/use_cases/events/create_task_from_event.py`
   - Extract event details into task description
   - Link task to event

4. **Create API handlers**
   - File: `backend/src/entrypoints/apigw/events/delete_event_handler.py`
   - File: `backend/src/entrypoints/apigw/events/create_task_handler.py`

5. **Update serverless.yml**
   - Add DELETE /events/{id} route
   - Add POST /events/{id}/create-task route

6. **Add tests**

---

## 3. Tasks API (7 endpoints)

**Priority: HIGH** - Core feature

### Endpoints:

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/tasks` | List tasks with filters | ❌ Missing |
| GET | `/api/tasks/{id}` | Get task details | ❌ Missing |
| POST | `/api/tasks` | Create new task | ❌ Missing |
| PUT | `/api/tasks/{id}` | Update task | ❌ Missing |
| DELETE | `/api/tasks/{id}` | Delete task | ❌ Missing |
| POST | `/api/tasks/{id}/comments` | Add comment to task | ❌ Missing |
| PUT | `/api/tasks/{id}/status` | Update task status | ❌ Missing |

### Implementation Steps:

1. **Create Task domain model**
   - File: `backend/src/domain/entities/task.py`
   - Fields: id, title, description, status, priority, assigned_user_id, event_id, due_date, created_at, updated_at, created_by
   - Status: open, in_progress, closed
   - Priority: critical, high, medium, low

2. **Create TaskComment domain model**
   - File: `backend/src/domain/entities/task_comment.py`
   - Fields: id, task_id, user_id, comment, created_at

3. **Create task use cases**
   - File: `backend/src/domain/use_cases/tasks/`
   - `list_tasks.py` - List with filters (status, priority, assigned_user, dates)
   - `get_task.py` - Get task by ID with comments
   - `create_task.py` - Create new task
   - `update_task.py` - Update task fields
   - `delete_task.py` - Delete task
   - `add_comment.py` - Add comment to task
   - `update_status.py` - Update task status

4. **Create Task repository**
   - File: `backend/src/adapters/repositories/task_repository.py`
   - Methods: get, list, create, update, delete, add_comment
   - DynamoDB operations for Task entity

5. **Create API Gateway handlers**
   - File: `backend/src/entrypoints/apigw/tasks/`
   - `list_tasks_handler.py`
   - `get_task_handler.py`
   - `create_task_handler.py`
   - `update_task_handler.py`
   - `delete_task_handler.py`
   - `add_comment_handler.py`
   - `update_status_handler.py`

6. **Update serverless.yml**
   - Add all task route configurations

7. **Update DynamoDB schema**
   - Add Task and TaskComment table/GSI configurations

8. **Add tests**

---

## 4. Users API (5 endpoints)

**Priority: HIGH** - Admin feature

### Endpoints:

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/users` | List users with filters | ❌ Missing |
| GET | `/api/users/{id}` | Get user details | ❌ Missing |
| POST | `/api/users` | Create new user (admin only) | ❌ Missing |
| PUT | `/api/users/{id}` | Update user | ❌ Missing |
| DELETE | `/api/users/{id}` | Delete user | ❌ Missing |

### Implementation Steps:

1. **Create user management use cases**
   - File: `backend/src/domain/use_cases/users/`
   - `list_users.py` - List with filters (role, active status, search)
   - `get_user.py` - Get user by ID
   - `create_user.py` - Admin creates user (with password generation)
   - `update_user.py` - Update user fields
   - `delete_user.py` - Delete/deactivate user

2. **Create API Gateway handlers**
   - File: `backend/src/entrypoints/apigw/users/`
   - `list_users_handler.py`
   - `get_user_handler.py`
   - `create_user_handler.py`
   - `update_user_handler.py`
   - `delete_user_handler.py`

3. **Add RBAC checks**
   - Only admin can create/delete users
   - Only admin/manager can list all users
   - Users can update their own profile

4. **Update serverless.yml**
   - Add all user route configurations
   - Add admin authorization

5. **Add tests**
   - Test RBAC enforcement

---

## 5. Dashboard API (4 endpoints)

**Priority: MEDIUM** - UI enhancement

### Endpoints:

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/dashboard/overview` | Get all dashboard stats | ❌ Missing |
| GET | `/api/dashboard/events-stats` | Get event statistics | ❌ Missing |
| GET | `/api/dashboard/tasks-stats` | Get task statistics | ❌ Missing |
| GET | `/api/dashboard/users-stats` | Get user statistics | ❌ Missing |

### Implementation Steps:

1. **Create dashboard use cases**
   - File: `backend/src/domain/use_cases/dashboard/`
   - `get_overview.py` - Aggregate all stats
   - `get_event_stats.py` - Total events, by severity, by source, recent events
   - `get_task_stats.py` - Total tasks, by status, by priority, my tasks
   - `get_user_stats.py` - Total users, active users, by role

2. **Create aggregation queries**
   - Use DynamoDB GSI for efficient aggregation
   - Cache results if performance is an issue

3. **Create API Gateway handlers**
   - File: `backend/src/entrypoints/apigw/dashboard/`
   - `overview_handler.py`
   - `event_stats_handler.py`
   - `task_stats_handler.py`
   - `user_stats_handler.py`

4. **Update serverless.yml**
   - Add dashboard route configurations

5. **Add tests**

---

## 6. Configuration API (8 endpoints)

**Priority: MEDIUM** - Admin feature

### Endpoints:

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/config/aws-accounts` | List AWS accounts | ❌ Missing (agents API exists) |
| GET | `/api/config/aws-accounts/{id}` | Get AWS account | ❌ Missing |
| POST | `/api/config/aws-accounts` | Add AWS account | ❌ Missing |
| PUT | `/api/config/aws-accounts/{id}` | Update AWS account | ❌ Missing |
| DELETE | `/api/config/aws-accounts/{id}` | Delete AWS account | ❌ Missing |
| POST | `/api/config/aws-accounts/{id}/test` | Test connection | ❌ Missing |
| GET | `/api/config/monitoring` | Get monitoring config | ❌ Missing |
| PUT | `/api/config/monitoring` | Update monitoring config | ❌ Missing |

### Implementation Steps:

1. **Refactor existing Agents to AwsAccounts**
   - The existing agents API is similar but needs renaming
   - Rename domain/entities/agent.py to aws_account.py
   - Update all references

2. **Create AWS account use cases**
   - File: `backend/src/domain/use_cases/aws_accounts/`
   - `list_accounts.py`
   - `get_account.py`
   - `create_account.py`
   - `update_account.py`
   - `delete_account.py`
   - `test_connection.py` - Verify AWS credentials

3. **Create MonitoringConfig domain model**
   - File: `backend/src/domain/entities/monitoring_config.py`
   - Fields: services, global_settings, thresholds, resource_filters

4. **Create monitoring config use cases**
   - File: `backend/src/domain/use_cases/config/`
   - `get_monitoring_config.py`
   - `update_monitoring_config.py`

5. **Create API Gateway handlers**
   - File: `backend/src/entrypoints/apigw/config/`
   - AWS accounts handlers
   - Monitoring config handlers

6. **Add AWS credentials validation**
   - Use boto3 to test STS assume role or list resources

7. **Update serverless.yml**
   - Add config route configurations

8. **Add tests**

---

## Implementation Priority

### Phase 1 - Critical (Must-have for MVP)
1. **Authentication API** (4 endpoints) - Week 1-2
   - Without this, users can't log in
   - Blocking all other features

2. **Events API** (2 new endpoints) - Week 2
   - Enable existing GET endpoints
   - Add DELETE and create-task

3. **Tasks API** (7 endpoints) - Week 3-4
   - Core feature for task management

### Phase 2 - Important (Enhanced functionality)
4. **Users API** (5 endpoints) - Week 5
   - Admin user management

5. **Dashboard API** (4 endpoints) - Week 6
   - Stats and overview

### Phase 3 - Nice-to-have (Additional features)
6. **Configuration API** (8 endpoints) - Week 7-8
   - AWS account management
   - Monitoring configuration

---

## Estimated Effort

| API Group | Endpoints | Complexity | Estimated Hours | Priority |
|-----------|-----------|------------|-----------------|----------|
| Authentication | 4 | High | 40-60h | Critical |
| Events | 2 | Low | 8-12h | High |
| Tasks | 7 | Medium | 35-45h | High |
| Users | 5 | Medium | 25-35h | High |
| Dashboard | 4 | Low | 16-24h | Medium |
| Configuration | 8 | Medium | 32-48h | Medium |
| **TOTAL** | **30** | - | **156-224h** | - |

**Note:** These estimates include:
- Domain model design
- Use case implementation
- Repository/adapter code
- API Gateway handlers
- Tests
- Documentation

---

## Technical Dependencies

### Required Libraries (Add to backend/pyproject.toml):
```toml
[tool.poetry.dependencies]
pyjwt = "^2.8.0"           # JWT token generation
bcrypt = "^4.1.2"          # Password hashing
python-jose = "^3.3.0"     # Alternative JWT library
passlib = "^1.7.4"         # Password utilities
```

### DynamoDB Schema Updates:

**New Tables/GSIs needed:**
1. User table
   - PK: USER#{user_id}
   - GSI: email-index (for login)
   - GSI: role-index (for filtering)

2. Task table
   - PK: TASK#{task_id}
   - GSI: assigned-user-index
   - GSI: status-index
   - GSI: event-id-index

3. TaskComment table
   - PK: COMMENT#{comment_id}
   - SK: TASK#{task_id}

4. MonitoringConfig table
   - PK: CONFIG#{config_type}

---

## Testing Strategy

For each endpoint, create:

1. **Unit Tests**
   - Test use cases in isolation
   - Mock repositories and external services
   - File: `backend/tests/unit/use_cases/`

2. **Integration Tests**
   - Test API Gateway handlers
   - Test with LocalStack DynamoDB
   - File: `backend/tests/integration/apigw/`

3. **E2E Tests**
   - Test full request/response flow
   - Test authentication flow
   - File: `backend/tests/e2e/`

---

## Next Steps

1. **Review and approve** this implementation plan
2. **Set up development environment** with required dependencies
3. **Start with Phase 1** (Authentication API)
4. **Create feature branches** for each API group
5. **Implement incrementally** following hexagonal architecture
6. **Deploy to dev environment** after each phase
7. **Update frontend** to connect to real backend

---

## Notes

- The existing backend has good hexagonal architecture foundation
- Event and Agent entities/repositories can be used as templates
- DynamoDB single-table design is already in place
- Lambda Powertools is configured and working
- Focus on consistency with existing code patterns

---

## Questions to Resolve

1. **Authentication method**: JWT tokens or AWS Cognito?
   - Recommendation: Start with JWT for simplicity

2. **Password reset flow**: Email-based or admin reset only?
   - Recommendation: Admin reset for MVP

3. **Task notifications**: Should task updates send notifications?
   - Recommendation: Yes, via existing Slack integration

4. **Soft delete vs hard delete**: For tasks, events, users?
   - Recommendation: Soft delete (add deleted_at field)

5. **Rate limiting**: Should we add API rate limiting?
   - Recommendation: Yes, use API Gateway throttling

6. **Audit logging**: Track all API changes?
   - Recommendation: Yes, add to DynamoDB with separate table

---

**Last Updated:** 2025-11-20
**Created By:** Claude Code
**Status:** Draft - Awaiting Approval

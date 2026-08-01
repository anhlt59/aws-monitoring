# Backend API Implementation Tasks

> **Status:** Planning Phase
> **Last Updated:** 2025-11-23
> **Based on:** [API_ENDPOINTS_SUMMARY.txt](./API_ENDPOINTS_SUMMARY.txt)

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Authentication API (Critical)](#phase-1-authentication-api-critical)
4. [Phase 2: Events API Extensions (High Priority)](#phase-2-events-api-extensions-high-priority)
5. [Phase 3: Tasks API (High Priority)](#phase-3-tasks-api-high-priority)
6. [Phase 4: Users API (High Priority)](#phase-4-users-api-high-priority)
7. [Phase 5: Dashboard API (Medium Priority)](#phase-5-dashboard-api-medium-priority)
8. [Phase 6: Configuration API (Medium Priority)](#phase-6-configuration-api-medium-priority)
9. [Testing Strategy](#testing-strategy)
10. [Deployment Checklist](#deployment-checklist)

---

## Overview

### Summary Statistics

| Phase | Priority | Endpoints | Estimated Hours | Timeline |
|-------|----------|-----------|-----------------|----------|
| Phase 1: Authentication | Critical | 4 | 40-60 | Week 1-2 |
| Phase 2: Events Extensions | High | 1 | 8-12 | Week 2 |
| Phase 3: Tasks | High | 7 | 35-45 | Week 3-4 |
| Phase 4: Users | High | 5 | 25-35 | Week 5 |
| Phase 5: Dashboard | Medium | 4 | 16-24 | Week 6 |
| Phase 6: Configuration | Medium | 4 | 20-30 | Week 7-8 |
| **TOTAL** | | **25** | **144-206** | **7-9 weeks** |

### Project Structure Reference

```
backend/src/
├── domain/                          # Core business logic
│   ├── models/                     # Domain entities
│   │   ├── user.py                 # ✅ User entity (exists)
│   │   ├── task.py                 # ✅ Task entity (exists)
│   │   ├── event.py                # ✅ Event entity (exists)
│   │   └── config.py               # ✅ Config entities (exists)
│   ├── use_cases/                  # Business use cases
│   │   └── *.py                    # ⬜ To be created
│   └── ports/                      # Interface definitions
│       └── repositories.py         # ✅ Port interfaces (exists)
├── adapters/                        # External integrations
│   ├── db/                         # Database layer
│   │   ├── models/                 # DynamoDB models (PynamoDB)
│   │   │   ├── user.py            # ✅ UserModel (exists)
│   │   │   ├── task.py            # ✅ TaskModel (exists)
│   │   │   └── event.py           # ✅ EventModel (exists)
│   │   ├── mappers/                # Domain ↔ DB mappers
│   │   │   ├── user.py            # ✅ UserMapper (exists)
│   │   │   ├── task.py            # ✅ TaskMapper (exists)
│   │   │   └── event.py           # ✅ EventMapper (exists)
│   │   └── repositories/           # Repository implementations
│   │       ├── user.py            # ✅ UserRepository (exists)
│   │       ├── task.py            # ✅ TaskRepository (exists)
│   │       └── event.py           # ✅ EventRepository (exists)
│   └── auth/                       # ⬜ Authentication services
│       ├── jwt.py                  # ⬜ JWT token management
│       └── password.py             # ⬜ Password hashing
└── entrypoints/                     # API Gateway handlers
    └── apigw/                      # API Gateway entry points
        ├── base.py                 # ✅ Base app creator (exists)
        ├── auth/                   # ⬜ Auth endpoints
        │   └── main.py
        ├── tasks/                  # ⬜ Task endpoints
        │   └── main.py
        ├── users/                  # ⬜ User endpoints
        │   └── main.py
        ├── dashboard/              # ⬜ Dashboard endpoints
        │   └── main.py
        └── config/                 # ⬜ Config endpoints
            └── main.py
```

---

## Prerequisites

### 1. Add Dependencies to `pyproject.toml`

```bash
cd backend
poetry add pyjwt==2.8.0
poetry add bcrypt==4.1.2
poetry add passlib[bcrypt]==1.7.4
poetry add python-multipart  # For form data handling
```

### 2. Environment Variables

Add to `backend/.env.local`:

```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Password Hashing
BCRYPT_ROUNDS=12

# CORS
CORS_ALLOW_ORIGIN=http://localhost:3000
```

### 3. Update DynamoDB Tables

Tables already exist based on the domain models. Verify GSI configurations:

- **User Table GSIs:**
  - GSI1: Email lookup (`pk=EMAIL`, `sk=EMAIL#{email}`)
  - GSI2: Role lookup (`pk=ROLE#{role}`, `sk=USER#{user_id}`)

- **Task Table GSIs:**
  - GSI1: Assigned user lookup (`pk=ASSIGNED#{user_id}`, `sk=STATUS#{status}#PRIORITY#{priority}#TASK#{id}`)
  - GSI2: Status lookup (`pk=STATUS#{status}`, `sk=CREATED#{created_at}#TASK#{id}`)

---

## Phase 1: Authentication API (Critical)

**Priority:** CRITICAL
**Endpoints:** 4
**Estimated:** 40-60 hours
**Timeline:** Week 1-2

### Endpoints to Implement

- [ ] `POST /api/auth/login` - Login with email/password
- [ ] `POST /api/auth/logout` - Logout current user
- [ ] `GET /api/auth/me` - Get current user profile
- [ ] `POST /api/auth/refresh` - Refresh access token

### Implementation Tasks

#### 1.1 Authentication Infrastructure

- [ ] **Create JWT token service** (`backend/src/adapters/auth/jwt.py`)
  - [ ] Implement `generate_access_token(user_id, email, role)` -> JWT string
  - [ ] Implement `generate_refresh_token(user_id)` -> JWT string
  - [ ] Implement `decode_token(token)` -> dict with claims
  - [ ] Implement `verify_token(token)` -> bool
  - [ ] Handle token expiration and validation errors
  - [ ] Add token blacklisting for logout (use DynamoDB or in-memory cache)

- [ ] **Create password service** (`backend/src/adapters/auth/password.py`)
  - [ ] Implement `hash_password(plain_password)` -> hashed password (bcrypt)
  - [ ] Implement `verify_password(plain_password, hashed_password)` -> bool
  - [ ] Use bcrypt with cost factor 12

- [ ] **Create authentication middleware** (`backend/src/entrypoints/apigw/middleware/auth.py`)
  - [ ] Extract JWT from `Authorization: Bearer <token>` header
  - [ ] Validate token and extract user claims
  - [ ] Attach user context to request
  - [ ] Handle authentication errors (401)
  - [ ] Create decorator `@require_auth` for protected endpoints
  - [ ] Create decorator `@require_role(role)` for role-based access

#### 1.2 Use Cases

- [ ] **Create use case:** `AuthenticateUser` (`backend/src/domain/use_cases/authenticate_user.py`)
  - [ ] Input: `AuthenticateUserDTO(email, password)`
  - [ ] Find user by email (case-insensitive)
  - [ ] Verify password hash
  - [ ] Return user entity or raise `AuthenticationError`
  - [ ] Update `last_login` timestamp
  - [ ] Handle non-existent user, invalid password

- [ ] **Create use case:** `GenerateAuthTokens` (`backend/src/domain/use_cases/generate_auth_tokens.py`)
  - [ ] Input: `User` entity
  - [ ] Generate access token (1 hour expiry)
  - [ ] Generate refresh token (30 days expiry)
  - [ ] Return `AuthTokensDTO(access_token, refresh_token, expires_in)`

- [ ] **Create use case:** `RefreshAuthToken` (`backend/src/domain/use_cases/refresh_auth_token.py`)
  - [ ] Input: `refresh_token`
  - [ ] Validate refresh token
  - [ ] Extract user_id from token
  - [ ] Verify user still exists and is active
  - [ ] Generate new access token
  - [ ] Return new access token

- [ ] **Create use case:** `LogoutUser` (`backend/src/domain/use_cases/logout_user.py`)
  - [ ] Input: `access_token`
  - [ ] Add token to blacklist (DynamoDB with TTL)
  - [ ] Return success

- [ ] **Create use case:** `GetCurrentUser` (`backend/src/domain/use_cases/get_current_user.py`)
  - [ ] Input: `user_id` (from JWT claims)
  - [ ] Fetch user from repository
  - [ ] Return user profile (exclude password_hash)

#### 1.3 API Endpoints

- [ ] **Create handler:** `POST /api/auth/login` (`backend/src/entrypoints/apigw/auth/main.py`)
  - [ ] Accept `LoginRequest(email, password, remember_me?)`
  - [ ] Call `AuthenticateUser` use case
  - [ ] Call `GenerateAuthTokens` use case
  - [ ] Return `LoginResponse(access_token, refresh_token, token_type, expires_in, user)`
  - [ ] HTTP 200 on success
  - [ ] HTTP 401 on invalid credentials
  - [ ] HTTP 429 for rate limiting

- [ ] **Create handler:** `POST /api/auth/refresh`
  - [ ] Accept `RefreshRequest(refresh_token)`
  - [ ] Call `RefreshAuthToken` use case
  - [ ] Return `RefreshResponse(access_token, token_type, expires_in)`
  - [ ] HTTP 200 on success
  - [ ] HTTP 401 on invalid/expired token

- [ ] **Create handler:** `POST /api/auth/logout`
  - [ ] Require authentication (`@require_auth`)
  - [ ] Extract access token from header
  - [ ] Call `LogoutUser` use case
  - [ ] Return HTTP 204 (No Content)
  - [ ] HTTP 401 if not authenticated

- [ ] **Create handler:** `GET /api/auth/me`
  - [ ] Require authentication (`@require_auth`)
  - [ ] Extract user_id from JWT claims
  - [ ] Call `GetCurrentUser` use case
  - [ ] Return `UserDTO` (without password_hash)
  - [ ] HTTP 200 on success
  - [ ] HTTP 401 if not authenticated

#### 1.4 Infrastructure Configuration

- [ ] **Create serverless config** (`backend/infra/functions/auth.yml`)
  ```yaml
  functions:
    auth:
      handler: src.entrypoints.apigw.auth.main.handler
      events:
        - httpApi:
            path: /auth/{proxy+}
            method: ANY
      environment:
        JWT_SECRET_KEY: ${env:JWT_SECRET_KEY}
        JWT_ALGORITHM: ${env:JWT_ALGORITHM}
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES: ${env:JWT_ACCESS_TOKEN_EXPIRE_MINUTES}
  ```

- [ ] **Include auth config** in `backend/infra/serverless.yml`:
  ```yaml
  functions: ${file(./functions/auth.yml):functions}
  ```

#### 1.5 Testing

- [ ] **Unit tests** (`backend/tests/unit/adapters/auth/`)
  - [ ] Test JWT token generation and validation
  - [ ] Test password hashing and verification
  - [ ] Test token expiration handling

- [ ] **Unit tests** (`backend/tests/unit/use_cases/`)
  - [ ] Test `AuthenticateUser` with valid/invalid credentials
  - [ ] Test `GenerateAuthTokens`
  - [ ] Test `RefreshAuthToken` with valid/expired tokens
  - [ ] Test `LogoutUser`
  - [ ] Test `GetCurrentUser`

- [ ] **Integration tests** (`backend/tests/integration/apigw/auth/`)
  - [ ] Test `POST /auth/login` with valid credentials
  - [ ] Test `POST /auth/login` with invalid credentials
  - [ ] Test `POST /auth/refresh` with valid token
  - [ ] Test `POST /auth/refresh` with expired token
  - [ ] Test `GET /auth/me` with valid token
  - [ ] Test `GET /auth/me` without token (401)
  - [ ] Test `POST /auth/logout`

#### 1.6 Documentation

- [ ] Update API specification in `docs/api-specification.yaml`
- [ ] Document JWT token format and claims
- [ ] Document error codes and responses
- [ ] Add authentication examples to README

---

## Phase 2: Events API Extensions (High Priority)

**Priority:** HIGH
**Endpoints:** 1 (+ 2 already implemented)
**Estimated:** 8-12 hours
**Timeline:** Week 2

### Endpoints to Implement

- [x] `GET /api/events` - List events (✅ already implemented)
- [x] `GET /api/events/{id}` - Get event details (✅ already implemented)
- [ ] `POST /api/events/{id}/create-task` - Create task from event

### Implementation Tasks

#### 2.1 Use Cases

- [ ] **Create use case:** `CreateTaskFromEvent` (`backend/src/domain/use_cases/create_task_from_event.py`)
  - [ ] Input: `CreateTaskFromEventDTO(event_id, title?, description?, assigned_user_id, priority?)`
  - [ ] Fetch event from EventRepository
  - [ ] Map event severity to task priority (if not provided)
  - [ ] Pre-fill task description with event details
  - [ ] Link task to event (store event_id and event_details)
  - [ ] Create task with TaskRepository
  - [ ] Return created Task entity

#### 2.2 API Endpoints

- [ ] **Create handler:** `POST /api/events/{id}/create-task` (`backend/src/entrypoints/apigw/events/main.py`)
  - [ ] Require authentication (`@require_auth`)
  - [ ] Accept `CreateTaskFromEventRequest(title?, description?, assigned_user_id, priority?)`
  - [ ] Call `CreateTaskFromEvent` use case
  - [ ] Return `TaskDTO` with HTTP 201
  - [ ] HTTP 404 if event not found
  - [ ] HTTP 400 for validation errors

#### 2.3 Infrastructure

- [ ] **Uncomment existing event routes** in `backend/infra/functions/serverless.yml` (lines 78-86)
  - Events API handlers already exist but are commented out
  - Enable them for deployment

#### 2.4 Testing

- [ ] **Unit tests** (`backend/tests/unit/use_cases/`)
  - [ ] Test `CreateTaskFromEvent` with valid event
  - [ ] Test `CreateTaskFromEvent` with non-existent event
  - [ ] Test priority mapping from event severity

- [ ] **Integration tests** (`backend/tests/integration/apigw/events/`)
  - [ ] Test `POST /events/{id}/create-task` with valid data
  - [ ] Test `POST /events/{id}/create-task` with non-existent event (404)
  - [ ] Test authentication requirement

---

## Phase 3: Tasks API (High Priority)

**Priority:** HIGH
**Endpoints:** 7
**Estimated:** 35-45 hours
**Timeline:** Week 3-4

### Endpoints to Implement

- [ ] `GET /api/tasks` - List tasks with filters
- [ ] `GET /api/tasks/{id}` - Get task details (includes embedded comments)
- [ ] `POST /api/tasks` - Create new task
- [ ] `PUT /api/tasks/{id}` - Update task
- [ ] `DELETE /api/tasks/{id}` - Delete task
- [ ] `POST /api/tasks/{id}/comments` - Add comment to task
- [ ] `PUT /api/tasks/{id}/status` - Update task status

### Implementation Tasks

#### 3.1 Use Cases

- [ ] **Create use case:** `CreateTask` (`backend/src/domain/use_cases/create_task.py`)
  - [ ] Input: `CreateTaskDTO(title, description, priority, assigned_user_id, due_date?, event_id?)`
  - [ ] Validate title (3-200 chars)
  - [ ] Validate description (10-5000 chars)
  - [ ] Validate assigned user exists (UserRepository)
  - [ ] Create AssignedUser object with {id, name}
  - [ ] Set status to `open`
  - [ ] Initialize empty comments array
  - [ ] Generate UUIDv7 for task_id
  - [ ] Set created_by from authenticated user
  - [ ] Save to TaskRepository
  - [ ] Return created Task entity

- [ ] **Create use case:** `GetTask` (`backend/src/domain/use_cases/get_task.py`)
  - [ ] Input: `task_id`
  - [ ] Fetch task from TaskRepository
  - [ ] Return Task entity with all embedded comments
  - [ ] Raise `NotFoundError` if task doesn't exist

- [ ] **Create use case:** `ListTasks` (`backend/src/domain/use_cases/list_tasks.py`)
  - [ ] Input: `ListTasksDTO(status?, priority?, assigned_user_id?, start_date?, end_date?, page, page_size, sort?)`
  - [ ] Build query based on filters
  - [ ] Use GSI1 for assigned_user queries
  - [ ] Use GSI2 for status queries
  - [ ] Support pagination
  - [ ] Return `PaginatedTasksDTO(items, total, page, page_size, has_more)`

- [ ] **Create use case:** `UpdateTask` (`backend/src/domain/use_cases/update_task.py`)
  - [ ] Input: `UpdateTaskDTO(task_id, title?, description?, priority?, assigned_user_id?, due_date?)`
  - [ ] Fetch existing task
  - [ ] Validate user permissions (owner or admin)
  - [ ] Update allowed fields
  - [ ] If assigned_user_id changed, update AssignedUser object
  - [ ] Update `updated_at` timestamp
  - [ ] Save to TaskRepository
  - [ ] Return updated Task entity

- [ ] **Create use case:** `UpdateTaskStatus` (`backend/src/domain/use_cases/update_task_status.py`)
  - [ ] Input: `UpdateTaskStatusDTO(task_id, new_status)`
  - [ ] Fetch existing task
  - [ ] Validate status transition
  - [ ] If status changes to `closed`, set `closed_at` timestamp
  - [ ] If reopening task, clear `closed_at`
  - [ ] Update `updated_at` timestamp
  - [ ] Save to TaskRepository
  - [ ] Return updated Task entity

- [ ] **Create use case:** `DeleteTask` (`backend/src/domain/use_cases/delete_task.py`)
  - [ ] Input: `task_id`
  - [ ] Fetch existing task
  - [ ] Validate user permissions (admin only)
  - [ ] Delete from TaskRepository
  - [ ] Return success

- [ ] **Create use case:** `AddCommentToTask` (`backend/src/domain/use_cases/add_comment_to_task.py`)
  - [ ] Input: `AddCommentDTO(task_id, comment_text, user_id, user_name)`
  - [ ] Fetch existing task
  - [ ] Validate comment_text (1-2000 chars)
  - [ ] Create TaskComment object with generated UUID
  - [ ] Append comment to task.comments array
  - [ ] Update task.updated_at timestamp
  - [ ] Save to TaskRepository
  - [ ] Return updated Task entity

#### 3.2 API Endpoints

- [ ] **Create handler:** `GET /api/tasks` (`backend/src/entrypoints/apigw/tasks/main.py`)
  - [ ] Require authentication (`@require_auth`)
  - [ ] Accept query params: `status`, `priority`, `assigned_user_id`, `start_date`, `end_date`, `page`, `page_size`, `sort`
  - [ ] Call `ListTasks` use case
  - [ ] Return `PaginatedTasksResponse`
  - [ ] HTTP 200 on success

- [ ] **Create handler:** `GET /api/tasks/{id}`
  - [ ] Require authentication (`@require_auth`)
  - [ ] Call `GetTask` use case
  - [ ] Return `TaskDTO` with all comments
  - [ ] HTTP 200 on success
  - [ ] HTTP 404 if not found

- [ ] **Create handler:** `POST /api/tasks`
  - [ ] Require authentication (`@require_auth`)
  - [ ] Accept `CreateTaskRequest(title, description, priority, assigned_user_id, due_date?, event_id?)`
  - [ ] Validate request body
  - [ ] Call `CreateTask` use case
  - [ ] Return `TaskDTO` with HTTP 201
  - [ ] HTTP 400 for validation errors

- [ ] **Create handler:** `PUT /api/tasks/{id}`
  - [ ] Require authentication (`@require_auth`)
  - [ ] Accept `UpdateTaskRequest(title?, description?, priority?, assigned_user_id?, due_date?)`
  - [ ] Call `UpdateTask` use case
  - [ ] Return `TaskDTO` with HTTP 200
  - [ ] HTTP 404 if not found
  - [ ] HTTP 403 if permission denied

- [ ] **Create handler:** `PUT /api/tasks/{id}/status`
  - [ ] Require authentication (`@require_auth`)
  - [ ] Accept `UpdateTaskStatusRequest(status)`
  - [ ] Call `UpdateTaskStatus` use case
  - [ ] Return `TaskDTO` with HTTP 200
  - [ ] HTTP 400 for invalid status
  - [ ] HTTP 404 if not found

- [ ] **Create handler:** `DELETE /api/tasks/{id}`
  - [ ] Require authentication and admin role (`@require_role('admin')`)
  - [ ] Call `DeleteTask` use case
  - [ ] Return HTTP 204 (No Content)
  - [ ] HTTP 404 if not found
  - [ ] HTTP 403 if not admin

- [ ] **Create handler:** `POST /api/tasks/{id}/comments`
  - [ ] Require authentication (`@require_auth`)
  - [ ] Accept `AddCommentRequest(comment)`
  - [ ] Extract user_id and user_name from JWT
  - [ ] Call `AddCommentToTask` use case
  - [ ] Return updated `TaskDTO` with HTTP 201
  - [ ] HTTP 404 if task not found
  - [ ] HTTP 400 for validation errors

#### 3.3 Infrastructure Configuration

- [ ] **Create serverless config** (`backend/infra/functions/tasks.yml`)
  ```yaml
  functions:
    tasks:
      handler: src.entrypoints.apigw.tasks.main.handler
      events:
        - httpApi:
            path: /tasks/{proxy+}
            method: ANY
  ```

- [ ] Include tasks config in `backend/infra/serverless.yml`

#### 3.4 Testing

- [ ] **Unit tests** (`backend/tests/unit/use_cases/`)
  - [ ] Test all task use cases with valid/invalid inputs
  - [ ] Test permission checks
  - [ ] Test status transitions
  - [ ] Test comment validation

- [ ] **Integration tests** (`backend/tests/integration/apigw/tasks/`)
  - [ ] Test all task endpoints
  - [ ] Test authentication and authorization
  - [ ] Test filtering and pagination
  - [ ] Test comment operations

---

## Phase 4: Users API (High Priority)

**Priority:** HIGH
**Endpoints:** 5
**Estimated:** 25-35 hours
**Timeline:** Week 5

### Endpoints to Implement

- [ ] `GET /api/users` - List users (admin only)
- [ ] `GET /api/users/{id}` - Get user details
- [ ] `POST /api/users` - Create user (admin only)
- [ ] `PUT /api/users/{id}` - Update user
- [ ] `DELETE /api/users/{id}` - Delete user (admin only)

### Implementation Tasks

#### 4.1 Use Cases

- [ ] **Create use case:** `CreateUser` (`backend/src/domain/use_cases/create_user.py`)
  - [ ] Input: `CreateUserDTO(email, full_name, password?, role)`
  - [ ] Validate email uniqueness (UserRepository)
  - [ ] Validate email format
  - [ ] Normalize email (lowercase, strip)
  - [ ] Validate full_name (2-100 chars)
  - [ ] Hash password (or generate random if not provided)
  - [ ] Generate UUIDv7 for user_id
  - [ ] Set created_at and updated_at timestamps
  - [ ] Save to UserRepository
  - [ ] Return created User entity (without password_hash)

- [ ] **Create use case:** `GetUser` (`backend/src/domain/use_cases/get_user.py`)
  - [ ] Input: `user_id`
  - [ ] Fetch user from UserRepository
  - [ ] Return User entity (without password_hash)
  - [ ] Raise `NotFoundError` if not exists

- [ ] **Create use case:** `ListUsers` (`backend/src/domain/use_cases/list_users.py`)
  - [ ] Input: `ListUsersDTO(role?, search?, page, page_size, sort?)`
  - [ ] Use GSI2 for role filtering
  - [ ] Use GSI1 for email search
  - [ ] Support pagination
  - [ ] Return `PaginatedUsersDTO(items, total, page, page_size, has_more)`

- [ ] **Create use case:** `UpdateUser` (`backend/src/domain/use_cases/update_user.py`)
  - [ ] Input: `UpdateUserDTO(user_id, email?, full_name?, role?)`
  - [ ] Fetch existing user
  - [ ] Validate permissions (self or admin)
  - [ ] If email changed, validate uniqueness
  - [ ] Update allowed fields
  - [ ] Update `updated_at` timestamp
  - [ ] Save to UserRepository
  - [ ] Return updated User entity

- [ ] **Create use case:** `ChangePassword` (`backend/src/domain/use_cases/change_password.py`)
  - [ ] Input: `ChangePasswordDTO(user_id, current_password, new_password)`
  - [ ] Fetch user
  - [ ] Verify current password
  - [ ] Validate new password strength
  - [ ] Hash new password
  - [ ] Update user.password_hash
  - [ ] Update updated_at timestamp
  - [ ] Save to UserRepository

- [ ] **Create use case:** `DeleteUser` (`backend/src/domain/use_cases/delete_user.py`)
  - [ ] Input: `user_id`
  - [ ] Validate admin permissions
  - [ ] Fetch user
  - [ ] Delete from UserRepository
  - [ ] Return success

#### 4.2 API Endpoints

- [ ] **Create handler:** `GET /api/users` (`backend/src/entrypoints/apigw/users/main.py`)
  - [ ] Require admin role (`@require_role('admin')`)
  - [ ] Accept query params: `role`, `search`, `page`, `page_size`, `sort`
  - [ ] Call `ListUsers` use case
  - [ ] Return `PaginatedUsersResponse`
  - [ ] HTTP 200 on success
  - [ ] HTTP 403 if not admin

- [ ] **Create handler:** `GET /api/users/{id}`
  - [ ] Require authentication (`@require_auth`)
  - [ ] Validate permissions (self or admin)
  - [ ] Call `GetUser` use case
  - [ ] Return `UserDTO`
  - [ ] HTTP 200 on success
  - [ ] HTTP 404 if not found
  - [ ] HTTP 403 if permission denied

- [ ] **Create handler:** `POST /api/users`
  - [ ] Require admin role (`@require_role('admin')`)
  - [ ] Accept `CreateUserRequest(email, full_name, password?, role)`
  - [ ] Call `CreateUser` use case
  - [ ] Return `UserDTO` with HTTP 201
  - [ ] HTTP 400 for validation errors (duplicate email, etc.)
  - [ ] HTTP 403 if not admin

- [ ] **Create handler:** `PUT /api/users/{id}`
  - [ ] Require authentication (`@require_auth`)
  - [ ] Validate permissions (self or admin)
  - [ ] Accept `UpdateUserRequest(email?, full_name?, role?)`
  - [ ] Call `UpdateUser` use case
  - [ ] Return `UserDTO` with HTTP 200
  - [ ] HTTP 404 if not found
  - [ ] HTTP 403 if permission denied
  - [ ] HTTP 400 for validation errors

- [ ] **Create handler:** `PUT /api/users/{id}/change-password`
  - [ ] Require authentication (`@require_auth`)
  - [ ] Validate user is updating their own password
  - [ ] Accept `ChangePasswordRequest(current_password, new_password)`
  - [ ] Call `ChangePassword` use case
  - [ ] Return HTTP 204 (No Content)
  - [ ] HTTP 400 if current password is invalid
  - [ ] HTTP 403 if trying to change another user's password

- [ ] **Create handler:** `DELETE /api/users/{id}`
  - [ ] Require admin role (`@require_role('admin')`)
  - [ ] Prevent deleting self
  - [ ] Call `DeleteUser` use case
  - [ ] Return HTTP 204 (No Content)
  - [ ] HTTP 404 if not found
  - [ ] HTTP 403 if not admin
  - [ ] HTTP 400 if trying to delete self

#### 4.3 Infrastructure Configuration

- [ ] **Create serverless config** (`backend/infra/functions/users.yml`)
  ```yaml
  functions:
    users:
      handler: src.entrypoints.apigw.users.main.handler
      events:
        - httpApi:
            path: /users/{proxy+}
            method: ANY
  ```

- [ ] Include users config in `backend/infra/serverless.yml`

#### 4.4 Testing

- [ ] **Unit tests** (`backend/tests/unit/use_cases/`)
  - [ ] Test user CRUD operations
  - [ ] Test email uniqueness validation
  - [ ] Test password change
  - [ ] Test permission checks

- [ ] **Integration tests** (`backend/tests/integration/apigw/users/`)
  - [ ] Test all user endpoints
  - [ ] Test admin-only endpoints with non-admin user (403)
  - [ ] Test self vs. other user permissions
  - [ ] Test password change flow

---

## Phase 5: Dashboard API (Medium Priority)

**Priority:** MEDIUM
**Endpoints:** 4
**Estimated:** 16-24 hours
**Timeline:** Week 6

### Endpoints to Implement

- [ ] `GET /api/dashboard/overview` - Get all stats
- [ ] `GET /api/dashboard/events-stats` - Event statistics
- [ ] `GET /api/dashboard/tasks-stats` - Task statistics
- [ ] `GET /api/dashboard/users-stats` - User statistics (admin only)

### Implementation Tasks

#### 5.1 Use Cases

- [ ] **Create use case:** `GetDashboardOverview` (`backend/src/domain/use_cases/get_dashboard_overview.py`)
  - [ ] Input: `GetDashboardOverviewDTO(time_period?)`
  - [ ] Aggregate stats from events, tasks, users
  - [ ] Return `DashboardOverviewDTO(events_stats, tasks_stats, users_stats)`

- [ ] **Create use case:** `GetEventsStats` (`backend/src/domain/use_cases/get_events_stats.py`)
  - [ ] Input: `GetEventsStatsDTO(start_date?, end_date?)`
  - [ ] Query EventRepository with filters
  - [ ] Count events by severity
  - [ ] Count events by account
  - [ ] Count events by region
  - [ ] Calculate time-series data for chart
  - [ ] Return `EventsStatsDTO`

- [ ] **Create use case:** `GetTasksStats` (`backend/src/domain/use_cases/get_tasks_stats.py`)
  - [ ] Input: `GetTasksStatsDTO(start_date?, end_date?)`
  - [ ] Query TaskRepository
  - [ ] Count tasks by status
  - [ ] Count tasks by priority
  - [ ] Count overdue tasks
  - [ ] Calculate completion rate
  - [ ] Return `TasksStatsDTO`

- [ ] **Create use case:** `GetUsersStats` (`backend/src/domain/use_cases/get_users_stats.py`)
  - [ ] Input: none
  - [ ] Query UserRepository
  - [ ] Count users by role
  - [ ] Count active users (last login < 30 days)
  - [ ] Return `UsersStatsDTO`

#### 5.2 API Endpoints

- [ ] **Create handler:** `GET /api/dashboard/overview` (`backend/src/entrypoints/apigw/dashboard/main.py`)
  - [ ] Require authentication (`@require_auth`)
  - [ ] Accept query param: `time_period` (last_24h, last_7d, last_30d)
  - [ ] Call `GetDashboardOverview` use case
  - [ ] Return `DashboardOverviewResponse`
  - [ ] HTTP 200 on success

- [ ] **Create handler:** `GET /api/dashboard/events-stats`
  - [ ] Require authentication (`@require_auth`)
  - [ ] Accept query params: `start_date`, `end_date`
  - [ ] Call `GetEventsStats` use case
  - [ ] Return `EventsStatsResponse`
  - [ ] HTTP 200 on success

- [ ] **Create handler:** `GET /api/dashboard/tasks-stats`
  - [ ] Require authentication (`@require_auth`)
  - [ ] Accept query params: `start_date`, `end_date`
  - [ ] Call `GetTasksStats` use case
  - [ ] Return `TasksStatsResponse`
  - [ ] HTTP 200 on success

- [ ] **Create handler:** `GET /api/dashboard/users-stats`
  - [ ] Require admin role (`@require_role('admin')`)
  - [ ] Call `GetUsersStats` use case
  - [ ] Return `UsersStatsResponse`
  - [ ] HTTP 200 on success
  - [ ] HTTP 403 if not admin

#### 5.3 Infrastructure Configuration

- [ ] **Create serverless config** (`backend/infra/functions/dashboard.yml`)
  ```yaml
  functions:
    dashboard:
      handler: src.entrypoints.apigw.dashboard.main.handler
      events:
        - httpApi:
            path: /dashboard/{proxy+}
            method: ANY
  ```

- [ ] Include dashboard config in `backend/infra/serverless.yml`

#### 5.4 Testing

- [ ] **Unit tests** for dashboard use cases
- [ ] **Integration tests** for dashboard endpoints
- [ ] Test aggregation calculations
- [ ] Test time range filters

---

## Phase 6: Configuration API (Medium Priority)

**Priority:** MEDIUM
**Endpoints:** 4
**Estimated:** 20-30 hours
**Timeline:** Week 7-8

### Endpoints to Implement

- [ ] `GET /api/config/aws` - Get AWS config (singleton)
- [ ] `PUT /api/config/aws` - Update AWS config (singleton)
- [ ] `POST /api/config/aws/test` - Test AWS connection
- [ ] `GET /api/config/monitoring` - Get monitoring config (singleton)
- [ ] `PUT /api/config/monitoring` - Update monitoring config (singleton)

### Implementation Tasks

#### 6.1 Use Cases

- [ ] **Create use case:** `GetAwsConfig` (`backend/src/domain/use_cases/get_aws_config.py`)
  - [ ] Fetch AWS config from AWSConfigRepository (singleton)
  - [ ] Return `AWSConfig` entity
  - [ ] Create default config if not exists

- [ ] **Create use case:** `UpdateAwsConfig` (`backend/src/domain/use_cases/update_aws_config.py`)
  - [ ] Input: `UpdateAwsConfigDTO(default_region?, monitoring_account?, ...)`
  - [ ] Validate AWS config
  - [ ] Update singleton record
  - [ ] Return updated `AWSConfig` entity

- [ ] **Create use case:** `TestAwsConnection` (`backend/src/domain/use_cases/test_aws_connection.py`)
  - [ ] Input: AWS config (or use current)
  - [ ] Try to connect to AWS using credentials
  - [ ] Validate permissions
  - [ ] Return connection test result

- [ ] **Create use case:** `GetMonitoringConfig` (`backend/src/domain/use_cases/get_monitoring_config.py`)
  - [ ] Fetch monitoring config from MonitoringConfigRepository (singleton)
  - [ ] Return `MonitoringConfig` entity
  - [ ] Create default config if not exists

- [ ] **Create use case:** `UpdateMonitoringConfig` (`backend/src/domain/use_cases/update_monitoring_config.py`)
  - [ ] Input: `UpdateMonitoringConfigDTO(query_duration?, chunk_size?, ...)`
  - [ ] Validate monitoring config
  - [ ] Update singleton record
  - [ ] Return updated `MonitoringConfig` entity

#### 6.2 API Endpoints

- [ ] **Create handler:** `GET /api/config/aws` (`backend/src/entrypoints/apigw/config/main.py`)
  - [ ] Require admin role (`@require_role('admin')`)
  - [ ] Call `GetAwsConfig` use case
  - [ ] Return `AWSConfigDTO`
  - [ ] HTTP 200 on success

- [ ] **Create handler:** `PUT /api/config/aws`
  - [ ] Require admin role (`@require_role('admin')`)
  - [ ] Accept `UpdateAwsConfigRequest`
  - [ ] Call `UpdateAwsConfig` use case
  - [ ] Return `AWSConfigDTO` with HTTP 200
  - [ ] HTTP 400 for validation errors

- [ ] **Create handler:** `POST /api/config/aws/test`
  - [ ] Require admin role (`@require_role('admin')`)
  - [ ] Call `TestAwsConnection` use case
  - [ ] Return test result with HTTP 200
  - [ ] Include connection status, error messages

- [ ] **Create handler:** `GET /api/config/monitoring`
  - [ ] Require admin role (`@require_role('admin')`)
  - [ ] Call `GetMonitoringConfig` use case
  - [ ] Return `MonitoringConfigDTO`
  - [ ] HTTP 200 on success

- [ ] **Create handler:** `PUT /api/config/monitoring`
  - [ ] Require admin role (`@require_role('admin')`)
  - [ ] Accept `UpdateMonitoringConfigRequest`
  - [ ] Call `UpdateMonitoringConfig` use case
  - [ ] Return `MonitoringConfigDTO` with HTTP 200
  - [ ] HTTP 400 for validation errors

#### 6.3 Infrastructure Configuration

- [ ] **Create serverless config** (`backend/infra/functions/config.yml`)
  ```yaml
  functions:
    config:
      handler: src.entrypoints.apigw.config.main.handler
      events:
        - httpApi:
            path: /config/{proxy+}
            method: ANY
  ```

- [ ] Include config in `backend/infra/serverless.yml`

#### 6.4 Testing

- [ ] **Unit tests** for config use cases
- [ ] **Integration tests** for config endpoints
- [ ] Test singleton pattern
- [ ] Test AWS connection validation

---

## Testing Strategy

### Unit Tests

Each use case and service should have comprehensive unit tests covering:

- [ ] Happy path scenarios
- [ ] Error scenarios (validation errors, not found, etc.)
- [ ] Edge cases (empty inputs, boundary values)
- [ ] Permission checks
- [ ] Mock all external dependencies (repositories, services)

**Location:** `backend/tests/unit/`

### Integration Tests

Each API endpoint should have integration tests covering:

- [ ] Successful requests with valid data
- [ ] Authentication and authorization
- [ ] Validation errors (400)
- [ ] Not found errors (404)
- [ ] Permission errors (403)
- [ ] Request/response schema validation

**Location:** `backend/tests/integration/`

### End-to-End Tests

- [ ] User registration and login flow
- [ ] Create task from event flow
- [ ] Task lifecycle (create → update → add comment → close)
- [ ] User management flow (admin creates user, user updates profile)
- [ ] Dashboard data aggregation

**Location:** `backend/tests/e2e/`

### Testing Commands

```bash
# Run all tests
make test

# Run specific test file
pytest backend/tests/unit/use_cases/test_authenticate_user.py

# Run with coverage
make coverage

# Run integration tests only
pytest backend/tests/integration/

# Run with verbose output
pytest -v backend/tests/
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Code coverage > 80%
- [ ] Environment variables configured
- [ ] DynamoDB tables created with GSIs
- [ ] JWT secret key configured (production-safe)
- [ ] CORS settings configured for frontend

### Local Deployment (LocalStack)

```bash
# Start LocalStack
make start

# Deploy to local
make deploy stage=local

# Test endpoints
curl -X POST http://localhost:3001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

### Dev Deployment

```bash
# Bootstrap (first time only)
make bootstrap stage=dev

# Deploy to dev
make deploy stage=dev

# Verify deployment
curl https://dev-api.example.com/auth/me \
  -H "Authorization: Bearer <token>"
```

### Production Deployment

- [ ] Review all configuration
- [ ] Update JWT_SECRET_KEY to production value
- [ ] Configure production database
- [ ] Set up CloudWatch alarms
- [ ] Configure rate limiting
- [ ] Enable API logging
- [ ] Deploy to production

```bash
# Package for production
make package stage=prod

# Deploy to production
make deploy stage=prod
```

---

## Reference Files

### Documentation

- [API Specification](../api-specification.yaml)
- [API Endpoints Summary](./API_ENDPOINTS_SUMMARY.txt)
- [Missing API Endpoints](../MISSING_API_ENDPOINTS.md)
- [User Model](../models/user.md)
- [Task Model](../models/task.md)
- [Event Model](../models/event.md)

### Existing Code Examples

- **Event Handler:** `backend/src/entrypoints/apigw/events/main.py`
- **Event Repository:** `backend/src/adapters/db/repositories/event.py`
- **Event Mapper:** `backend/src/adapters/db/mappers/event.py`
- **Event Model:** `backend/src/domain/models/event.py`
- **Base Repository:** `backend/src/adapters/db/repositories/base.py`
- **Base API Handler:** `backend/src/entrypoints/apigw/base.py`

### Frontend API Expectations

- `frontend/src/api/modules/auth.api.ts`
- `frontend/src/api/modules/events.api.ts`
- `frontend/src/api/modules/tasks.api.ts`
- `frontend/src/api/modules/users.api.ts`
- `frontend/src/api/modules/dashboard.api.ts`
- `frontend/src/api/modules/config.api.ts`

---

## Progress Tracking

### Overall Progress: 0/25 endpoints (0%)

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Authentication | ⬜ Not Started | 0/4 (0%) |
| Phase 2: Events Extensions | ⬜ Not Started | 0/1 (0%) |
| Phase 3: Tasks | ⬜ Not Started | 0/7 (0%) |
| Phase 4: Users | ⬜ Not Started | 0/5 (0%) |
| Phase 5: Dashboard | ⬜ Not Started | 0/4 (0%) |
| Phase 6: Configuration | ⬜ Not Started | 0/4 (0%) |

### Legend

- ✅ Completed
- 🔄 In Progress
- ⬜ Not Started
- ❌ Blocked

---

## Notes

1. **Authentication First:** Phase 1 (Authentication) MUST be completed before starting other phases, as all other endpoints require authentication.

2. **Incremental Development:** Each phase can be developed and deployed independently after authentication is complete.

3. **Testing is Critical:** Every endpoint must have unit tests and integration tests before being marked as complete.

4. **Documentation:** Update API specification and docs as you implement each endpoint.

5. **Frontend Coordination:** Coordinate with frontend team to ensure API contracts match expectations.

6. **Security:** Always validate user permissions, sanitize inputs, and protect sensitive data.

---

**Last Updated:** 2025-11-23
**Document Version:** 1.0
**Status:** Ready for Implementation

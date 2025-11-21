# AWS Monitoring Backend - API Endpoints Summary

**Last Updated:** 2025-11-20

---

## Overview

This document lists all API endpoints for the AWS Monitoring backend, organized by:
1. **Currently Deployed** - Endpoints actively running in Lambda
2. **Defined but Not Deployed** - Endpoints with code/configuration but not enabled
3. **Planned/Spec Only** - Endpoints defined in OpenAPI spec but not yet implemented

---

## 1. CURRENTLY DEPLOYED ENDPOINTS

### Event-Driven Functions (EventBridge Triggers)

#### 1.1 Handle Monitoring Events
- **Function Name:** `HandleMonitoringEvents`
- **Handler:** `src.entrypoints.functions.handle_monitoring_events.main.handler`
- **Trigger:** EventBridge rule
- **Event Patterns:** 
  - AWS Health Events
  - GuardDuty Findings
  - Custom monitoring events (source: monitoring*)
- **Purpose:** Processes monitoring events and sends notifications via Slack
- **File:** `/home/user/aws-monitoring/backend/infra/functions/HandleMonitoringEvents.yml`

#### 1.2 Update Deployment
- **Function Name:** `UpdateDeployment`
- **Handler:** `src.entrypoints.functions.update_deployment.main.handler`
- **Trigger:** EventBridge rule
- **Event Pattern:** CloudFormation Stack Status Change (monitoring stacks)
- **Purpose:** Updates agent deployment status when CloudFormation stacks update
- **File:** `/home/user/aws-monitoring/backend/infra/functions/UpdateDeployment.yml`

### Scheduled Functions

#### 1.3 Daily Report
- **Function Name:** `DailyReport`
- **Handler:** `src.entrypoints.functions.daily_report.main.handler`
- **Trigger:** CloudWatch Events (cron: `0 0 * * ? *` - daily at midnight UTC)
- **Purpose:** Generates and sends daily monitoring report to Slack
- **File:** `/home/user/aws-monitoring/backend/infra/functions/DailyReport.yml`

#### 1.4 Query Error Logs
- **Function Name:** `QueryErrorLogs`
- **Handler:** `src.entrypoints.functions.query_error_logs.main.handler`
- **Trigger:** CloudWatch Events (configurable schedule)
- **Purpose:** Queries CloudWatch Logs Insights for errors and publishes events
- **Configuration:**
  - Default Query: `fields @message, @log, @logStream | filter @message like /(?i)(error|fail|exception)/ | sort @timestamp desc | limit 200`
  - Query Duration: 300 seconds
  - Timeout: 15 seconds
  - Delivery Latency: 15 seconds
- **File:** `/home/user/aws-monitoring/backend/infra/functions/QueryErrorLogs.yml`

---

## 2. DEFINED BUT NOT DEPLOYED (Commented Out)

These endpoints have both handler code and configuration files but are commented out in `serverless.yml` (lines 78-86).

### API Gateway REST Endpoints

#### 2.1 Events API
**Base Handler:** `src.entrypoints.apigw.events.main.handler`  
**CORS:** Enabled, origin: `*`, max age: 3600s

**Endpoints:**

| Method | Path | Operation | Function Config | Status |
|--------|------|-----------|-----------------|--------|
| GET | `/events` | List events | `infra/functions/api/Event-ListItems.yml` | Not deployed |
| GET | `/events/{event_id}` | Get event details | `infra/functions/api/Event-GetItem.yml` | Not deployed |

**Supported Query Parameters (for GET /events):**
- `start_date` (int, Unix timestamp) - Filter from date
- `end_date` (int, Unix timestamp) - Filter until date
- `limit` (int, default: 50) - Results per page
- `direction` (str, default: "desc") - Sort order (asc/desc)
- `cursor` (str) - Pagination cursor (base64 encoded)

**Response Format:**
```json
{
  "items": [...],
  "limit": 50,
  "next": null,
  "previous": null
}
```

#### 2.2 Agents API
**Base Handler:** `src.entrypoints.apigw.agents.main.handler`  
**CORS:** Enabled, origin: `*`, max age: 3600s

**Endpoints:**

| Method | Path | Operation | Function Config | Status |
|--------|------|-----------|-----------------|--------|
| GET | `/agents` | List agents | `infra/functions/api/Agent-ListItems.yml` | Not deployed |
| GET | `/agents/{agent_id}` | Get agent details | `infra/functions/api/Agent-GetItem.yml` | Not deployed |
| PUT | `/agents/{agent_id}` | Update agent | `infra/functions/api/Agent-UpdateItem.yml` | Not deployed |

**Response Format:**
```json
{
  "items": [...] or {...},
  "limit": 50,
  "next": null,
  "previous": null
}
```

**Agent Model Fields:**
```python
{
  "account": str,          # AWS Account ID (12 digits)
  "region": str,           # AWS Region
  "status": str,           # Agent deployment status
  "deployed_at": int,      # Unix timestamp
  "created_at": int        # Unix timestamp
}
```

**Event Model Fields:**
```python
{
  "id": str,               # Event ID
  "account": str,          # AWS Account ID
  "region": str,           # AWS Region
  "source": str,           # Event source
  "detail_type": str,      # Event detail type
  "detail": dict,          # Event-specific details
  "severity": int,         # Severity level (0-4)
  "resources": list,       # Affected resources
  "published_at": int,     # Unix timestamp
  "updated_at": int,       # Unix timestamp
  "acknowledged": bool,    # Acknowledgment status
  "notes": str,            # User notes
  "tags": list             # Custom tags
}
```

---

## 3. PLANNED/SPEC ONLY (OpenAPI Defined)

These endpoints are defined in `/home/user/aws-monitoring/docs/api-specification.yaml` but not yet implemented.

**OpenAPI Spec Location:** `/home/user/aws-monitoring/docs/api-specification.yaml`

### 3.1 Authentication Endpoints

| Method | Path | Purpose | Auth Required |
|--------|------|---------|---|
| POST | `/auth/login` | User login with email/password | No |
| POST | `/auth/refresh` | Refresh access token | No |
| POST | `/auth/logout` | Invalidate current token | Yes |

### 3.2 Dashboard Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/dashboard/stats` | Get summary statistics |
| GET | `/dashboard/timeline` | Get events timeline for charts |

**Dashboard Stats Response:**
```json
{
  "total_events": 419,
  "critical_events": 12,
  "high_events": 45,
  "medium_events": 128,
  "low_events": 234,
  "active_agents": 6,
  "inactive_agents": 1,
  "affected_accounts": 8,
  "period": "last_24h"
}
```

### 3.3 Events Endpoints (Extended)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/events` | List events (with full filtering) |
| GET | `/events/{id}` | Get event details |
| PATCH | `/events/{id}` | Update event (acknowledge, notes, tags) |
| GET | `/events/{id}/related` | Get related events |
| GET | `/events/export` | Export events (CSV/JSON/PDF) |
| GET | `/events/accounts` | Get unique account IDs |
| GET | `/events/regions` | Get unique regions |

**Query Parameters for GET /events:**
- `account` - Filter by AWS account ID
- `region` - Filter by AWS region
- `source` - Filter by event source
- `severity` - Filter by severity level (can be multiple)
- `detail_type` - Filter by event type
- `start_date` - Filter from date (Unix timestamp)
- `end_date` - Filter until date (Unix timestamp)
- `search` - Full-text search
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)
- `sort` - Sort field and order (e.g., "-severity,published_at")

### 3.4 Agents Endpoints (Extended)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/agents` | List all agents with filtering |
| POST | `/agents` | Deploy new agent |
| GET | `/agents/{account}` | Get agent details |
| PUT | `/agents/{account}` | Update agent configuration |
| DELETE | `/agents/{account}` | Delete agent |
| GET | `/agents/{account}/metrics` | Get agent performance metrics |
| GET | `/agents/{account}/health` | Get agent health status |
| POST | `/agents/{account}/redeploy` | Trigger agent redeployment |

### 3.5 Reports Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/reports/daily` | Get daily report for specified date |
| POST | `/reports/custom` | Generate custom report |
| GET | `/reports` | List all reports |
| GET | `/reports/{id}/download` | Download report file |

### 3.6 User Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/users/me` | Get current user profile |
| PUT | `/users/me` | Update user profile |
| POST | `/users/me/change-password` | Change password |

### 3.7 Settings Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/settings/notifications` | Get notification preferences |
| PUT | `/settings/notifications` | Update notification preferences |
| GET | `/settings/system` | Get system settings (admin only) |
| PUT | `/settings/system` | Update system settings (admin only) |

---

## 4. DATABASE & DATA MODELS

### Repositories Available

**Location:** `backend/src/adapters/db/repositories/`

1. **EventRepository** (`event.py`)
   - `get(event_id)` - Get event by ID
   - `list(dto)` - List events with filtering and pagination
   - Methods for CRUD operations

2. **AgentRepository** (`agent.py`)
   - `get(agent_id)` - Get agent by ID
   - `list()` - List all agents
   - Methods for deployment status updates

### DynamoDB Table

**Table Name:** `monitoring-local` (or from env var `AWS_DYNAMODB_TABLE`)

**Models:**
- Event model: `backend/src/adapters/db/models/event.py`
- Agent model: `backend/src/adapters/db/models/agent.py`

---

## 5. INFRASTRUCTURE CONFIGURATION

### Serverless Configuration Files

**Main Files:**
- `/home/user/aws-monitoring/backend/serverless.yml` - Main config (defaults to `dev` stage)
- `/home/user/aws-monitoring/backend/serverless.local.yml` - Local overrides
- `backend/infra/configs/local.yml` - Local environment config
- `backend/infra/configs/neos.yml` - Production environment config

### Environment Variables (Lambda)

Set in `serverless.yml` provider section:
- `SERVICE` - Service name (monitoring)
- `STAGE` - Deployment stage (dev/prod/local)
- `POWERTOOLS_LOG_LEVEL` - Logging level
- `AWS_DYNAMODB_TABLE` - DynamoDB table name
- `POWERTOOLS_SERVICE_NAME` - Service name for powertools

Function-specific env vars:
- `MONITORING_WEBHOOK_URL` - Slack webhook for monitoring events
- `DEPLOYMENT_WEBHOOK_URL` - Slack webhook for deployment events
- `REPORT_WEBHOOK_URL` - Slack webhook for daily reports
- `CW_INSIGHTS_QUERY_STRING` - CloudWatch Logs query
- `CW_INSIGHTS_QUERY_DURATION` - Query time range (seconds)
- `CW_INSIGHTS_QUERY_TIMEOUT` - Query timeout (seconds)
- `CW_LOGS_DELIVERY_LATENCY` - Delivery latency (seconds)

### AWS Resources Configured

**EventBridge Rules:**
1. `MonitoringEventRule` - Handles AWS Health, GuardDuty, and custom events
2. `DeploymentEventRule` - Handles CloudFormation stack events

**DynamoDB:**
- Single table for all data models

**SQS:**
- Dead Letter Queue for event processing failures

**IAM:**
- Lambda execution role with permissions for:
  - DynamoDB read/write
  - EventBridge publishing
  - CloudWatch Logs access
  - CloudWatch Logs Insights queries

---

## 6. CODE STRUCTURE

### Entrypoints Directory Structure

```
backend/src/entrypoints/
├── apigw/                           # API Gateway handlers (currently not deployed)
│   ├── base.py                      # APIGatewayRestResolver setup
│   ├── configs.py                   # CORS and config
│   ├── agents/main.py               # Agent API endpoints
│   └── events/main.py               # Event API endpoints
│
└── functions/                       # EventBridge/Scheduled functions (deployed)
    ├── handle_monitoring_events/main.py
    ├── update_deployment/main.py
    ├── daily_report/main.py
    └── query_error_logs/main.py
```

### Use Cases (Domain Layer)

Located at `backend/src/domain/use_cases/`:
- `insert_monitoring_event.py` - Process incoming events
- `update_deployment.py` - Update agent deployment status
- `daily_report.py` - Generate daily reports
- `query_error_logs.py` - Query CloudWatch Logs

---

## 7. API FRAMEWORK

**Framework:** AWS Lambda Powertools Event Handler
- **Class:** `APIGatewayRestResolver`
- **Documentation:** AWS Lambda Powertools
- **Features:**
  - Automatic request/response validation
  - CORS support
  - Exception handling

**Validation:**
- Pydantic v2 for data validation
- Custom error handlers for `ValidationError`

---

## 8. TESTING

### Test Files

**API Integration Tests:**
- `backend/tests/integrations/api/test_events.py`
- `backend/tests/integrations/api/test_agents.py`

**Function Integration Tests:**
- `backend/tests/integrations/functions/test_handle_monitoring_events.py`
- `backend/tests/integrations/functions/test_daily_report.py`
- `backend/tests/integrations/functions/test_query_error_logs.py`
- `backend/tests/integrations/functions/test_update_agent_deployment.py`

**Test Data:**
- `backend/tests/data/` - Sample event payloads for testing

---

## 9. DEPLOYMENT STATUS

### Current Deployment (serverless.yml)

**Active Functions:**
- ✅ HandleMonitoringEvents
- ✅ UpdateDeployment
- ✅ DailyReport
- ✅ QueryErrorLogs

**Commented Out Functions (Not Deployed):**
- ❌ GetEvent (API Gateway)
- ❌ ListEvents (API Gateway)
- ❌ GetAgent (API Gateway)
- ❌ ListAgents (API Gateway)
- ❌ UpdateAgent (API Gateway)

### To Enable API Endpoints

Uncomment lines 78-86 in `backend/serverless.yml`:

```yaml
#  # API -------------------------------------------------------------------------
#  # Events
#  GetEvent: ${file(infra/functions/api/Event-GetItem.yml):function}
#  ListEvents: ${file(infra/functions/api/Event-ListItems.yml):function}

```

Then redeploy with: `make deploy stage=local`

---

## 10. REFERENCES

### Important Documentation Files
- API Specification: `/home/user/aws-monitoring/docs/api-specification.yaml`
- Screen-API Mapping: `/home/user/aws-monitoring/docs/screen-api-mapping.md`
- Database Schema: `/home/user/aws-monitoring/docs/db.md`
- Architecture: `/home/user/aws-monitoring/docs/overview.md`

### Key Source Files
- Events Handler: `backend/src/entrypoints/apigw/events/main.py`
- Agents Handler: `backend/src/entrypoints/apigw/agents/main.py`
- Event Repository: `backend/src/adapters/db/repositories/event.py`
- Agent Repository: `backend/src/adapters/db/repositories/agent.py`

---

**End of Summary**

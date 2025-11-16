# Frontend Screen Design

## Overview

This document outlines all screens/pages in the AWS Monitoring web application, their purpose, components, and user flows.

## Screen Hierarchy

```
AWS Monitoring Application
│
├── Public Screens (No Auth Required)
│   └── Login
│
├── Protected Screens (Auth Required)
│   ├── Dashboard (Home)
│   ├── Events
│   │   ├── Events List
│   │   └── Event Detail
│   ├── Agents
│   │   ├── Agents List
│   │   ├── Agent Detail
│   │   └── Deploy Agent
│   ├── Reports
│   │   ├── Daily Reports
│   │   └── Custom Reports
│   └── Settings
│       ├── User Profile
│       ├── Notifications
│       └── System Configuration
```

## Screen Designs

### 1. Login Screen

**Route:** `/login`

**Purpose:** Authenticate users to access the monitoring system

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              AWS Monitoring System                      │
│                                                         │
│         ┌─────────────────────────────┐                │
│         │  Email                      │                │
│         │  [________________]         │                │
│         │                             │                │
│         │  Password                   │                │
│         │  [________________]         │                │
│         │                             │                │
│         │  [x] Remember me            │                │
│         │                             │                │
│         │  [      Login      ]        │                │
│         │                             │                │
│         │  Forgot password?           │                │
│         └─────────────────────────────┘                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Components:**
- Email input field
- Password input field (with show/hide toggle)
- Remember me checkbox
- Login button
- Forgot password link

**API Endpoints:**
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/refresh` - Refresh access token

**User Flow:**
1. User enters email and password
2. Click Login button
3. System validates credentials
4. On success: Redirect to Dashboard
5. On failure: Show error message

**Validation:**
- Email format validation
- Password minimum length (8 characters)
- Rate limiting (max 5 attempts per 15 minutes)

---

### 2. Dashboard (Home)

**Route:** `/` or `/dashboard`

**Purpose:** Provide high-level overview of monitoring system health and recent activity

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ [AWS Monitoring]    [Dashboard] [Events] [Agents]...   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Dashboard                                   [User ▼]  │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │ Critical │  │   High   │  │  Medium  │  │  Low   ││
│  │    12    │  │    45    │  │   128    │  │  234   ││
│  │ Events   │  │ Events   │  │ Events   │  │ Events ││
│  └──────────┘  └──────────┘  └──────────┘  └────────┘│
│                                                         │
│  ┌─────────────────────────┐  ┌──────────────────────┐│
│  │ Recent Events           │  │ Agent Health         ││
│  ├─────────────────────────┤  ├──────────────────────┤│
│  │ 🔴 Lambda timeout       │  │ 🟢 Account: 12345    ││
│  │    account-123          │  │ 🟢 Account: 67890    ││
│  │ 🟠 ECS task failed      │  │ 🔴 Account: 11111    ││
│  │    account-456          │  │ 🟢 Account: 22222    ││
│  │ 🔵 CloudWatch alarm     │  │                      ││
│  │    account-789          │  │ 4 agents active      ││
│  │ [View All Events]       │  │ 1 agent inactive     ││
│  └─────────────────────────┘  └──────────────────────┘│
│                                                         │
│  ┌─────────────────────────────────────────────────────┐
│  │ Events Over Time (Last 7 Days)                     │
│  ├─────────────────────────────────────────────────────┤
│  │          📊 Line Chart                              │
│  │  Events                                             │
│  │    │                                                │
│  │  50├─────╱╲──────╱╲────                            │
│  │    │    ╱  ╲    ╱  ╲                               │
│  │  25├───╱────╲──╱────╲───                           │
│  │    │                                                │
│  │  0 └────────────────────                           │
│  │     Mon Tue Wed Thu Fri Sat Sun                    │
│  └─────────────────────────────────────────────────────┘
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Components:**
- **Statistics Cards** (4 cards)
  - Critical events count
  - High severity events count
  - Medium severity events count
  - Low severity events count

- **Recent Events Widget**
  - List of last 10 events
  - Severity indicator (colored dot)
  - Event type
  - Account ID
  - Timestamp
  - "View All Events" link

- **Agent Health Widget**
  - List of all agents with status
  - Health indicator (colored dot)
  - Account ID and region
  - Active/Inactive count summary
  - "Manage Agents" link

- **Events Timeline Chart**
  - Line chart showing events over last 7 days
  - Filterable by severity
  - Interactive tooltips

**API Endpoints:**
- `GET /api/dashboard/stats` - Get summary statistics
- `GET /api/events?limit=10&sort=-published_at` - Get recent events
- `GET /api/agents` - Get all agents with health status
- `GET /api/dashboard/timeline?days=7` - Get events timeline data

**Real-time Updates:**
- Auto-refresh every 30 seconds
- WebSocket connection for real-time events (optional)

---

### 3. Events List Screen

**Route:** `/events`

**Purpose:** Display all monitoring events with filtering and search capabilities

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ [AWS Monitoring]    Dashboard [Events] Agents...       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Events                                      [User ▼]  │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐
│  │ Filters                                             │
│  ├─────────────────────────────────────────────────────┤
│  │ [Account ▼] [Region ▼] [Severity ▼] [Date Range]  │
│  │ [Apply Filters]  [Reset]          [🔍 Search...]   │
│  └─────────────────────────────────────────────────────┘
│                                                         │
│  Showing 1-20 of 419 events                [Export ▼]  │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐
│  │ Severity │ Account  │ Region    │ Type    │ Time   │
│  ├─────────────────────────────────────────────────────┤
│  │ 🔴 CRIT │ 123456   │ us-east-1 │ Lambda  │ 2m ago ││
│  │ 🟠 HIGH │ 123456   │ us-west-2 │ ECS     │ 5m ago ││
│  │ 🔵 MED  │ 789012   │ us-east-1 │ CW Alrm │ 8m ago ││
│  │ 🟢 LOW  │ 345678   │ eu-west-1 │ Lambda  │ 10m    ││
│  │ ...     │ ...      │ ...       │ ...     │ ...    ││
│  └─────────────────────────────────────────────────────┘
│                                                         │
│  [← Previous]  Page 1 of 21  [Next →]                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Components:**
- **Filter Bar**
  - Account dropdown (multi-select)
  - Region dropdown (multi-select)
  - Severity dropdown (multi-select)
  - Date range picker (start/end date)
  - Apply filters button
  - Reset filters button
  - Search input (full-text search)

- **Action Bar**
  - Results count display
  - Export dropdown (CSV, JSON, PDF)
  - Bulk actions (if multiple selection enabled)

- **Events Table**
  - Sortable columns
  - Clickable rows (navigate to detail)
  - Pagination controls
  - Severity indicator with icon
  - Relative time display (with hover for absolute time)
  - Empty state when no results

**API Endpoints:**
- `GET /api/events?account={}&region={}&severity={}&start_date={}&end_date={}&page={}&page_size={}` - Get filtered events
- `GET /api/events/export?format={}` - Export events
- `GET /api/events/accounts` - Get list of accounts for filter
- `GET /api/events/regions` - Get list of regions for filter

**Features:**
- URL parameters sync with filters (shareable links)
- Infinite scroll option
- Virtual scrolling for large datasets
- Auto-refresh toggle

---

### 4. Event Detail Screen

**Route:** `/events/:id`

**Purpose:** Display detailed information about a specific monitoring event

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ [AWS Monitoring]    Dashboard Events [Agents]...       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [← Back to Events]                          [User ▼]  │
│                                                         │
│  Event Details                                          │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐
│  │ 🔴 CRITICAL - Lambda Function Timeout               │
│  ├─────────────────────────────────────────────────────┤
│  │                                                      │
│  │ Event ID:       evt-123456789                       │
│  │ Account:        123456789012                        │
│  │ Region:         us-east-1                           │
│  │ Source:         aws.lambda                          │
│  │ Published:      2024-01-15 10:30:45 UTC            │
│  │ Updated:        2024-01-15 10:31:12 UTC            │
│  │                                                      │
│  └─────────────────────────────────────────────────────┘
│                                                         │
│  ┌─────────────────────────────────────────────────────┐
│  │ Event Details                                       │
│  ├─────────────────────────────────────────────────────┤
│  │                                                      │
│  │ Function Name: process-orders-prod                  │
│  │ Error Type:    Task timed out after 30.00 seconds  │
│  │ Request ID:    abc-def-ghi-123                      │
│  │                                                      │
│  │ Stack Trace:                                        │
│  │ ┌────────────────────────────────────────────────┐ │
│  │ │ at processOrder (/var/task/index.js:45:12)    │ │
│  │ │ at Runtime.handler (/var/task/index.js:12:8)  │ │
│  │ └────────────────────────────────────────────────┘ │
│  │                                                      │
│  └─────────────────────────────────────────────────────┘
│                                                         │
│  ┌─────────────────────────────────────────────────────┐
│  │ Affected Resources                                  │
│  ├─────────────────────────────────────────────────────┤
│  │ • arn:aws:lambda:us-east-1:123:function:process-...│
│  │ • arn:aws:logs:us-east-1:123:log-group:/aws/lam... │
│  └─────────────────────────────────────────────────────┘
│                                                         │
│  ┌─────────────────────────────────────────────────────┐
│  │ Raw Event Data                     [Copy JSON]      │
│  ├─────────────────────────────────────────────────────┤
│  │ {                                                    │
│  │   "id": "evt-123456789",                            │
│  │   "account": "123456789012",                        │
│  │   ...                                               │
│  │ }                                                    │
│  └─────────────────────────────────────────────────────┘
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Components:**
- **Event Header**
  - Severity badge with icon
  - Event title/type
  - Quick actions (Acknowledge, Create ticket, etc.)

- **Event Metadata Card**
  - Event ID
  - Account and Region
  - Source service
  - Timestamps (published, updated)
  - Status badges

- **Event Details Card**
  - Parsed event details specific to event type
  - Lambda: Function name, error type, request ID, stack trace
  - ECS: Cluster, task, container, exit code
  - CloudWatch: Alarm name, metric, threshold

- **Affected Resources Card**
  - List of AWS resource ARNs
  - Links to AWS console (if applicable)

- **Raw Event Data Card**
  - JSON viewer with syntax highlighting
  - Copy to clipboard button
  - Expand/collapse sections

**API Endpoints:**
- `GET /api/events/{id}` - Get event details
- `PATCH /api/events/{id}` - Update event (acknowledge, add notes)
- `GET /api/events/{id}/related` - Get related events

**Features:**
- Breadcrumb navigation
- Related events sidebar
- Event timeline (if multiple updates)
- Notes/comments section

---

### 5. Agents List Screen

**Route:** `/agents`

**Purpose:** Manage monitoring agents deployed across AWS accounts

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ [AWS Monitoring]    Dashboard Events [Agents]...       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Agents                                      [User ▼]  │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Active  │  │ Deploying│  │  Failed  │             │
│  │    4     │  │    1     │  │    1     │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                         │
│  [+ Deploy New Agent]                    [🔍 Search]   │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐
│  │ Account    │ Region    │ Status      │ Deployed   ││
│  ├─────────────────────────────────────────────────────┤
│  │ 123456789  │ us-east-1 │ 🟢 Active   │ 2024-01-01 ││
│  │ 123456789  │ us-west-2 │ 🟢 Active   │ 2024-01-01 ││
│  │ 789012345  │ us-east-1 │ 🟡 Deploying│ 2024-01-15 ││
│  │ 345678901  │ eu-west-1 │ 🟢 Active   │ 2024-01-10 ││
│  │ 567890123  │ ap-south-1│ 🔴 Failed   │ 2024-01-12 ││
│  │ 234567890  │ us-east-1 │ 🟢 Active   │ 2024-01-05 ││
│  └─────────────────────────────────────────────────────┘
│                                                         │
│  Actions: [Update] [Delete] [View Logs] [Redeploy]    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Components:**
- **Status Summary Cards**
  - Active agents count
  - Deploying agents count
  - Failed agents count
  - Inactive agents count

- **Actions Bar**
  - Deploy new agent button (opens modal)
  - Search/filter input
  - Refresh button

- **Agents Table**
  - Sortable columns
  - Status indicator with icon
  - Last deployed timestamp
  - Row actions dropdown
    - View details
    - Update agent
    - Redeploy
    - View logs
    - Delete

- **Deploy Agent Modal**
  - Account ID input
  - Region selector
  - Configuration options
  - Deploy button

**API Endpoints:**
- `GET /api/agents` - Get all agents
- `POST /api/agents` - Deploy new agent
- `GET /api/agents/{account}` - Get agent details
- `PUT /api/agents/{account}` - Update agent
- `DELETE /api/agents/{account}` - Delete agent
- `POST /api/agents/{account}/redeploy` - Redeploy agent

**Features:**
- Auto-refresh status every 60 seconds
- Bulk operations (select multiple agents)
- Filter by status, region, account
- Export agent list

---

### 6. Agent Detail Screen

**Route:** `/agents/:account`

**Purpose:** View detailed information about a specific monitoring agent

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ [AWS Monitoring]    Dashboard Events Agents...         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [← Back to Agents]                          [User ▼]  │
│                                                         │
│  Agent Details - 123456789012                           │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐
│  │ 🟢 Active                      [Update] [Redeploy]  │
│  ├─────────────────────────────────────────────────────┤
│  │                                                      │
│  │ Account:        123456789012                        │
│  │ Region:         us-east-1                           │
│  │ Status:         CREATE_COMPLETE                     │
│  │ Deployed:       2024-01-01 08:00:00 UTC            │
│  │ Last Updated:   2024-01-15 10:30:00 UTC            │
│  │                                                      │
│  └─────────────────────────────────────────────────────┘
│                                                         │
│  ┌────────────────────────┐  ┌──────────────────────┐ │
│  │ Metrics (Last 24h)     │  │ Health Check         │ │
│  ├────────────────────────┤  ├──────────────────────┤ │
│  │ Events Published: 1,234│  │ Status: 🟢 Healthy   │ │
│  │ Errors Detected:  45   │  │ Last Check: 2m ago   │ │
│  │ Query Duration:   2.3s │  │ Uptime: 99.8%        │ │
│  │ Log Groups:       12   │  │ Error Rate: 0.2%     │ │
│  └────────────────────────┘  └──────────────────────┘ │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐
│  │ Recent Events Published                             │
│  ├─────────────────────────────────────────────────────┤
│  │ • Lambda timeout - process-orders (2m ago)          │
│  │ • ECS task failed - web-service (5m ago)           │
│  │ • CloudWatch alarm - high-cpu (8m ago)             │
│  │ [View All Events from this Agent]                  │
│  └─────────────────────────────────────────────────────┘
│                                                         │
│  ┌─────────────────────────────────────────────────────┐
│  │ Configuration                                       │
│  ├─────────────────────────────────────────────────────┤
│  │ Query String:   fields @message | filter...        │
│  │ Query Duration: 300 seconds                         │
│  │ Delivery Latency: 15 seconds                       │
│  │ Chunk Size:     10 log groups                      │
│  └─────────────────────────────────────────────────────┘
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Components:**
- **Agent Status Card**
  - Status indicator
  - Action buttons (Update, Redeploy, Delete)
  - Key metadata

- **Metrics Cards**
  - Events published count
  - Errors detected count
  - Average query duration
  - Log groups monitored count

- **Health Check Card**
  - Current health status
  - Last health check time
  - Uptime percentage
  - Error rate

- **Recent Events Widget**
  - Last 10 events published by this agent
  - Link to filtered events view

- **Configuration Card**
  - CloudWatch query configuration
  - Timing parameters
  - Edit configuration button

**API Endpoints:**
- `GET /api/agents/{account}` - Get agent details
- `GET /api/agents/{account}/metrics` - Get agent metrics
- `GET /api/agents/{account}/health` - Get health status
- `GET /api/events?agent_account={account}` - Get events from agent
- `PUT /api/agents/{account}/config` - Update configuration

---

### 7. Reports Screen

**Route:** `/reports`

**Purpose:** View daily/weekly reports and generate custom reports

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ [AWS Monitoring]    Dashboard Events Agents [Reports]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Reports                                     [User ▼]  │
│                                                         │
│  [Daily Reports] [Custom Reports]                      │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐
│  │ Daily Report - 2024-01-15                           │
│  ├─────────────────────────────────────────────────────┤
│  │                                                      │
│  │ Summary                                             │
│  │ • Total Events:      419                           │
│  │ • Critical Events:   12                            │
│  │ • High Events:       45                            │
│  │ • Affected Accounts: 8                             │
│  │ • Active Agents:     6                             │
│  │                                                      │
│  │ ┌────────────────────────────────────────────────┐ │
│  │ │ Events by Severity      📊 Pie Chart           │ │
│  │ │                                                 │ │
│  │ │   Critical: 3%                                  │ │
│  │ │   High: 11%                                     │ │
│  │ │   Medium: 31%                                   │ │
│  │ │   Low: 55%                                      │ │
│  │ └────────────────────────────────────────────────┘ │
│  │                                                      │
│  │ ┌────────────────────────────────────────────────┐ │
│  │ │ Top Errors                                      │ │
│  │ │ 1. Lambda timeout (25 occurrences)             │ │
│  │ │ 2. ECS task failed (18 occurrences)            │ │
│  │ │ 3. CloudWatch alarm (15 occurrences)           │ │
│  │ └────────────────────────────────────────────────┘ │
│  │                                                      │
│  │ [Download PDF] [Download CSV] [Email Report]       │
│  └─────────────────────────────────────────────────────┘
│                                                         │
│  ┌─────────────────────────────────────────────────────┐
│  │ Previous Reports                                    │
│  │ • 2024-01-14 [View] [Download]                     │
│  │ • 2024-01-13 [View] [Download]                     │
│  │ • 2024-01-12 [View] [Download]                     │
│  └─────────────────────────────────────────────────────┘
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Components:**
- **Report Tabs**
  - Daily Reports tab
  - Custom Reports tab

- **Daily Report View**
  - Date selector
  - Summary statistics cards
  - Charts and visualizations
    - Events by severity (pie chart)
    - Events timeline (line chart)
    - Events by account (bar chart)
  - Top errors table
  - Agent health summary
  - Export actions (PDF, CSV, Email)

- **Custom Report Builder**
  - Date range picker
  - Account selector (multi-select)
  - Region selector (multi-select)
  - Severity filter
  - Report format selector
  - Generate button

- **Previous Reports List**
  - Chronological list of past reports
  - View and download actions

**API Endpoints:**
- `GET /api/reports/daily?date={}` - Get daily report
- `POST /api/reports/custom` - Generate custom report
- `GET /api/reports` - List previous reports
- `GET /api/reports/{id}/download?format={}` - Download report

---

### 8. Settings Screen

**Route:** `/settings`

**Purpose:** Configure user preferences, notifications, and system settings

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ [AWS Monitoring]    Dashboard Events Agents Reports    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Settings                                    [User ▼]  │
│                                                         │
│  ┌──────────────┐  ┌────────────────────────────────┐ │
│  │ Profile      │  │ User Profile                    │ │
│  │ Notifications│  │                                 │ │
│  │ System       │  │ Name:  [John Doe            ]  │ │
│  │              │  │ Email: [john@example.com    ]  │ │
│  │              │  │ Role:  Administrator           │ │
│  │              │  │                                 │ │
│  │              │  │ [Save Changes]                 │ │
│  └──────────────┘  └────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Sections:**

#### 8.1 Profile Tab
- Name input
- Email input (read-only)
- Role display (read-only)
- Change password button
- Save changes button

#### 8.2 Notifications Tab
- Email notifications toggle
- Slack notifications toggle
- Notification preferences by severity
  - Critical: Always notify
  - High: Notify during business hours
  - Medium: Daily digest
  - Low: Weekly digest
- Save preferences button

#### 8.3 System Tab (Admin only)
- Master stack configuration
- Agent deployment settings
- Retention policies
- Integration settings (Slack webhook URL)
- Save configuration button

**API Endpoints:**
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update user profile
- `POST /api/users/me/change-password` - Change password
- `GET /api/settings/notifications` - Get notification settings
- `PUT /api/settings/notifications` - Update notification settings
- `GET /api/settings/system` - Get system settings (admin)
- `PUT /api/settings/system` - Update system settings (admin)

---

## User Flows

### Flow 1: User Login
```
1. Navigate to /login
2. Enter email and password
3. Click "Login"
4. API: POST /api/auth/login
5. Store JWT token
6. Redirect to /dashboard
```

### Flow 2: View Recent Events
```
1. From Dashboard
2. See recent events in widget
3. Click "View All Events"
4. Navigate to /events
5. API: GET /api/events?limit=20&page=1
6. Display events table
```

### Flow 3: Filter Events
```
1. On /events page
2. Select filters (account, region, severity, date)
3. Click "Apply Filters"
4. API: GET /api/events?account=123&severity=critical
5. Update URL with query params
6. Display filtered results
```

### Flow 4: View Event Details
```
1. On /events page
2. Click event row
3. Navigate to /events/{id}
4. API: GET /api/events/{id}
5. Display event details
6. Option to view related events
```

### Flow 5: Deploy New Agent
```
1. On /agents page
2. Click "Deploy New Agent"
3. Modal opens with form
4. Enter account ID and region
5. Click "Deploy"
6. API: POST /api/agents
7. Show deployment progress
8. Update agents list on completion
```

### Flow 6: View Daily Report
```
1. Navigate to /reports
2. Select date from date picker
3. API: GET /api/reports/daily?date=2024-01-15
4. Display report with charts
5. Option to download PDF or CSV
6. API: GET /api/reports/{id}/download?format=pdf
```

### Flow 7: Configure Notifications
```
1. Navigate to /settings
2. Click "Notifications" tab
3. Toggle notification channels
4. Set severity preferences
5. Click "Save"
6. API: PUT /api/settings/notifications
7. Show success message
```

## Responsive Design Considerations

### Mobile Layout (< 768px)
- Collapsible sidebar navigation
- Stack cards vertically
- Simplified tables (hide non-essential columns)
- Touch-friendly buttons (min 44px height)
- Bottom navigation bar

### Tablet Layout (768px - 1024px)
- Side navigation drawer
- 2-column layout for cards
- Full tables with horizontal scroll

### Desktop Layout (> 1024px)
- Full sidebar navigation
- Multi-column layouts
- Wide tables
- Side panels for details

## Accessibility Features

- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode
- Focus indicators
- ARIA labels on interactive elements
- Alt text for images and icons

## Loading States

- Skeleton screens for initial load
- Spinner for data fetching
- Progress bars for long operations (agent deployment)
- Optimistic UI updates where applicable

## Error States

- Inline form validation errors
- Toast notifications for API errors
- Empty states with helpful messages
- 404 page for invalid routes
- 500 page for server errors
- Network error handling with retry

## Performance Optimizations

- Lazy loading of routes
- Virtual scrolling for large tables
- Image lazy loading
- API response caching
- Debounced search inputs
- Pagination for large datasets
- Code splitting by route

---

This screen design provides a complete user experience for the AWS Monitoring application with clear navigation, comprehensive functionality, and intuitive workflows.

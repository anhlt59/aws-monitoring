ss# AWS Config Monitoring - Requirements Document

## 1. Executive Summary

### Purpose
Extend the existing AWS monitoring system to include AWS Config compliance monitoring, providing real-time visibility into resource configuration compliance across multiple AWS accounts.

### Goals
- Monitor AWS Config rule compliance status across all monitored accounts
- Detect and alert on configuration compliance changes
- Aggregate compliance data for reporting and audit purposes
- Maintain consistency with existing monitoring architecture (hexagonal, master-agent pattern)

## 2. Background

### Current System
The AWS Monitoring project currently supports:
- CloudWatch Log error detection
- CloudWatch Alarm monitoring
- AWS Health events
- GuardDuty findings
- CloudFormation stack status tracking

### Gap Analysis
- **Missing**: AWS Config rule compliance monitoring
- **Missing**: Resource configuration change tracking
- **Missing**: Compliance drift detection and alerting

## 3. Functional Requirements

### FR-1: AWS Config Event Detection
**Priority**: High
**Description**: Monitor AWS Config compliance events in real-time

**Acceptance Criteria**:
- System detects AWS Config rule compliance state changes (COMPLIANT → NON_COMPLIANT)
- System captures configuration change events
- System identifies affected resources and rules
- Events are captured within 5 minutes of AWS Config evaluation

**Event Sources**:
- `aws.config` - Config rule compliance change notifications
- EventBridge patterns for compliance changes

### FR-2: Compliance Event Processing
**Priority**: High
**Description**: Process and store AWS Config compliance events

**Acceptance Criteria**:
- Parse AWS Config event payloads
- Extract rule name, resource type, compliance status, and resource ID
- Store events in DynamoDB with existing event schema
- Maintain event history for compliance auditing

**Data Points to Capture**:
- Config rule name
- Resource type (e.g., EC2, S3, IAM)
- Resource ID (e.g., instance-id, bucket name)
- Previous compliance status
- New compliance status
- Evaluation timestamp
- Compliance reason/annotation

### FR-3: Compliance Notifications
**Priority**: High
**Description**: Alert on critical compliance violations

**Acceptance Criteria**:
- Send Slack notifications for NON_COMPLIANT transitions
- Include rule name, resource details, and remediation guidance
- Support severity-based filtering (critical rules only)
- Batch non-critical violations for daily reporting

**Notification Rules**:
- **Immediate**: High-severity compliance failures (security rules)
- **Batched**: Low/medium-severity violations (operational rules)
- **Daily Report**: Summary of all compliance status changes

### FR-4: Compliance Status Querying
**Priority**: Medium
**Description**: API to query compliance history and current status

**Acceptance Criteria**:
- REST API endpoint to list compliance events by account/region
- Filter by rule name, resource type, compliance status
- Pagination support for large result sets
- Response time < 200ms for filtered queries

**API Endpoints**:
```
GET /events?source=aws.config&account={account_id}
GET /events?source=aws.config&status=NON_COMPLIANT
GET /events?source=aws.config&rule_name={rule_name}
```

### FR-5: Compliance Reporting
**Priority**: Medium
**Description**: Daily/weekly compliance summary reports

**Acceptance Criteria**:
- Daily report includes compliance status summary by account
- Report shows new NON_COMPLIANT resources
- Report includes trend analysis (improving/degrading)
- Report sent via Slack with charts/visualizations

**Report Sections**:
1. Compliance Score by Account (% compliant resources)
2. New Violations (last 24 hours)
3. Resolved Violations (last 24 hours)
4. Top Non-Compliant Rules
5. Resource Types with Most Violations

### FR-6: Multi-Account Support
**Priority**: High
**Description**: Monitor AWS Config across all agent-deployed accounts

**Acceptance Criteria**:
- Agent stack configures EventBridge rules for Config events
- Config events routed to master account via cross-account EventBridge
- Account-specific compliance tracking in master DynamoDB
- No additional IAM permissions required beyond EventBridge access

## 4. Non-Functional Requirements

### NFR-1: Performance
- Event processing latency: < 5 seconds from Config evaluation to storage
- API query response time: < 200ms (p95)
- Daily report generation: < 60 seconds
- Support 1000+ compliance events per day across all accounts

### NFR-2: Scalability
- Support 50+ AWS accounts
- Handle 100+ Config rules per account
- Process 5000+ resource evaluations per day
- Auto-scale Lambda concurrency for burst traffic

### NFR-3: Reliability
- Event processing success rate: > 99.5%
- Dead Letter Queue (DLQ) for failed event processing
- Automatic retry with exponential backoff
- Graceful degradation if DynamoDB throttled

### NFR-4: Security
- Minimal IAM permissions (least privilege)
- Encryption at rest for DynamoDB data
- TLS 1.2+ for all API communications
- No secrets in code or environment variables (use AWS Secrets Manager)

### NFR-5: Maintainability
- Follow existing hexagonal architecture patterns
- 90%+ test coverage for new code
- Type-safe with Pydantic v2 validation
- Comprehensive logging for troubleshooting

### NFR-6: Cost Optimization
- Use existing DynamoDB table (no new tables)
- Leverage EventBridge filtering to reduce Lambda invocations
- Batch notifications to reduce Slack API calls
- On-demand DynamoDB capacity for cost efficiency

## 5. Technical Constraints

### TC-1: AWS Service Availability
- AWS Config must be enabled in monitored accounts
- Config rules must be configured and active
- EventBridge permissions required for cross-account event delivery

### TC-2: Architecture Alignment
- Must follow master-agent hub-and-spoke pattern
- Domain layer remains pure (no AWS SDK dependencies)
- Adapters handle AWS-specific event parsing
- Use existing Event domain model with source filtering

### TC-3: Backward Compatibility
- New features must not break existing monitoring functionality
- Existing event schema supports Config events without migration
- Notification templates extensible for new event types

## 6. Event Type Specifications

### AWS Config Compliance Change Event
**Source**: `aws.config`
**Detail Type**: `Config Rules Compliance Change`

**Example Event**:
```json
{
  "version": "0",
  "id": "a1b2c3d4-5678-90ab-cdef-EXAMPLE11111",
  "detail-type": "Config Rules Compliance Change",
  "source": "aws.config",
  "account": "123456789012",
  "time": "2025-01-15T12:34:56Z",
  "region": "us-east-1",
  "resources": [
    "arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0"
  ],
  "detail": {
    "resourceId": "i-1234567890abcdef0",
    "resourceType": "AWS::EC2::Instance",
    "configRuleNames": ["required-tags"],
    "messageType": "ComplianceChangeNotification",
    "newEvaluationResult": {
      "evaluationResultIdentifier": {
        "evaluationResultQualifier": {
          "configRuleName": "required-tags",
          "resourceType": "AWS::EC2::Instance",
          "resourceId": "i-1234567890abcdef0"
        },
        "orderingTimestamp": "2025-01-15T12:34:56.789Z"
      },
      "complianceType": "NON_COMPLIANT",
      "resultRecordedTime": "2025-01-15T12:34:56.789Z",
      "configRuleInvokedTime": "2025-01-15T12:34:50.123Z",
      "annotation": "Resource is missing required tags: Environment, Owner"
    },
    "oldEvaluationResult": {
      "complianceType": "COMPLIANT"
    },
    "configRuleName": "required-tags",
    "configRuleArn": "arn:aws:config:us-east-1:123456789012:config-rule/config-rule-abcdef"
  }
}
```

### AWS Config Configuration Change Event
**Source**: `aws.config`
**Detail Type**: `Config Configuration Item Change`

**Use Case**: Track when resource configurations change (even if compliant)

## 7. User Stories

### US-1: Security Engineer - Immediate Security Violation Alerts
**As a** security engineer
**I want** immediate Slack notifications for security Config rule violations
**So that** I can respond quickly to potential security issues

**Acceptance Criteria**:
- Receive Slack notification within 5 minutes of NON_COMPLIANT status
- Notification includes rule name, resource ID, and violation reason
- Link to AWS Console for quick investigation

### US-2: DevOps Engineer - Compliance Trend Visibility
**As a** DevOps engineer
**I want** daily compliance status reports
**So that** I can track compliance improvement over time

**Acceptance Criteria**:
- Daily Slack message with compliance summary
- Shows compliance score trend (last 7 days)
- Highlights accounts with declining compliance

### US-3: Audit Manager - Compliance History Queries
**As an** audit manager
**I want** to query historical compliance events via API
**So that** I can generate audit reports for compliance reviews

**Acceptance Criteria**:
- REST API to filter events by time range and rule name
- Export results as JSON for further analysis
- Query performance < 200ms for 90-day history

## 8. Dependencies

### External Dependencies
- AWS Config enabled in all monitored accounts
- Config rules created and evaluated regularly
- EventBridge permissions configured for cross-account delivery

### Internal Dependencies
- Existing event processing Lambda (`HandleMonitoringEvents`)
- DynamoDB events table with current schema
- Slack webhook configuration for notifications
- EventBridge custom event bus in master account

## 9. Success Metrics

### Adoption Metrics
- Number of accounts with Config monitoring enabled
- Number of Config rules monitored
- Total compliance events processed per day

### Performance Metrics
- Event processing latency (p50, p95, p99)
- API query response times
- Lambda cold start frequency

### Reliability Metrics
- Event processing success rate
- DLQ message count (failed events)
- Notification delivery success rate

### Business Impact Metrics
- Mean time to detect (MTTD) compliance violations
- Mean time to resolve (MTTR) violations
- Compliance score improvement over time

## 10. Out of Scope

The following are explicitly **not** included in this design:

- Automated remediation of non-compliant resources
- Custom Config rule creation or management
- Integration with third-party compliance frameworks (SOC2, PCI-DSS)
- Real-time streaming compliance dashboards
- Cost analysis of compliance violations
- Integration with ticketing systems (Jira, ServiceNow)

These features may be considered for future iterations.

## 11. Open Questions

1. **Config Rule Priority**: Should all Config rules trigger notifications, or only specific critical rules?
2. **Retention Policy**: How long should compliance events be retained in DynamoDB (90 days? 1 year?)?
3. **Remediation Guidance**: Should notifications include automated remediation steps or documentation links?
4. **Multi-Region**: Should Config events be aggregated by region or account-level only?
5. **Historical Backfill**: Should system backfill historical compliance events when first enabled?

## 12. Next Steps

1. **Requirements Review**: Stakeholder approval of requirements (this document)
2. **Design Phase**: Create technical design specification (architecture, data models, API specs)
3. **Proof of Concept**: Build minimal viable Config monitoring for single account
4. **Implementation**: Full feature development with test coverage
5. **Testing**: Integration and load testing across multiple accounts
6. **Deployment**: Gradual rollout with monitoring and validation
7. **Documentation**: User guide and operational runbook

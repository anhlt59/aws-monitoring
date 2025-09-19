# AWS Config Monitoring - Technical Design Specification

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Monitored AWS Account                        │
│                                                                   │
│  ┌──────────────┐         ┌─────────────────┐                  │
│  │  AWS Config  │────────>│   EventBridge   │                  │
│  │   Rules      │         │   (Local Bus)   │                  │
│  └──────────────┘         └────────┬────────┘                  │
│                                     │                            │
│                                     │ Cross-Account Rule         │
└─────────────────────────────────────┼────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Master AWS Account                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              EventBridge Custom Bus                       │  │
│  │         (receives cross-account Config events)            │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │     HandleMonitoringEvents Lambda                        │   │
│  │  - Parse ConfigEvent                                     │   │
│  │  - Extract compliance data                               │   │
│  │  - Store in DynamoDB                                     │   │
│  │  - Trigger notifications                                 │   │
│  └──────────┬───────────────────────┬──────────────────────┘   │
│             │                       │                            │
│             ▼                       ▼                            │
│  ┌───────────────────┐   ┌────────────────────────┐            │
│  │    DynamoDB       │   │  Slack Notifications   │            │
│  │  Events Table     │   │  - Immediate alerts    │            │
│  │  (Config events)  │   │  - Daily summaries     │            │
│  └───────────────────┘   └────────────────────────┘            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │     API Gateway (Query Config Events)                    │   │
│  │  GET /events?source=aws.config                           │   │
│  │  GET /compliance/summary?account={id}                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

#### 1.2.1 Agent Stack Components (Monitored Accounts)
- **AWS Config**: Evaluates resources against Config rules
- **EventBridge Local Bus**: Captures Config events
- **Cross-Account Rule**: Forwards Config events to master account

**No additional Lambda functions required** - EventBridge handles routing

#### 1.2.2 Master Stack Components
- **EventBridge Custom Bus**: Receives all Config events
- **HandleMonitoringEvents Lambda**: Processes Config events (existing function, enhanced)
- **DynamoDB Events Table**: Stores compliance events (existing table)
- **ConfigEventNotifier**: Sends Slack notifications for violations (new)
- **API Gateway**: Query endpoints for compliance data (enhanced existing)
- **DailyReport Lambda**: Includes Config compliance summary (enhanced existing)

## 2. Data Model Design

### 2.1 Domain Models

#### 2.1.1 ConfigComplianceEvent (Domain Model)
Location: `src/domain/models/config.py`

```python
from pydantic import BaseModel, Field
from src.common.utils.datetime_utils import current_utc_timestamp

class ConfigComplianceEvent(BaseModel):
    """Domain model for AWS Config compliance events."""

    # Core identification
    config_rule_name: str
    config_rule_arn: str

    # Resource information
    resource_id: str
    resource_type: str  # e.g., "AWS::EC2::Instance"
    resource_arn: str | None = None

    # Compliance status
    old_compliance_status: str | None = None  # COMPLIANT, NON_COMPLIANT, NOT_APPLICABLE
    new_compliance_status: str

    # Evaluation details
    evaluation_timestamp: int
    result_recorded_time: int
    annotation: str | None = None  # Reason for non-compliance

    # Metadata
    account: str
    region: str
    message_type: str = "ComplianceChangeNotification"


class ConfigResourceChange(BaseModel):
    """Domain model for Config resource configuration changes."""

    resource_id: str
    resource_type: str
    change_type: str  # CREATE, UPDATE, DELETE
    configuration_item: dict  # Full Config item

    account: str
    region: str
    recorded_time: int
```

#### 2.1.2 Event Model Extension
Location: `src/domain/models/event.py`

**No changes required** - existing Event model already supports Config events through:
- `source: str` = "aws.config"
- `detail_type: str` = "Config Rules Compliance Change"
- `detail: dict` = Full Config event payload

### 2.2 Adapter Models

#### 2.2.1 ConfigEvent Data Class
Location: `src/adapters/aws/data_classes.py`

```python
from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent
from aws_lambda_powertools.utilities.data_classes.common import DictWrapper

class ConfigComplianceDetail(DictWrapper):
    """Adapter for AWS Config compliance event detail."""

    @property
    def config_rule_name(self) -> str:
        return self["configRuleName"]

    @property
    def config_rule_arn(self) -> str:
        return self["configRuleArn"]

    @property
    def resource_id(self) -> str:
        return self["resourceId"]

    @property
    def resource_type(self) -> str:
        return self["resourceType"]

    @property
    def new_compliance_status(self) -> str:
        return self["newEvaluationResult"]["complianceType"]

    @property
    def old_compliance_status(self) -> str | None:
        old = self.get("oldEvaluationResult")
        return old.get("complianceType") if old else None

    @property
    def annotation(self) -> str | None:
        return self["newEvaluationResult"].get("annotation")

    @property
    def evaluation_timestamp(self) -> str:
        return self["newEvaluationResult"]["evaluationResultIdentifier"]["orderingTimestamp"]

    @property
    def result_recorded_time(self) -> str:
        return self["newEvaluationResult"]["resultRecordedTime"]


class ConfigEvent(EventBridgeEvent):
    """AWS Config compliance change event."""

    @property
    def compliance_detail(self) -> ConfigComplianceDetail:
        return ConfigComplianceDetail(self["detail"])
```

### 2.3 DynamoDB Schema

**No schema changes required** - uses existing Events table:

```yaml
EventsTable:
  pk: "EVENT"
  sk: "EVENT#{timestamp}-{event_id}"

  # Config event example
  {
    "pk": "EVENT",
    "sk": "EVENT#1705324496-a1b2c3d4-5678-90ab-cdef",
    "account": "123456789012",
    "region": "us-east-1",
    "source": "aws.config",
    "detail_type": "Config Rules Compliance Change",
    "resources": ["arn:aws:ec2:us-east-1:123456789012:instance/i-abc123"],
    "detail": "{...full Config event JSON...}",
    "published_at": 1705324496,
    "updated_at": 1705324496,
    "expired_at": 1713100496  # 90 days TTL
  }
```

**Access Patterns**:
1. List all Config events: `pk=EVENT AND sk BETWEEN EVENT#start AND EVENT#end`
2. Filter by account: Add filter expression `account = :account_id`
3. Filter by source: Add filter expression `source = 'aws.config'`

### 2.4 Notification Payload

#### Slack Notification Format
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "⚠️ AWS Config Compliance Violation"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Account:*\n123456789012"
        },
        {
          "type": "mrkdwn",
          "text": "*Region:*\nus-east-1"
        },
        {
          "type": "mrkdwn",
          "text": "*Rule:*\nrequired-tags"
        },
        {
          "type": "mrkdwn",
          "text": "*Resource:*\ni-1234567890abcdef0"
        },
        {
          "type": "mrkdwn",
          "text": "*Status:*\n❌ NON_COMPLIANT"
        },
        {
          "type": "mrkdwn",
          "text": "*Reason:*\nResource is missing required tags: Environment, Owner"
        }
      ]
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "View in Console"
          },
          "url": "https://console.aws.amazon.com/config/..."
        }
      ]
    }
  ]
}
```

## 3. Component Design

### 3.1 Domain Layer Components

#### 3.1.1 Use Case: Process Config Compliance Event
Location: `src/domain/use_cases/process_config_event.py`

```python
from src.domain.models.config import ConfigComplianceEvent
from src.domain.models.event import Event
from src.domain.ports.repositories import IEventRepository
from src.domain.ports.notifier import IEventNotifier

def process_config_event_use_case(
    config_data: ConfigComplianceEvent,
    event_metadata: dict,  # account, region, time, resources
    event_repo: IEventRepository,
    notifier: IEventNotifier
) -> None:
    """Process AWS Config compliance event.

    1. Create domain Event from Config data
    2. Persist to repository
    3. Send notification if NON_COMPLIANT
    """

    # 1. Create domain event
    event = Event(
        id=event_metadata["event_id"],
        account=event_metadata["account"],
        region=event_metadata["region"],
        source="aws.config",
        detail_type="Config Rules Compliance Change",
        detail={
            "config_rule_name": config_data.config_rule_name,
            "resource_id": config_data.resource_id,
            "resource_type": config_data.resource_type,
            "old_status": config_data.old_compliance_status,
            "new_status": config_data.new_compliance_status,
            "annotation": config_data.annotation,
        },
        resources=event_metadata["resources"],
        published_at=config_data.evaluation_timestamp,
    )

    # 2. Persist event
    event_repo.create(event)

    # 3. Notify if violation
    if config_data.new_compliance_status == "NON_COMPLIANT":
        notifier.notify(event)
```

#### 3.1.2 Port: IConfigEventNotifier
Location: `src/domain/ports/notifier.py` (extend existing)

```python
from typing import Protocol
from src.domain.models.event import Event

class IConfigEventNotifier(Protocol):
    """Interface for Config compliance notifications."""

    def notify_compliance_violation(self, event: Event) -> None:
        """Send notification for compliance violation."""
        ...

    def notify_compliance_summary(self, summary: dict) -> None:
        """Send daily compliance summary."""
        ...
```

### 3.2 Adapter Layer Components

#### 3.2.1 ConfigEventNotifier
Location: `src/adapters/notifiers/config.py`

```python
from src.adapters.notifiers.base import SlackClient
from src.domain.models.event import Event
from src.common.utils.template import render_template

class ConfigEventNotifier:
    """Adapter for Config event notifications."""

    def __init__(self, client: SlackClient):
        self.client = client

    def notify_compliance_violation(self, event: Event) -> None:
        """Send Slack notification for compliance violation."""

        # Extract Config-specific data from event detail
        detail = event.detail

        # Render Slack message from template
        message = render_template(
            "config_violation.j2",
            account=event.account,
            region=event.region,
            rule_name=detail["config_rule_name"],
            resource_id=detail["resource_id"],
            resource_type=detail["resource_type"],
            status=detail["new_status"],
            reason=detail.get("annotation", "No reason provided"),
            console_url=self._build_console_url(event),
        )

        self.client.send(message)

    def _build_console_url(self, event: Event) -> str:
        """Build AWS Console URL for Config resource."""
        account = event.account
        region = event.region
        resource_id = event.detail["resource_id"]

        return f"https://console.aws.amazon.com/config/home?region={region}#/resources/timeline?resourceId={resource_id}&resourceType={event.detail['resource_type']}"
```

#### 3.2.2 Config Event Parser
Location: `src/adapters/aws/config_parser.py`

```python
from src.adapters.aws.data_classes import ConfigEvent
from src.domain.models.config import ConfigComplianceEvent
from src.common.utils.datetime_utils import datetime_str_to_timestamp

def parse_config_event(aws_event: ConfigEvent) -> tuple[ConfigComplianceEvent, dict]:
    """Parse AWS Config event to domain model.

    Returns:
        Tuple of (ConfigComplianceEvent, event_metadata)
    """
    detail = aws_event.compliance_detail

    config_data = ConfigComplianceEvent(
        config_rule_name=detail.config_rule_name,
        config_rule_arn=detail.config_rule_arn,
        resource_id=detail.resource_id,
        resource_type=detail.resource_type,
        old_compliance_status=detail.old_compliance_status,
        new_compliance_status=detail.new_compliance_status,
        evaluation_timestamp=datetime_str_to_timestamp(detail.evaluation_timestamp),
        result_recorded_time=datetime_str_to_timestamp(detail.result_recorded_time),
        annotation=detail.annotation,
        account=aws_event.account,
        region=aws_event.region,
    )

    event_metadata = {
        "event_id": aws_event.get_id,
        "account": aws_event.account,
        "region": aws_event.region,
        "resources": aws_event.resources,
    }

    return config_data, event_metadata
```

### 3.3 Entrypoint Layer Components

#### 3.3.1 Enhanced HandleMonitoringEvents Lambda
Location: `src/entrypoints/functions/handle_monitoring_events/main.py`

```python
from src.adapters.aws.data_classes import ConfigEvent, event_source
from src.adapters.aws.config_parser import parse_config_event
from src.adapters.db.repositories import EventRepository
from src.adapters.notifiers import ConfigEventNotifier, SlackClient
from src.common.constants import CONFIG_WEBHOOK_URL
from src.domain.use_cases.process_config_event import process_config_event_use_case

config_notifier = ConfigEventNotifier(client=SlackClient(CONFIG_WEBHOOK_URL))
event_repo = EventRepository()

@event_source(data_class=dict)
def handler(event, context):
    """Handle monitoring events including AWS Config."""

    source = event.get("source")

    if source == "aws.config":
        # Parse Config event
        config_event = ConfigEvent(event)
        config_data, event_metadata = parse_config_event(config_event)

        # Process via use case
        process_config_event_use_case(
            config_data=config_data,
            event_metadata=event_metadata,
            event_repo=event_repo,
            notifier=config_notifier
        )

    # ... existing handlers for other event types ...
```

### 3.4 API Gateway Endpoints

#### Enhanced Events API
Location: `src/entrypoints/apigw/events/main.py`

```python
@router.get("/compliance/summary")
def get_compliance_summary(
    account: str | None = None,
    region: str | None = None,
    start_date: int | None = None,
    end_date: int | None = None
) -> dict:
    """Get compliance summary for Config events.

    Returns:
        {
          "total_events": 150,
          "compliant": 120,
          "non_compliant": 30,
          "by_rule": {
            "required-tags": {"compliant": 50, "non_compliant": 10},
            ...
          },
          "by_resource_type": {
            "AWS::EC2::Instance": {"compliant": 30, "non_compliant": 5},
            ...
          }
        }
    """

    # Query Config events from repository
    events = event_repo.list(
        dto=ListEventsDTO(
            start_date=start_date,
            end_date=end_date
        )
    )

    # Filter for Config events and specified account/region
    config_events = [
        e for e in events.items
        if e.source == "aws.config"
        and (account is None or e.account == account)
        and (region is None or e.region == region)
    ]

    # Calculate summary statistics
    summary = calculate_compliance_summary(config_events)

    return summary
```

## 4. Infrastructure Configuration

### 4.1 Agent Stack EventBridge Configuration
Location: `infra/agent/resources/eventbridge.yml`

```yaml
Resources:
  ConfigComplianceRule:
    Type: AWS::Events::Rule
    Properties:
      Name: ${self:service}-${self:provider.stage}-config-compliance
      Description: Forward AWS Config compliance events to master account
      State: ENABLED
      EventPattern:
        source:
          - aws.config
        detail-type:
          - Config Rules Compliance Change
      Targets:
        - Arn: !Sub "arn:aws:events:${AWS::Region}:${self:custom.masterAccountId}:event-bus/monitoring-event-bus"
          RoleArn: !GetAtt EventBridgeCrossAccountRole.Arn
          Id: MasterAccountEventBus
```

### 4.2 Master Stack EventBridge Rule
Location: `infra/master/resources/eventbridge.yml`

```yaml
  ConfigEventsRule:
    Type: AWS::Events::Rule
    Properties:
      Name: ${self:service}-${self:provider.stage}-config-events
      Description: Process AWS Config compliance events
      State: ENABLED
      EventBusName: !Ref MonitoringEventBus
      EventPattern:
        source:
          - aws.config
        detail-type:
          - Config Rules Compliance Change
      Targets:
        - Arn: !GetAtt HandleMonitoringEventsLambda.Arn
          Id: HandleConfigEvents
          RetryPolicy:
            MaximumRetryAttempts: 2
            MaximumEventAge: 3600
          DeadLetterConfig:
            Arn: !GetAtt EventsDLQ.Arn
```

### 4.3 Lambda Environment Variables
Location: `infra/master/functions/handle_monitoring_events.yml`

```yaml
HandleMonitoringEvents:
  handler: src/entrypoints/functions/handle_monitoring_events/main.handler
  environment:
    EVENTS_TABLE: !Ref EventsTable
    ALARM_WEBHOOK_URL: ${ssm:/monitoring/${self:provider.stage}/alarm-webhook}
    HEALTH_WEBHOOK_URL: ${ssm:/monitoring/${self:provider.stage}/health-webhook}
    CONFIG_WEBHOOK_URL: ${ssm:/monitoring/${self:provider.stage}/config-webhook}  # NEW
    LOG_LEVEL: INFO
```

### 4.4 IAM Permissions

**Agent Stack** - No additional permissions needed (EventBridge handles cross-account)

**Master Stack**:
```yaml
  - Effect: Allow
    Action:
      - events:PutEvents
    Resource:
      - !GetAtt MonitoringEventBus.Arn
  - Effect: Allow
    Action:
      - dynamodb:PutItem
      - dynamodb:GetItem
      - dynamodb:Query
    Resource:
      - !GetAtt EventsTable.Arn
```

## 5. Notification Templates

### 5.1 Config Violation Template
Location: `statics/templates/config_violation.j2`

```jinja2
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "⚠️ AWS Config Compliance Violation"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Account:*\n{{ account }}"
        },
        {
          "type": "mrkdwn",
          "text": "*Region:*\n{{ region }}"
        },
        {
          "type": "mrkdwn",
          "text": "*Rule:*\n{{ rule_name }}"
        },
        {
          "type": "mrkdwn",
          "text": "*Resource:*\n{{ resource_id }}"
        },
        {
          "type": "mrkdwn",
          "text": "*Type:*\n{{ resource_type }}"
        },
        {
          "type": "mrkdwn",
          "text": "*Status:*\n❌ {{ status }}"
        }
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Reason:*\n```{{ reason }}```"
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "View in Console 🔗"
          },
          "url": "{{ console_url }}",
          "style": "danger"
        }
      ]
    }
  ]
}
```

### 5.2 Daily Compliance Report Template
Location: `statics/templates/config_daily_report.j2`

```jinja2
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "📊 Daily AWS Config Compliance Report"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Report Period:* {{ start_date }} to {{ end_date }}"
      }
    },
    {
      "type": "divider"
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Total Evaluations:*\n{{ total_evaluations }}"
        },
        {
          "type": "mrkdwn",
          "text": "*Compliance Score:*\n{{ compliance_percentage }}%"
        },
        {
          "type": "mrkdwn",
          "text": "*New Violations:*\n{{ new_violations }}"
        },
        {
          "type": "mrkdwn",
          "text": "*Resolved:*\n{{ resolved_violations }}"
        }
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Top Non-Compliant Rules:*\n{% for rule in top_rules %}• {{ rule.name }}: {{ rule.count }} violations\n{% endfor %}"
      }
    }
  ]
}
```

## 6. Testing Strategy

### 6.1 Unit Tests

**Test Coverage Targets**:
- Domain use cases: 100%
- Adapters: 90%
- Entrypoints: 85%

**Key Test Cases**:
```python
# tests/domain/use_cases/test_process_config_event.py
def test_process_compliant_event_no_notification():
    """Config compliant event should not trigger notification."""

def test_process_non_compliant_event_triggers_notification():
    """Config NON_COMPLIANT event should trigger Slack notification."""

def test_config_event_persisted_to_repository():
    """Config event should be stored in event repository."""

# tests/adapters/test_config_parser.py
def test_parse_config_compliance_change_event():
    """Parse AWS Config event to domain model."""

def test_parse_config_event_with_missing_fields():
    """Handle Config events with optional fields missing."""

# tests/adapters/notifiers/test_config_notifier.py
def test_slack_notification_format():
    """Verify Slack message format for Config violations."""

def test_notification_console_url_generation():
    """Verify AWS Console URL construction."""
```

### 6.2 Integration Tests

```python
# tests/integrations/test_config_event_flow.py
def test_end_to_end_config_event_processing():
    """Full flow: EventBridge → Lambda → DynamoDB → Slack."""

    # 1. Send Config event to EventBridge
    # 2. Lambda processes event
    # 3. Verify event in DynamoDB
    # 4. Verify Slack webhook called
```

### 6.3 Load Tests

**Scenarios**:
- Process 1000 Config events in 1 minute
- Query 10,000 Config events via API
- Generate daily report with 5000+ events

**Tools**: Locust, AWS Lambda stress testing

## 7. Deployment Strategy

### 7.1 Phased Rollout

**Phase 1: Single Account POC**
- Enable Config monitoring in 1 test account
- Validate event flow and notifications
- Duration: 1 week

**Phase 2: Pilot Accounts**
- Enable in 3-5 non-production accounts
- Monitor performance and costs
- Duration: 2 weeks

**Phase 3: Production Rollout**
- Gradual rollout to all accounts (10 accounts/week)
- Monitor error rates and DLQ
- Duration: 4-6 weeks

### 7.2 Deployment Steps

1. **Master Stack Update**:
   ```bash
   cd infra/master
   serverless deploy --stage production
   ```

2. **Agent Stack Update** (per account):
   ```bash
   cd infra/agent
   serverless deploy --stage production --param account=123456789012
   ```

3. **Verification**:
   - Send test Config event
   - Verify in DynamoDB
   - Check Slack notification

### 7.3 Rollback Plan

If issues detected:
1. Disable EventBridge rule in master stack
2. Events buffered in EventBridge (24-hour retention)
3. Fix issue and re-enable
4. Buffered events auto-processed

## 8. Monitoring & Observability

### 8.1 CloudWatch Metrics

**Custom Metrics**:
- `ConfigEventsProcessed` - Count of Config events processed
- `ConfigEventProcessingErrors` - Failed event processing
- `ComplianceViolationNotifications` - Notifications sent
- `ConfigEventLatency` - Processing time

**Alarms**:
- Error rate > 5% in 5 minutes
- DLQ message count > 10
- Lambda duration > 10 seconds (p99)

### 8.2 Logging

**Log Structure**:
```json
{
  "timestamp": "2025-01-15T12:34:56Z",
  "level": "INFO",
  "service": "monitoring",
  "function": "HandleMonitoringEvents",
  "event_type": "config_compliance",
  "account": "123456789012",
  "config_rule": "required-tags",
  "resource_id": "i-abc123",
  "compliance_status": "NON_COMPLIANT",
  "processing_time_ms": 245
}
```

### 8.3 Dashboards

**CloudWatch Dashboard Widgets**:
1. Config Events Timeline (last 24 hours)
2. Compliance Score by Account
3. Top Non-Compliant Rules
4. Event Processing Latency (p50, p95, p99)
5. Error Rate and DLQ Count

## 9. Security Considerations

### 9.1 Data Protection
- Config event details may contain sensitive resource configurations
- Mask sensitive fields in logs (resource names, IPs)
- DynamoDB encryption at rest enabled
- EventBridge events encrypted in transit

### 9.2 Access Control
- IAM least privilege for Lambda execution roles
- EventBridge resource-based policies for cross-account
- API Gateway authorization via IAM or Cognito
- Slack webhook URL stored in AWS Secrets Manager

### 9.3 Compliance
- Config events retained 90 days for audit
- All access logged to CloudTrail
- Compliance summary reports for SOC2/ISO audits

## 10. Cost Estimation

### 10.1 Per-Account Monthly Costs (Estimated)

**Assumptions**:
- 50 Config rules per account
- 1000 resource evaluations per day
- 100 compliance changes per day

**Cost Breakdown**:
- AWS Config evaluations: $0.003 per evaluation = $90/month
- EventBridge events: $0.000001 per event × 100 × 30 = $0.003/month
- Lambda invocations: $0.0000002 per invoke × 100 × 30 = $0.0006/month
- DynamoDB writes: $0.00000125 per write × 100 × 30 = $0.00375/month
- Data transfer: Negligible (same region)

**Total per account**: ~$90/month (AWS Config is primary cost)

**50 accounts**: ~$4,500/month

### 10.2 Cost Optimization Tips
- Use AWS Config organization-level aggregator (reduce per-account costs)
- Configure Config rules to evaluate only on changes (not periodic)
- Implement DynamoDB TTL to auto-delete old events
- Use S3 for long-term Config snapshot storage (cheaper than DynamoDB)

## 11. Future Enhancements

### 11.1 Phase 2 Features (Future)
- Automated remediation via Lambda for common violations
- Integration with AWS Systems Manager for patch compliance
- Custom Config rules via Lambda
- Compliance dashboard web UI
- Integration with ticketing systems (Jira, ServiceNow)

### 11.2 Phase 3 Features (Future)
- ML-based anomaly detection for config changes
- Predictive compliance scoring
- Cost optimization recommendations based on Config data
- Multi-cloud support (Azure Policy, GCP Security Command Center)

## 12. Appendix

### 12.1 AWS Config Event Examples

See full event examples in:
- `tests/data/config_compliance_change.json`
- `tests/data/config_configuration_change.json`

### 12.2 Glossary

- **AWS Config**: AWS service for resource configuration tracking and compliance
- **Config Rule**: Policy that defines desired resource configuration
- **Compliance Status**: COMPLIANT, NON_COMPLIANT, NOT_APPLICABLE, INSUFFICIENT_DATA
- **Configuration Item**: Snapshot of resource configuration at a point in time
- **Compliance Timeline**: History of compliance status changes for a resource

### 12.3 References

- [AWS Config Developer Guide](https://docs.aws.amazon.com/config/)
- [EventBridge Cross-Account Event Delivery](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-cross-account.html)
- [AWS Config Event Format](https://docs.aws.amazon.com/config/latest/developerguide/monitor-config-with-cloudwatchevents.html)
- Project hexagonal architecture patterns: `docs/project_structure.md`

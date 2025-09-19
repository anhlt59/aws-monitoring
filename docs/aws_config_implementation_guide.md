# AWS Config Monitoring - Implementation Guide

## Quick Start

This guide provides step-by-step instructions for implementing AWS Config monitoring based on the requirements and design specifications.

## Prerequisites

- [ ] AWS Config enabled in all monitored accounts
- [ ] At least one Config rule configured and evaluating
- [ ] Existing monitoring system deployed (master + agent stacks)
- [ ] Python 3.13+ with Poetry
- [ ] AWS CLI configured with appropriate credentials

## Implementation Phases

### Phase 1: Domain Layer (Pure Business Logic)

#### Step 1.1: Create Config Domain Models

```bash
# Create domain model file
touch src/domain/models/config.py
```

**Implementation**: Copy from `docs/aws_config_monitoring_design.md` Section 2.1.1

**Files to create**:
- `src/domain/models/config.py` - ConfigComplianceEvent, ConfigResourceChange

**Tests**:
```bash
poetry run pytest tests/domain/models/test_config.py -v
```

#### Step 1.2: Create Config Use Case

```bash
# Create use case file
touch src/domain/use_cases/process_config_event.py
```

**Implementation**: Copy from design document Section 3.1.1

**Files to create**:
- `src/domain/use_cases/process_config_event.py`

**Tests**:
```bash
poetry run pytest tests/domain/use_cases/test_process_config_event.py -v
```

**Expected test coverage**: 100% for use case

#### Step 1.3: Extend Domain Ports

```bash
# Edit existing file
vim src/domain/ports/notifier.py
```

**Changes**:
- Add `IConfigEventNotifier` protocol (Section 3.1.2)

### Phase 2: Adapter Layer (AWS Integration)

#### Step 2.1: Create Config Event Data Class

```bash
# Edit existing file
vim src/adapters/aws/data_classes.py
```

**Implementation**: Add ConfigEvent and ConfigComplianceDetail (Section 2.2.1)

**Tests**:
```bash
poetry run pytest tests/adapters/aws/test_config_data_classes.py -v
```

#### Step 2.2: Create Config Parser

```bash
# Create parser file
touch src/adapters/aws/config_parser.py
```

**Implementation**: Copy from Section 3.2.2

**Tests**:
```bash
poetry run pytest tests/adapters/test_config_parser.py -v
```

#### Step 2.3: Create Config Notifier

```bash
# Create notifier file
touch src/adapters/notifiers/config.py
```

**Implementation**: Copy from Section 3.2.1

**Files to create**:
- `src/adapters/notifiers/config.py`
- `statics/templates/config_violation.j2`
- `statics/templates/config_daily_report.j2`

**Tests**:
```bash
poetry run pytest tests/adapters/notifiers/test_config.py -v
```

### Phase 3: Entrypoint Layer (Lambda Handlers)

#### Step 3.1: Enhance HandleMonitoringEvents Lambda

```bash
# Edit existing Lambda handler
vim src/entrypoints/functions/handle_monitoring_events/main.py
```

**Changes**:
1. Import Config components
2. Add Config event handling branch
3. Call process_config_event_use_case

**Implementation**: Copy from Section 3.3.1

**Tests**:
```bash
poetry run pytest tests/integrations/functions/test_handle_monitoring_events.py::test_handle_config_event -v
```

#### Step 3.2: Add Config API Endpoints

```bash
# Edit existing API
vim src/entrypoints/apigw/events/main.py
```

**Changes**:
- Add `GET /compliance/summary` endpoint

**Implementation**: Copy from Section 3.4

**Tests**:
```bash
poetry run pytest tests/integrations/api/test_config_endpoints.py -v
```

### Phase 4: Infrastructure Configuration

#### Step 4.1: Update Agent Stack

```bash
cd infra/agent
```

**Files to modify**:
- `resources/eventbridge.yml` - Add ConfigComplianceRule

**Implementation**: Copy from Section 4.1

**Validate**:
```bash
serverless package --stage dev
```

#### Step 4.2: Update Master Stack

```bash
cd infra/master
```

**Files to modify**:
- `resources/eventbridge.yml` - Add ConfigEventsRule
- `functions/handle_monitoring_events.yml` - Add CONFIG_WEBHOOK_URL env var

**Implementation**: Copy from Sections 4.2 and 4.3

**Validate**:
```bash
serverless package --stage dev
```

#### Step 4.3: Add Slack Webhook to SSM

```bash
# Store Config webhook URL
aws ssm put-parameter \
  --name /monitoring/dev/config-webhook \
  --value "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  --type SecureString \
  --region us-east-1
```

### Phase 5: Testing

#### Step 5.1: Unit Tests

```bash
# Run all Config-related tests
poetry run pytest tests/ -k config -v --cov=src

# Verify coverage > 90%
poetry run pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

#### Step 5.2: Integration Tests

```bash
# Start LocalStack
make start

# Deploy to LocalStack
make deploy-local

# Run integration tests
poetry run pytest tests/integrations/ -v
```

#### Step 5.3: Manual Testing

**Test Config Event**:
```bash
# Send test Config event to EventBridge
aws events put-events \
  --entries file://tests/data/config_compliance_change.json \
  --endpoint-url http://localhost:4566
```

**Verify**:
1. Check Lambda logs: `aws logs tail /aws/lambda/monitoring-dev-handle-events --follow`
2. Query DynamoDB: `aws dynamodb scan --table-name EventsTable`
3. Check Slack notification received

### Phase 6: Deployment

#### Step 6.1: Deploy Master Stack

```bash
cd infra/master

# Deploy to dev environment
serverless deploy --stage dev

# Verify deployment
serverless info --stage dev
```

**Verify**:
- Lambda function updated
- EventBridge rule created
- Environment variables set

#### Step 6.2: Deploy Agent Stack (Per Account)

```bash
cd infra/agent

# Deploy to test account
serverless deploy --stage dev --param account=123456789012

# Verify EventBridge rule created
aws events list-rules --name-prefix monitoring-dev-config
```

#### Step 6.3: Smoke Test

**Send Test Event**:
```bash
# Trigger a Config rule evaluation
aws configservice start-config-rules-evaluation \
  --config-rule-names required-tags
```

**Verify**:
1. Wait 2-5 minutes for evaluation
2. Check Lambda logs for Config event processing
3. Verify event in DynamoDB
4. Check Slack notification received

### Phase 7: Monitoring Setup

#### Step 7.1: Create CloudWatch Dashboard

```bash
# Create dashboard from template
aws cloudwatch put-dashboard \
  --dashboard-name monitoring-config-compliance \
  --dashboard-body file://infra/master/dashboards/config_dashboard.json
```

#### Step 7.2: Configure Alarms

```bash
# Deploy CloudWatch alarms
cd infra/master
serverless deploy --stage dev --function handle-monitoring-events
```

**Alarms to create**:
- Config event processing errors > 5%
- DLQ messages > 10
- Lambda duration > 10s (p99)

#### Step 7.3: Enable Logging

**Verify log groups**:
```bash
aws logs describe-log-groups \
  --log-group-name-prefix /aws/lambda/monitoring-dev
```

**Set retention**:
```bash
aws logs put-retention-policy \
  --log-group-name /aws/lambda/monitoring-dev-handle-events \
  --retention-in-days 30
```

## Verification Checklist

### Development Environment
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Test coverage > 90%
- [ ] LocalStack deployment successful
- [ ] Manual smoke test successful

### Staging Environment
- [ ] Master stack deployed
- [ ] Agent stack deployed to test account
- [ ] Test Config event processed successfully
- [ ] Slack notification received
- [ ] API endpoint returns compliance data
- [ ] CloudWatch dashboard created
- [ ] Alarms configured and active

### Production Environment
- [ ] Master stack deployed
- [ ] Agent stacks deployed to all accounts (phased)
- [ ] Config events flowing correctly
- [ ] Notifications working
- [ ] API performance validated
- [ ] Daily reports generating
- [ ] Monitoring dashboards reviewed

## Troubleshooting

### Issue: No Config Events Received

**Diagnosis**:
```bash
# Check EventBridge rule in agent account
aws events list-rules --name-prefix monitoring

# Check EventBridge metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Events \
  --metric-name Invocations \
  --dimensions Name=RuleName,Value=monitoring-dev-config-compliance \
  --start-time 2025-01-15T00:00:00Z \
  --end-time 2025-01-15T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

**Solutions**:
1. Verify AWS Config is enabled and rules are evaluating
2. Check cross-account EventBridge permissions
3. Verify EventBridge rule target ARN correct

### Issue: Events Not Stored in DynamoDB

**Diagnosis**:
```bash
# Check Lambda execution errors
aws logs tail /aws/lambda/monitoring-dev-handle-events --since 1h

# Check Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=monitoring-dev-handle-events \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

**Solutions**:
1. Check Lambda IAM permissions for DynamoDB
2. Review Lambda logs for exceptions
3. Check DynamoDB table exists and is active

### Issue: No Slack Notifications

**Diagnosis**:
```bash
# Check webhook URL configured
aws ssm get-parameter --name /monitoring/dev/config-webhook --with-decryption

# Check Lambda logs for notification errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/monitoring-dev-handle-events \
  --filter-pattern "notification"
```

**Solutions**:
1. Verify Slack webhook URL is valid
2. Test webhook manually: `curl -X POST -d '{"text":"test"}' $WEBHOOK_URL`
3. Check network connectivity from Lambda

### Issue: High Lambda Duration

**Diagnosis**:
```bash
# Check Lambda duration metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=monitoring-dev-handle-events \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

**Solutions**:
1. Increase Lambda memory (improves CPU)
2. Optimize DynamoDB query patterns
3. Enable Lambda function caching for boto3 clients

## Performance Optimization

### DynamoDB Query Optimization

**Problem**: Slow Config event queries

**Solution**:
```python
# Add filter expression to reduce scanned items
events = event_repo.list(
    dto=ListEventsDTO(start_date=start, end_date=end),
    filter_expression="source = :source",
    expression_values={":source": "aws.config"}
)
```

### Lambda Cold Start Reduction

**Problem**: High Lambda cold start latency

**Solutions**:
1. Enable Provisioned Concurrency (1-2 instances)
2. Reduce Lambda package size (remove unused dependencies)
3. Use Lambda SnapStart (if supported in region)

### Notification Batching

**Problem**: Too many Slack notifications

**Solution**:
```python
# Batch non-critical violations
if config_data.new_compliance_status == "NON_COMPLIANT":
    if is_critical_rule(config_data.config_rule_name):
        notifier.notify_immediately(event)
    else:
        notifier.batch_for_daily_report(event)
```

## Rollback Procedure

### If Production Issues Detected

**Step 1: Disable EventBridge Rule**
```bash
aws events disable-rule \
  --name monitoring-prod-config-events \
  --region us-east-1
```

**Step 2: Investigate Issue**
- Check Lambda logs and errors
- Review DLQ messages
- Identify root cause

**Step 3: Fix and Redeploy**
```bash
# Fix issue in code
git commit -m "fix: Config event processing issue"

# Redeploy master stack
cd infra/master
serverless deploy --stage prod
```

**Step 4: Re-enable EventBridge Rule**
```bash
aws events enable-rule \
  --name monitoring-prod-config-events \
  --region us-east-1
```

**Step 5: Monitor Recovery**
- Check Lambda execution success rate
- Verify DLQ clears out
- Confirm notifications working

## Next Steps

After successful implementation:

1. **Enable in Additional Accounts**: Roll out to remaining AWS accounts (10/week)
2. **Create Runbook**: Document operational procedures for on-call team
3. **Set Up Dashboards**: Create Grafana/Datadog dashboards for visualization
4. **Tune Notifications**: Refine which rules trigger immediate vs batched alerts
5. **Document Patterns**: Share Config compliance patterns with team
6. **Plan Phase 2**: Evaluate automated remediation requirements

## Support & Resources

- **Design Documentation**: `docs/aws_config_monitoring_design.md`
- **Requirements**: `docs/aws_config_monitoring_requirements.md`
- **AWS Config Docs**: https://docs.aws.amazon.com/config/
- **EventBridge Cross-Account**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-cross-account.html
- **Project Architecture**: `docs/overview.md`

# AWS Config Integration Plan for Serverless Monitoring Application

## 1. Overview of AWS Config and its Monitoring Capabilities

AWS Config is a service that continuously monitors and records configuration changes of AWS resources, providing:

**Core Capabilities:**
- **Configuration Monitoring**: Tracks resource configuration changes in real-time
- **Compliance Assessment**: Evaluates resources against predefined or custom rules
- **Historical Tracking**: Maintains configuration history for audit trails
- **Multi-Account/Multi-Region Aggregation**: Centralizes data across AWS accounts and regions
- **Remediation**: Automated corrective actions for non-compliant resources

**2025 Enhanced Features:**
- **Proactive Compliance**: New feature for preventing non-compliant resource creation
- **Advanced Conformance Packs**: Standardized compliance frameworks (SOC, PCI, FedRAMP)
- **Improved Integration**: Better integration with Security Hub, Control Tower, and Audit Manager

## 2. Recommended Integration Approach

### Architecture Overview

Given your existing master/agent stack pattern, I recommend extending the architecture to include AWS Config capabilities while maintaining the serverless event-driven design:

```
Agent Accounts:
├── AWS Config (Configuration Recorder + Delivery Channel)
├── Config Rules (Compliance evaluation)
├── EventBridge Rules (Config events → Master account)
└── Existing Agent Stack (CloudWatch logs monitoring)

Master Account:
├── Config Aggregator (Multi-account data aggregation)
├── EventBridge Bus (Receives Config events from agents)
├── New Config Handler (Process Config events)
├── Enhanced DynamoDB Schema (Config compliance data)
└── Existing Master Stack (Event processing, notifications)
```

## 3. Required AWS Services and Their Roles

### Core Config Services:
1. **AWS Config** - Configuration recording and change tracking
2. **Config Rules** - Compliance evaluation (managed + custom Lambda rules)
3. **Config Aggregator** - Multi-account data aggregation
4. **Remediation Configurations** - Automated corrective actions

### Integration Services:
1. **EventBridge** - Cross-account event routing for Config events
2. **Lambda** - Custom Config rules and event processing
3. **Systems Manager** - Automated remediation actions
4. **SNS** - Config notifications and integration with existing alerting

### Key Limitation:
- **Config Aggregator does NOT directly emit EventBridge events**
- **Workaround**: Individual account Config services emit events that can be forwarded cross-account

## 4. Configuration Changes for Master/Agent Stacks

### Agent Stack Extensions (`infra/agent/`):

**New Resources Needed:**
```yaml
# infra/agent/resources/config.yml
ConfigServiceLinkedRole:
  Type: AWS::IAM::ServiceLinkedRole
  Properties:
    AWSServiceName: config.amazonaws.com

ConfigurationRecorder:
  Type: AWS::Config::ConfigurationRecorder
  Properties:
    Name: !Sub "${AWS::StackName}-ConfigRecorder"
    RoleARN: !Sub "arn:aws:iam::${AWS::AccountId}:role/aws-service-role/config.amazonaws.com/AWSServiceRoleForConfig"
    RecordingGroup:
      AllSupported: true
      IncludeGlobalResourceTypes: true

DeliveryChannel:
  Type: AWS::Config::DeliveryChannel
  Properties:
    Name: !Sub "${AWS::StackName}-DeliveryChannel"
    S3BucketName: !Ref ConfigBucket

ConfigBucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketName: !Sub "${AWS::StackName}-config-bucket-${AWS::AccountId}"

# Config Rules
SecurityGroupSSHRule:
  Type: AWS::Config::ConfigRule
  Properties:
    ConfigRuleName: security-group-ssh-check
    Source:
      Owner: AWS
      SourceIdentifier: INCOMING_SSH_DISABLED

# Cross-account EventBridge Rule for Config events
ConfigEventBridgeRule:
  Type: AWS::Events::Rule
  Properties:
    Name: "${self:service}-ConfigEventRule"
    EventPattern:
      source: ["aws.config"]
      detail-type: 
        - "Config Configuration Item Change"
        - "Config Rules Compliance Change"
    Targets:
      - Arn: "arn:aws:events:${self:custom.monitoringConfigs.MasterRegion}:${self:custom.monitoringConfigs.MasterAccountId}:event-bus/monitoring-master-${self:custom.monitoringConfigs.MasterStage}-MonitoringEventBus"
        Id: "ConfigEventForwarder"
        RoleArn: !GetAtt EventBridgeRole.Arn
```

**New Function:**
```yaml
# infra/agent/functions/ProcessConfigEvents.yml
function:
  handler: src.modules.agent.handlers.process_config_events.handler
  events:
    - eventBridge:
        eventBus: default
        pattern:
          source: ["aws.config"]
          detail-type:
            - "Config Configuration Item Change"
            - "Config Rules Compliance Change"
```

### Master Stack Extensions (`infra/master/`):

**Enhanced EventBridge Configuration:**
```yaml
# Update infra/master/resources/event_bridge.yml
MonitoringEventRule:
  Type: AWS::Events::Rule
  Properties:
    EventPattern: |
      {
        "source": [
          "aws.cloudwatch",
          "aws.guardduty", 
          "aws.health",
          "aws.config",
          "monitoring.agent.cloudwatch",
          "monitoring.agent.guardduty",
          "monitoring.agent.health",
          "monitoring.agent.logs",
          "monitoring.agent.config"
        ]
      }

# New Config Aggregator
ConfigAggregator:
  Type: AWS::Config::ConfigurationAggregator
  Properties:
    ConfigurationAggregatorName: !Sub "${AWS::StackName}-ConfigAggregator"
    OrganizationAggregationSource:
      AllAwsRegions: true
      RoleArn: !GetAtt ConfigAggregatorRole.Arn
```

**New Handler Function:**
```yaml
# infra/master/functions/HandleConfigEvents.yml
function:
  handler: src.modules.master.handlers.handle_config_events.handler
  events:
    - eventBridge:
        eventBus: !Ref MonitoringEventBus
        pattern:
          source: ["aws.config", "monitoring.agent.config"]
```

**Enhanced DynamoDB Schema:**
```yaml
# Add to infra/master/resources/dynamodb.yml
ConfigComplianceGSI:
  Type: AWS::DynamoDB::GlobalSecondaryIndex
  Properties:
    IndexName: ConfigCompliance-Index
    KeySchema:
      - AttributeName: compliance_status
        KeyType: HASH
      - AttributeName: resource_type
        KeyType: RANGE
    Projection:
      ProjectionType: ALL
```

## 5. Event Flow Design for Config Events

### Current Event Flow Enhancement:

```
Agent Account Config Events:
AWS Config → EventBridge (Default Bus) → Cross-Account Rule → Master EventBridge Bus

Master Account Processing:
Master EventBridge Bus → HandleConfigEvents Lambda → DynamoDB + Notifications

Data Aggregation:
Config Aggregator → API Queries → Daily Report Lambda
```

### Event Types to Handle:

1. **Configuration Item Changes**
   - Resource creation/modification/deletion
   - Configuration drift detection

2. **Compliance Changes**
   - Rule evaluation results
   - Compliance status changes

3. **Remediation Events**
   - Automated remediation execution
   - Remediation success/failure

## 6. Multi-Account Considerations

### Cross-Account EventBridge Setup:
```yaml
# Master account EventBridge policy update
MonitoringEventBus:
  Properties:
    Policy: |
      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Sid": "AllowAgentAccountsConfigEvents",
            "Effect": "Allow",
            "Principal": {
              "AWS": [
                "arn:aws:iam::AGENT-ACCOUNT-1:root",
                "arn:aws:iam::AGENT-ACCOUNT-2:root"
              ]
            },
            "Action": "events:PutEvents",
            "Resource": "*",
            "Condition": {
              "StringEquals": {
                "events:source": ["aws.config", "monitoring.agent.config"]
              }
            }
          }
        ]
      }
```

### Organizations Integration:
- Use AWS Organizations for Config Aggregator automatic account discovery
- Leverage Organization-wide Config Rules for standardized compliance
- Implement Config Conformance Packs at organization level

## 7. Implementation Phases/Roadmap

### Phase 1: Foundation (2-3 weeks)
1. **Extend Agent Stack**
   - Add Config service configuration
   - Implement basic Config rules
   - Set up cross-account EventBridge forwarding
   - Create `ProcessConfigEvents` handler

2. **Extend Master Stack**
   - Add Config Aggregator
   - Create `HandleConfigEvents` handler  
   - Enhance DynamoDB schema for compliance data
   - Update EventBridge rules

### Phase 2: Core Integration (2-3 weeks)
3. **Event Processing**
   - Implement Config event processing logic
   - Add compliance data storage
   - Integrate with existing notification system
   - Create Config-specific API endpoints

4. **Monitoring and Reporting**
   - Enhance daily reports with compliance data
   - Add Config dashboards
   - Implement compliance trending

### Phase 3: Advanced Features (3-4 weeks)
5. **Custom Rules and Remediation**
   - Implement custom Config rules
   - Add automated remediation actions
   - Create compliance workflows

6. **Multi-Account Management**
   - Implement organization-wide aggregation
   - Add cross-account compliance reporting
   - Create compliance management APIs

## 8. Potential Challenges and Mitigation Strategies

### Challenge 1: Config Aggregator EventBridge Limitation
**Issue**: Config Aggregator doesn't emit EventBridge events directly
**Mitigation**: 
- Use individual account Config events forwarded via cross-account EventBridge
- Implement periodic polling of Aggregator API for centralized reporting
- Consider Config API-based data synchronization

### Challenge 2: Cross-Account Event Costs
**Issue**: Cross-account EventBridge events incur charges
**Mitigation**:
- Implement event filtering to reduce volume
- Batch events where possible
- Monitor costs and optimize event patterns

### Challenge 3: Config Service Costs
**Issue**: Config charges per configuration item recorded
**Mitigation**:
- Selective resource recording based on criticality
- Use Config recording exclusions for non-critical resources
- Implement cost monitoring and alerts

### Challenge 4: Event Volume Management
**Issue**: High-frequency Config events may overwhelm processing
**Mitigation**:
- Implement SQS buffering for high-volume events
- Use Lambda reserved concurrency limits
- Add event sampling for non-critical changes

### Challenge 5: Compliance Data Storage
**Issue**: Large volume of compliance data in DynamoDB
**Mitigation**:
- Implement data lifecycle policies (TTL)
- Use DynamoDB on-demand billing for variable workloads
- Consider S3 archival for historical compliance data

## 9. Required Implementation Files

### New Handler Files:
- `src/modules/agent/handlers/process_config_events/handler.py`
- `src/modules/master/handlers/handle_config_events/handler.py`

### New Service Files:
- `src/modules/master/services/repositories/config_compliance.py`
- `src/infras/aws/config.py`

### New Model Files:
- `src/modules/master/models/config_item.py`
- `src/modules/master/models/compliance_result.py`

### Infrastructure Configuration Files:
- `infra/agent/resources/config.yml`
- `infra/agent/functions/ProcessConfigEvents.yml`
- `infra/master/functions/HandleConfigEvents.yml`

## 10. Enhanced Database Schema

### Events Table Extensions:
Add new fields to support Config events:

```python
# Additional fields for Config events
config_item_type: String      # Type of AWS resource (e.g., "AWS::EC2::Instance")
compliance_status: String     # "COMPLIANT", "NON_COMPLIANT", "NOT_APPLICABLE"
configuration_state: String   # "ResourceDiscovered", "ResourceDeleted", etc.
resource_id: String          # AWS resource ID
config_rule_name: String     # Name of the Config rule that triggered the event
```

### New Config Compliance Table:
```python
# ConfigCompliance Table Schema
pk: String                   # "CONFIG_COMPLIANCE"
sk: String                   # "ACCOUNT#{account}#RESOURCE#{resource_id}#RULE#{rule_name}"
account: String              # AWS Account ID
region: String              # AWS Region
resource_id: String         # AWS Resource ID
resource_type: String       # AWS Resource Type
config_rule_name: String    # Config Rule Name
compliance_status: String   # "COMPLIANT", "NON_COMPLIANT", "NOT_APPLICABLE"
last_evaluated: Integer     # Unix timestamp
compliance_details: String  # JSON with detailed compliance information
```

This integration plan maintains your existing serverless architecture patterns while adding comprehensive AWS Config monitoring capabilities. The phased approach allows for incremental implementation and testing, ensuring minimal disruption to your current monitoring system.
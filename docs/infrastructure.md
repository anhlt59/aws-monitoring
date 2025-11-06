# Infrastructure

This document provides an overview of the infrastructure for the AWS Monitoring project.

## Serverless Framework

The infrastructure for this project is managed using the [Serverless Framework](https://www.serverless.com/). The configuration is defined in the following files:

- `serverless.master.yml`: Defines the master stack, which is the central component of the monitoring system.
- `serverless.agent.yml`: Defines the agent stack, which is deployed to each AWS account that you want to monitor.

## Master Stack

The master stack consists of the following resources:

- **Lambda Functions:**
  - `HandleMonitoringEvents`: Handles monitoring events from the agent stacks.
  - `UpdateDeployment`: Updates the agent stacks with the latest configuration.
  - `DailyReport`: Generates a daily report of the monitoring system.
- **DynamoDB Table:** Stores the monitoring data.
- **EventBridge Bus:** Receives monitoring events from the agent stacks.
- **SQS Queue:** A dead-letter queue for the EventBridge bus.
- **IAM Roles and Policies:** Defines the permissions for the Lambda functions and other resources.
- **API Gateway**

  The following table lists the API endpoints that are exposed by the API Gateway:

  | Method | Path              | Description        | Function                                                                 |
  | ------ | ----------------- | ------------------ | ------------------------------------------------------------------------ |
  | GET    | /events           | List events        | [Master-ListEvents](../infra/functions/api/Event-ListItems.yml)   |
  | PUT    | /events/{eventId} | Update event by ID | [Master-UpdateEvent](../infra/functions/api/Event-UpdateItem.yml) |
  | GET    | /agents           | List agents        | [Master-ListAgents](../infra/functions/api/Agent-ListItems.yml)   |
  | GET    | /agents/{agentId} | Get agent by ID    | [Master-GetAgent](../infra/functions/api/Agent-GetItem.yml)       |
  | PUT    | /agents/{agentId} | Update agent by ID | [Master-UpdateAgent](../infra/functions/api/Agent-UpdateItem.yml) |

## Agent Stack

The agent stack consists of the following resources:

- **Lambda Function:**
  - `QueryErrorLogs`: Queries CloudWatch Logs for errors and sends them to the master stack.
- **EventBridge Rule:** Schedules the `QueryErrorLogs` Lambda function to run periodically.
- **SQS Queue:** A dead-letter queue for the EventBridge rule.
- **IAM Roles and Policies:** Defines the permissions for the Lambda function and other resources.

## Deployment

The infrastructure is deployed using the scripts in the `ops/deployment` folder. For more information, see the [deployment documentation](deployment.md).

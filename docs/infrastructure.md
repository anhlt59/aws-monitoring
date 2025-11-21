# Infrastructure

This document provides an overview of the infrastructure for the AWS Monitoring project.

## Serverless Framework

The infrastructure for this project is managed using the [Serverless Framework](https://www.serverless.com/). The
configuration is defined in the following files:

- `serverless.yml`: Defines the monitoring stack, which is deployed to your AWS account to monitor your resources.

## Monitoring Stack

The monitoring-stack consists of the following resources:

- **Lambda Functions:**
  - `HandleMonitoringEvents`: Handles monitoring events from the agent stacks.
  - `UpdateDeployment`: Updates the agent stacks with the latest configuration.
  - `DailyReport`: Generates a daily report of the monitoring system.
  - `QueryErrorLogs`: Queries CloudWatch Logs for errors and sends them to the master stack.
- **EventBridge Rule:** Schedules Lambda functions to run periodically.
- **DynamoDB Table:** Stores the monitoring data.
- **SQS Queue:** A dead-letter queue for the EventBridge rule.
- **IAM Roles and Policies:** Defines the permissions for the Lambda functions and other resources.
- **API Gateway**

  The following table lists the API endpoints that are exposed by the API Gateway:

  | Method | Path              | Description        | Function                                                                 |
  | ------ | ----------------- | ------------------ | ------------------------------------------------------------------------ |
  | GET    | /events           | List events        | [Master-ListEvents](../backend/infra/functions/api/Event-ListItems.yml)  |
  | PUT    | /events/{eventId} | Update event by ID | [Master-UpdateEvent](../backend/infra/functions/api/Event-UpdateItem.yml) |

## Deployment

The infrastructure is deployed using the scripts in the `ops/deployment` folder. For more information, see
the [deployment documentation](deployment.md).

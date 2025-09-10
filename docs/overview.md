# Project Overview

## Architecture

The AWS Monitoring project is a fully serverless application designed to monitor AWS resources and applications for performance, availability, and security issues.

![infra](images/infra.png)

### Components

- **Master Stack:** The master stack is the central component of the monitoring system. It is responsible for...
- **Agent Stack:** The agent stack is deployed to each AWS account that you want to monitor...

## Tech Stack

- **Backend:** Python, Serverless Framework
- **Database:** Amazon DynamoDB
- **Infrastructure:** AWS (Lambda, API Gateway, EventBridge, SNS, S3, CloudWatch)
- **Testing:** Pytest, Coverage
- **Local Development:** LocalStack, Docker

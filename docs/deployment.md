# Deployment Guide

This guide provides comprehensive instructions for deploying the AWS Monitoring project to various AWS environments
including production, staging, and multi-account setups.

## Prerequisites

Before you can deploy the project, you need to have the following prerequisites installed and configured:

### Software Requirements

| Tool                | Purpose                         | Installation                                                                                           |
|---------------------|---------------------------------|--------------------------------------------------------------------------------------------------------|
| **AWS CLI 2.x**     | AWS service interaction         | [AWS CLI Install Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) |
| **Docker**          | LocalStack and containerization | [Docker Install Guide](https://docs.docker.com/engine/install/)                                        |
| **Python 3.13+**    | Runtime environment             | [python.org](https://www.python.org/downloads/)                                                        |
| **Node.js 23.0.0+** | Serverless Framework            | [nodejs.org](https://nodejs.org/en/download/)                                                          |

## Pre-Deployment Setup

### 1. Bootstrap Infrastructure

Bootstrap creates the foundational AWS resources needed for deployment:

```bash
# Bootstrap NEOS environment (agent only)
make bootstrap-neos

# Bootstrap CM+ environment (master + staging agent)
make bootstrap-cm
```

The bootstrap process creates:

- **S3 Bucket:** An S3 bucket in the same region as your application to store the artifacts for your serverless
   application. For example, `neos-monitoring-deployment`. 
- **IAM Roles:** An IAM role that will be used to deploy the CloudFormation stack. The required permissions are
   defined in the `infra/roles/deployment_policy.json.tpl` file.

### 2. Environment-Specific Configuration

The project uses a two-stack approach for deployment:

- **Master Stack:** There is only one master stack (except for local development). The configuration files for the
  master stack are located in the `infra/master/configs` directory.
- **Agent Stack:** Each environment has its own agent stack. The configuration files for the agent stack are located in
  the `infra/agent/configs` directory.


## Deployment Process

To deploy the project, follow these steps:

Deploy to specific environments using make commands:

```bash
# Install dependencies first
make install
make activate

# Deploy to NEOS environment (agent stack only)
make deploy-neos

# Deploy to master environment
make deploy-master
```


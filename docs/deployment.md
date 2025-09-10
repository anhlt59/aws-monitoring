# Deployment Guide

This guide provides instructions for deploying the AWS Monitoring project to your AWS account.

## Prerequisites

Before you can deploy the project, you need to have the following prerequisites installed and configured:

- [Docker](https://docs.docker.com/engine/install/)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- An AWS account with the necessary permissions to create the required resources.

### AWS Resources

You need to set up the following prerequisite resources in AWS before deploying the application:

1.  **IAM Role:** Create an IAM role that will be used to deploy the CloudFormation stack. The required permissions are defined in the `infra/roles/deployment_policy.json.tpl` file.
2.  **S3 Bucket:** Create an S3 bucket in the same region as your application to store the artifacts for your serverless application. For example, `neos-monitoring-deployment`.

> You can use the `make bootstrap-${env}` command to create the necessary resources in your AWS account.

## Environment Configurations

The project uses a two-stack approach for deployment:

- **Master Stack:** There is only one master stack (except for local development). The configuration files for the master stack are located in the `infra/master/configs` directory.
- **Agent Stack:** Each environment has its own agent stack. The configuration files for the agent stack are located in the `infra/agent/configs` directory.

## Deployment Steps

To deploy the project, follow these steps:

1.  **Install dependencies:** Run `make install` to install all the required dependencies.
2.  **Activate the virtual environment:** Run `make activate` to activate the virtual environment.
3.  **Deploy the stacks:** Run `make deploy-${env}` to deploy the master and agent stacks to the specified environment. For example, to deploy to the `neos` environment, run `make deploy-neos`.

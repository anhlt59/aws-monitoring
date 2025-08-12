# Prerequisite Resources

Before deploying, you need to set up the following prerequisite resources in AWS.

1. IAM

    **Create an IAM role/policy**: that will be used to deploy the cloudformation stack.
     - [deployment_policy](../infra/roles/deployment_policy.json)

2. S3

    **Create an S3 Bucket**:
    Create an S3 bucket in the same region as your application to store the artifacts for your serverless application.
    For example `neos-monitoring-deployment`.

> Use  `make bootstrap-${env}` to create the necessary resources in your AWS account.

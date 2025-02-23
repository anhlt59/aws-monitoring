# Prerequisite Resources

<!-- TOC -->

* [Prerequisite Resources](#prerequisite-resources)
    * [IAM](#iam)
    * [S3](#s3)
    * [IoT](#iot)
    * [SecretsManager](#secretsmanager)

<!-- TOC -->

## IAM

- **Create an IAM role/user**: that will be used to deploy the cloudformation stack.

  - [deployment_policies](../serverless/resources/deployment_policies.json)

## S3

- **Create an S3 Bucket**:
  Create an S3 bucket in the same region as your application to store the artifacts for your serverless application. For
  example `denaribots-dev-deployment`.

## IoT

- **Create an IoT Thing**:
  [Create an IoT thing](https://ap-southeast-1.console.aws.amazon.com/iot/home?region=ap-southeast-1#/thinghub)
  as required for your application.

## SecretsManager

- To store your secret keys securely in the AWS Secrets Manager, create a secret key with name denaribots/SecretKeys
  contains these things:

```json
{
  "DB_HOST": "...",
  "DB_PASSWORD": "...",
  "DB_DATABASE": "...",
  "DB_USERNAME": "...",
  "MAIL_USERNAME": "...",
  "MAIL_PASSWORD": "...",
  "MAIL_HOST": "...",
  "DEFAULT_CMS_ADMIN_EMAIL": "...",
  "DEFAULT_CMS_ADMIN_PASSWORD": "...",
  "FIREBASE_CREDENTIALS": "...",
  "SES_ACCESS_KEY_ID": "...",
  "SES_SECRET_ACCESS_KEY": "...",
  "SORACOM_ENDPOINT": "...",
  "SORACOM_AUTH_KEY_ID": "...",
  "SORACOM_AUTH_KEY_SECRET": "...",
  "DEFAULT_ADMIN_EMAIL": "...",
  "DEFAULT_ADMIN_PASSWORD": "..."
}
```

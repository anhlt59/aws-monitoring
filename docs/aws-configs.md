## Environment Configurations

The `serverless/configs` folder contains a list of serverless configuration files for different environments.

* Configuration for Different Environments
    - [local.yml](../serverless/configs/local.yml)
    - [dev.yml](../serverless/configs/dev.yml)
    - [stg.yml](../serverless/configs/stg.yml)
    - [prod.yml](../serverless/configs/prod.yml)

### Update Configuration

You can customize the configuration settings in these files based on your requirements. Here's an example of how to update the configuration in the YAML file:

```yaml
# AWS Services
S3:
  DeploymentBucket:
    # Add the name of the S3 bucket created in the Prerequisite step
    name: denaribots-dev-deployment

Lambda:
  # Adjust the `logRetentionInDays` duration. Logs will expire after this number of days.
  logRetentionInDays: 7

DynamoDB:
  BillingMode: PROVISIONED # Allowed values: PAY_PER_REQUEST | PROVISIONED

  # Only for PROVISIONED mode
  RCU: 10
  WCU: 10
  AutoScale:
    Enable: true
    RCU:
      min: 10
      max: 20
    WCU:
      min: 10
      max: 20
    TargetUtilization: 70 # Scale when CPU utilization reaches 70%

VPC:
  PrivateSubnetIds:
    # List of private subnets that can connect to the RDS instance and access the internet
    - subnet-08cc5d69be197b5f4
    - subnet-0c3f5696d7541b437
    - subnet-0a552e89af58fdfd0
  SecurityGroupIds:
    - sg-0fa7d84572f03fae3

SES:
  Sender: DENARI BOTS <no-reply@denaribots.app>
  Region: ap-northeast-1

IOTCore:
  # Configure the IoT Core endpoint
  Host: a2dbnw0qcofuo1-ats.iot.ap-southeast-1.amazonaws.com

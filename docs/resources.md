## AWS resources

<!-- TOC -->

* [AWS resources](#aws-resources)
    * [IAM](#iam)
    * [DynamoDB](#dynamodb)
    * [SQS](#sqs)
    * [IOT Core](#iot-core)

<!-- TOC -->

Folder `serverless/resources` contains a list of template files.\
A template file contains resource templates.

### [IAM](serverless/resources/iam.yml)

| Name                 | Type                    | Description |
|----------------------|-------------------------|-------------|
| LambdaFunctionRole   | AWS::IAM::Role          |             |
| IOTCoreRole          | AWS::IAM::Role          |             |
| LambdaFunctionPolicy | AWS::IAM::ManagedPolicy |             |
| IOTCorePolicy        | AWS::IAM::ManagedPolicy |             |
| SoracomPolicy        | AWS::IAM::ManagedPolicy |             |

### [DynamoDB](serverless/resources/dynamodb.yml)

| Name                        | Type                                        | Description |
|-----------------------------|---------------------------------------------|-------------|
| DynamoDBTable               | AWS::DynamoDB::Table                        |             |
| ScalingRole                 | AWS::IAM::Role                              |             |
| WriteScalingPolicy          | AWS::ApplicationAutoScaling::ScalingPolicy  |             |
| ReadScalingPolicy           | AWS::ApplicationAutoScaling::ScalingPolicy  |             |
| WriteCapacityScalableTarget | AWS::ApplicationAutoScaling::ScalableTarget |             |
| ReadCapacityScalableTarget  | AWS::ApplicationAutoScaling::ScalableTarget |             |

### [SQS](serverless/resources/sqs.yml)

| Name                | Type                  | Description |
|---------------------|-----------------------|-------------|
| IOTStreamQueue      | AWS::SQS::Queue       |             |
| IOTStreamDLQ        | AWS::SQS::Queue       |             |
| MonitorCase123Queue | AWS::SQS::Queue       |             |
| MonitorCase4Queue   | AWS::SQS::Queue       |             |
| MonitorCase5Queue   | AWS::SQS::Queue       |             |
| MonitorCase6Queue   | AWS::SQS::Queue       |             |
| MonitorCase7Queue   | AWS::SQS::Queue       |             |
| MonitorDLQ          | AWS::SQS::Queue       |             |
| NotificationQueue   | AWS::SQS::Queue       |             |
| NotificationDLQ     | AWS::SQS::Queue       |             |
| DynamoStreamDLQ     | AWS::SQS::Queue       |             |
| IOTCoreQueuePolicy  | AWS::SQS::QueuePolicy |             |
| LambdaQueuePolicy   | AWS::SQS::QueuePolicy |             |
| SNSQueuePolicy      | AWS::SQS::QueuePolicy | Deprecated  |

### [IOT Core](serverless/resources/iot_core.yml)

| Name      | Type                   | Description |
|-----------|------------------------|-------------|
| IoTThing  | AWS::IoT::Thing        | Deprecated  |
| IoTRule0  | AWS::IoT::TopicRule    |             |
| IoTRule1  | AWS::IoT::TopicRule    |             |
| IoTLogs   | AWS::IoT::Logging      |             |

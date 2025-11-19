{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CloudFormationLimitedAccess",
      "Effect": "Allow",
      "Action": "cloudformation:*",
      "Resource": [
        "arn:aws:cloudformation:${AWS_REGION}:${AWS_ACCOUNT_ID}:stack/monitoring-*/*"
      ]
    },
    {
      "Sid": "IAMRoleManagement",
      "Effect": "Allow",
      "Action": [
        "iam:Get*",
        "iam:List*",
        "iam:PassRole",
        "iam:CreateRole",
        "iam:CreatePolicy",
        "iam:CreatePolicyVersion",
        "iam:AttachRolePolicy",
        "iam:UpdateRole",
        "iam:UpdateRoleDescription",
        "iam:UpdateAssumeRolePolicy",
        "iam:PutGroupPolicy",
        "iam:PutRolePolicy",
        "iam:DetachRolePolicy",
        "iam:DeleteRole",
        "iam:DeletePolicy",
        "iam:DeletePolicyVersion",
        "iam:Tag*",
        "iam:Untag*"
      ],
      "Resource": [
        "arn:aws:iam::*:role/monitoring*",
        "arn:aws:iam::*:policy/monitoring*"
      ]
    },
    {
      "Sid": "EventBridgeLimitedAccess",
      "Effect": "Allow",
      "Action": [
        "events:List*",
        "events:Describe*",
        "events:CreateEventBus",
        "events:PutRule",
        "events:PutPermission",
        "events:UpdateEventBus",
        "events:DeleteRule",
        "events:EnableRule",
        "events:DisableRule",
        "events:PutTargets",
        "events:RemoveTargets",
        "events:DeleteEventBus",
        "events:TagResource",
        "events:UntagResource"
      ],
      "Resource": [
        "arn:aws:events:${AWS_REGION}:${AWS_ACCOUNT_ID}:rule/monitoring*",
        "arn:aws:events:${AWS_REGION}:${AWS_ACCOUNT_ID}:event-bus/monitoring*"
      ]
    },
    {
      "Sid": "CloudWatchLogsLimitedAccess",
      "Effect": "Allow",
      "Action": [
        "logs:Get*",
        "logs:List*",
        "logs:Describe*",
        "logs:Create*",
        "logs:Put*",
        "logs:DeleteLogGroup",
        "logs:DeleteLogStream",
        "logs:Tag*",
        "logs:Untag*"
      ],
      "Resource": [
        "arn:aws:logs:${AWS_REGION}:${AWS_ACCOUNT_ID}:log-group:/aws/lambda/monitoring*",
        "arn:aws:logs:${AWS_REGION}:${AWS_ACCOUNT_ID}:log-group:/aws/lambda/monitoring*:*"
      ]
    },
    {
      "Sid": "S3BucketManagement",
      "Effect": "Allow",
      "Action": [
        "s3:Get*",
        "s3:List*",
        "s3:Describe*",
        "s3:CreateBucket",
        "s3:PutBucketAcl",
        "s3:PutBucketPolicy",
        "s3:PutEncryptionConfiguration",
        "s3:GetBucketLocation",
        "s3:TagResource",
        "s3:UntagResource"
      ],
      "Resource": ["arn:aws:s3:::monitoring*"]
    },
    {
      "Sid": "LambdaFunctionReadOnly",
      "Effect": "Allow",
      "Action": ["lambda:List*", "lambda:Get*"],
      "Resource": [
        "arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:function:*",
        "arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:layer:*"
      ]
    },
    {
      "Sid": "LambdaFunctionManagement",
      "Effect": "Allow",
      "Action": [
        "lambda:Create*",
        "lambda:Update*",
        "lambda:Put*",
        "lambda:Publish*",
        "lambda:Add*",
        "lambda:DeleteFunction",
        "lambda:DeleteAlias",
        "lambda:DeleteEventSourceMapping",
        "lambda:DeleteLayerVersion",
        "lambda:RemoveLayerVersionPermission",
        "lambda:RemovePermission",
        "lambda:TagResource",
        "lambda:UntagResource"
      ],
      "Resource": [
        "arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:function:monitoring*",
        "arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:layer:monitoring*"
      ]
    },
   {
      "Sid": "SQSQueueManagement",
      "Effect": "Allow",
      "Action": [
        "sqs:Get*",
        "sqs:List*",
        "sqs:CreateQueue",
        "sqs:DeleteQueue",
        "sqs:SetQueueAttributes",
        "sqs:Tag*",
        "sqs:Untag*"
      ],
      "Resource": "arn:aws:sqs:${AWS_REGION}:${AWS_ACCOUNT_ID}:monitoring*"
    },
   {
      "Sid": "AllowPublishSNSMessages",
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:*:*:monitoring*"
    },
    {
      "Sid": "DynamoDBReadOnlyAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:List*",
        "dynamodb:Describe*",
        "dynamodb:Get*"
      ],
      "Resource": "arn:aws:dynamodb:${AWS_REGION}:${AWS_ACCOUNT_ID}:table/*"
    },
    {
      "Sid": "DynamoDBLimitedAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:CreateTable",
        "dynamodb:UpdateTable",
        "dynamodb:DeleteTable",
        "dynamodb:TagResource",
        "dynamodb:UntagResource",
        "dynamodb:UpdateTimeToLive",
        "dynamodb:UpdateContinuousBackups"
      ],
      "Resource": "arn:aws:dynamodb:${AWS_REGION}:${AWS_ACCOUNT_ID}:table/monitoring*"
    }
  ]
}

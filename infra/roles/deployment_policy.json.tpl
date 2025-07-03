{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "cloudformation:*",
      "Resource": [
        "arn:aws:cloudformation:${AWS_REGION}:${AWS_ACCOUNT_ID}:stack/teligent-agent/*"
      ],
      "Effect": "Allow",
      "Sid": "CloudFormationLimitedAccess"
    },
    {
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
        "arn:aws:iam::*:role/teligent*",
        "arn:aws:iam::*:policy/teligent*"
      ],
      "Effect": "Allow",
      "Sid": "IAMRoleManagement"
    },
    {
      "Action": [
        "events:List*",
        "events:Describe*",
        "events:CreateEventBus",
        "events:PutRule",
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
        "arn:aws:events:${AWS_REGION}:${AWS_ACCOUNT_ID}:rule/teligent*",
        "arn:aws:events:${AWS_REGION}:${AWS_ACCOUNT_ID}:event-bus/teligent*"
      ],
      "Effect": "Allow",
      "Sid": "EventBridgeLimitedAccess"
    },
    {
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
        "arn:aws:logs:${AWS_REGION}:${AWS_ACCOUNT_ID}:log-group:/aws/lambda/teligent*:*"
      ],
      "Effect": "Allow",
      "Sid": "CloudWatchLogsLimitedAccess"
    },
    {
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
      "Resource": ["arn:aws:s3:::teligent*"],
      "Effect": "Allow",
      "Sid": "S3BucketManagement"
    },
    {
      "Action": ["lambda:List*", "lambda:Get*"],
      "Resource": [
        "arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:function:*",
        "arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:layer:*"
      ],
      "Effect": "Allow",
      "Sid": "LambdaFunctionReadOnly"
    },
    {
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
        "arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:function:teligent*",
        "arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:layer:teligent*"
      ],
      "Effect": "Allow",
      "Sid": "LambdaFunctionManagement"
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
      "Resource": "arn:aws:sqs:${AWS_REGION}:${AWS_ACCOUNT_ID}:teligent*"
    }
  ]
}

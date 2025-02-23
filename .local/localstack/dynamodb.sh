#!/usr/bin/env bash

set -euo pipefail

echo "configuring dynamodb table"
echo "==================="

AWS_REGION=us-east-1

# https://docs.aws.amazon.com/cli/latest/reference/dynamodb/create-table.html
awslocal dynamodb create-table \
  --table-name denaribots-local \
  --billing-mode PAY_PER_REQUEST \
  --key-schema AttributeName=IMEI,KeyType=HASH AttributeName=sensor_time,KeyType=RANGE \
  --attribute-definitions AttributeName=IMEI,AttributeType=S AttributeName=sensor_time,AttributeType=S \
  --region "$AWS_REGION"
#  --stream-specification StreamEnabled=true,StreamViewType=NEW_IMAGE

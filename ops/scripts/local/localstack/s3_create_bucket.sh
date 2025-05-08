#!/usr/bin/env bash

set -euo pipefail

# enable debug
# set -x

echo "configuring s3"
echo "==================="
AWS_REGION=us-east-1

# https://docs.aws.amazon.com/cli/latest/reference/s3/mb.html
create_bucket() {
  local NAME=$1
  awslocal s3 mb "s3://${NAME}" --region "$AWS_REGION"
}

# https://docs.aws.amazon.com/cli/latest/reference/s3/cp.html
put_object() {
  local BUCKET_NAME=$1
  local FILE_PATH=$2
  local S3_OBJECT_KEY=$3
  awslocal s3 cp "$FILE_PATH" "s3://${BUCKET_NAME}/${S3_OBJECT_KEY}" --region "$AWS_REGION"
}

create_bucket teligent-local
create_bucket teligent-local-deployment

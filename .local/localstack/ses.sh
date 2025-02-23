#!/usr/bin/env bash

set -euo pipefail

echo "configuring ses email identity"
echo "==================="

AWS_REGION=us-east-1

# https://docs.localstack.cloud/user-guide/aws/ses/

#awslocal ses verify-email-identity \
#  --email no-reply@denaribots.app \
#  --region "$AWS_REGION"

awslocal ses verify-domain-identity \
  --domain denaribots.app \
  --region "$AWS_REGION"

awslocal ses list-identities

#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "$0")")" && pwd)
source "${SCRIPT_DIR}/base.sh"
STAGE="${1:-neos}"

if [[ "$STAGE" == "local" ]]; then
  echo -e "${RED}Warning: 'local' stage is not supported.${RESET}"
  exit 1
fi

CONFIG_FILE="${BASE_DIR}/infra/agent/configs/${STAGE}.yml"
AWS_DEFAULT_REGION="$(yq e '.Region' "$CONFIG_FILE")"
AWS_PROFILE="$(yq e '.Profile' "$CONFIG_FILE")"
export AWS_DEFAULT_REGION
export AWS_PROFILE

# Read S3 deployment bucket name from CONFIG_FILE using yq
# Then check if the S3 deployment bucket exists, create if not
DEPLOYMENT_BUCKET=$(yq e '.S3.DeploymentBucket.name' "$CONFIG_FILE")
if aws s3api head-bucket --bucket "$DEPLOYMENT_BUCKET" 2>/dev/null; then
  echo -e "${GREEN}S3 bucket '$DEPLOYMENT_BUCKET' already exists.${RESET}"
else
  echo -e "${YELLOW}S3 bucket '$DEPLOYMENT_BUCKET' does not exist. Creating...${RESET}"
  aws s3api create-bucket --bucket "$DEPLOYMENT_BUCKET"
  echo -e "${GREEN}S3 bucket '$DEPLOYMENT_BUCKET' created.${RESET}"
fi

# Create or update IAM role & policy for deployment
ROLE_NAME="teligent-DeploymentRole"
POLICY_NAME="teligent-DeploymentPolicy"

# Search for the policy by name
POLICY_ARN=$(aws iam list-policies --scope Local --query "Policies[?PolicyName=='$POLICY_NAME'].Arn" --output text)
# Create IAM policy, if the policy doesn't exist
if [[ -n "$POLICY_ARN" ]]; then
  echo -e "${GREEN}IAM policy '$POLICY_NAME' already exists.${RESET}"
  echo -e "${YELLOW}Updating IAM policy '$POLICY_NAME'...${RESET}"
  aws iam create-policy-version \
    --policy-arn "$POLICY_ARN" \
    --policy-document "file://${BASE_DIR}/infra/roles/deployment_policy.json" \
    --set-as-default
  echo -e "${GREEN}IAM policy '$POLICY_NAME' updated with new default version.${RESET}"
else
  echo -e "${YELLOW}Creating IAM policy '$POLICY_NAME'...${RESET}"
  aws iam create-policy \
    --policy-name "$POLICY_NAME" \
    --policy-document "file://${BASE_DIR}/infra/roles/deployment_policy.json"
  echo -e "${GREEN}IAM policy '$POLICY_NAME' created.${RESET}"
fi

# Create IAM role, if the role doesn't exist
if aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
  echo -e "${GREEN}IAM role '$ROLE_NAME' already exists.${RESET}"
else
  echo -e "${YELLOW}Creating IAM role '$ROLE_NAME'...${RESET}"
  echo "Creating IAM role: ${ROLE_NAME}"
  aws iam create-role \
    --role-name "$ROLE_NAME" \
    --assume-role-policy-document "file://$BASE_DIR/infra/roles/trust_policy.json" \
    --description "Service role for AWS CloudFormation"
  echo "Attaching policy '$POLICY_NAME' to role '$ROLE_NAME'"
  aws iam attach-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-arn "$POLICY_ARN"
  echo -e "${GREEN}IAM role '$ROLE_NAME' created and policy '$POLICY_NAME' attached."
fi

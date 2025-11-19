#!/usr/bin/env bash
# ==================================================================================
# This script is designed to automate the setup of S3 buckets and IAM roles/policies
#   for a given deployment stage.
#
# Usage:
#   $ bootstrap.sh [stage]
# Arguments:
#   - stage: The deployment stage (e.g., 'local')
# ==================================================================================

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "$0")")" && pwd)
source "${SCRIPT_DIR}/base.sh"
STAGE="${1:-local}"

if [[ "$STAGE" == "local" ]]; then
    echo -e "${RED}Warning: 'local' stage is not supported.${RESET}"
    exit 1
fi

echo -e "${BLUE}===============================${RESET}"
echo -e "${BLUE}Bootstrap 'monitoring'${RESET}"
echo -e "${BLUE}* Stage        ${STAGE}${RESET}"
echo -e "${BLUE}* AWS profile  ${AWS_PROFILE}${RESET}"
echo -e "${BLUE}* AWS region   ${AWS_DEFAULT_REGION}${RESET}${RESET}"
echo -e "${BLUE}===============================${RESET}\n"

# Create folder .serverless in current directory
DEPLOYMENT_DIR="${BACKEND_DIR}/.serverless"
mkdir -p "$DEPLOYMENT_DIR"

# Copy the config file
CONFIG_FILE="${DEPLOYMENT_DIR}/config.yml"
cp "${BACKEND_DIR}/infra/configs/${STAGE}.yml" "$CONFIG_FILE"
cp -r "${BACKEND_DIR}/infra/roles/" "$DEPLOYMENT_DIR"
AWS_DEFAULT_REGION="$(yq e '.Region' "$CONFIG_FILE")"
AWS_PROFILE="$(yq e '.Profile' "$CONFIG_FILE")"
export AWS_DEFAULT_REGION
export AWS_PROFILE

# IAM POLICY -----------------------------------------------------------------------------------------------------------
echo -e "${GREEN}\nBootstrapping IAM Role & Policy...${RESET}"
ROLE_NAME="monitoring-DeploymentRole"
POLICY_NAME="monitoring-DeploymentPolicy"

# Generate deployment policy file
sed -e "s|\${AWS_REGION}|$AWS_DEFAULT_REGION|g" \
    -e "s|\${AWS_ACCOUNT_ID}|$(aws sts get-caller-identity --query Account --output text)|g" \
    "${DEPLOYMENT_DIR}/deployment_policy.json.tpl" >"${DEPLOYMENT_DIR}/deployment_policy.json"
echo -e "${GREEN}Generated deployment policy at '${DEPLOYMENT_DIR}/deployment_policy.json'.${RESET}"

# Create or update IAM role & policy for deployment
# Search for the policy by name
POLICY_ARN=$(aws iam list-policies --scope Local --query "Policies[?PolicyName=='$POLICY_NAME'].Arn" --output text)
# Create IAM policy, if the policy doesn't exist
if [[ -n "$POLICY_ARN" ]]; then
    echo -e "${GREEN}IAM policy '$POLICY_NAME' already exists.${RESET}"
    echo -e "${YELLOW}Updating IAM policy '$POLICY_NAME'...${RESET}"
    # List all policy versions
    POLICY_VERSIONS=$(aws iam list-policy-versions --policy-arn "$POLICY_ARN" --query 'Versions' --output json)
    VERSION_COUNT=$(echo "$POLICY_VERSIONS" | jq 'length')

    if [[ "$VERSION_COUNT" -ge 5 ]]; then
        # Find the oldest non-default version
        OLDEST_VERSION=$(echo "$POLICY_VERSIONS" | jq -r '[.[] | select(.IsDefaultVersion==false)] | sort_by(.CreateDate) | .[0].VersionId')
        if [[ -n "$OLDEST_VERSION" ]]; then
            echo -e "${ORANGE}Deleting oldest policy version: $OLDEST_VERSION${RESET}"
            aws iam delete-policy-version --policy-arn "$POLICY_ARN" --version-id "$OLDEST_VERSION"
        fi
    fi
    aws iam create-policy-version \
        --policy-arn "$POLICY_ARN" \
        --policy-document "file://${DEPLOYMENT_DIR}/deployment_policy.json" \
        --set-as-default
    echo -e "${GREEN}IAM policy '$POLICY_NAME' updated with new default version.${RESET}"
else
    echo -e "${YELLOW}Creating IAM policy '$POLICY_NAME'...${RESET}"
    aws iam create-policy \
        --policy-name "$POLICY_NAME" \
        --policy-document "file://${DEPLOYMENT_DIR}/deployment_policy.json"
    echo -e "${GREEN}IAM policy '$POLICY_NAME' created.${RESET}"
fi

# IAM ROLE -------------------------------------------------------------------------------------------------------------
# Create IAM role, if the role doesn't exist
if aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
    echo -e "${GREEN}IAM role '$ROLE_NAME' already exists.${RESET}"
else
    echo -e "${YELLOW}Creating IAM role '$ROLE_NAME'...${RESET}"
    echo "Creating IAM role: ${ROLE_NAME}"
    aws iam create-role \
        --role-name "$ROLE_NAME" \
        --assume-role-policy-document "file://${DEPLOYMENT_DIR}/trust_policy.json" \
        --description "Service role for AWS CloudFormation"
    echo "Attaching policy '$POLICY_NAME' to role '$ROLE_NAME'"
    aws iam attach-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-arn "$(aws iam list-policies --scope Local --query "Policies[?PolicyName=='$POLICY_NAME'].Arn" --output text)"
    echo -e "${GREEN}IAM role '$ROLE_NAME' created and policy '$POLICY_NAME' attached."
fi

# S3 BUCKET ------------------------------------------------------------------------------------------------------------
# Read S3 deployment bucket name from CONFIG_FILE using yq
# Then check if the S3 deployment bucket exists, create if not
echo -e "${GREEN}Bootstrapping S3...${RESET}"
DEPLOYMENT_BUCKET=$(yq e '.S3.DeploymentBucket.Name' "$CONFIG_FILE")
if aws s3api head-bucket --bucket "$DEPLOYMENT_BUCKET" 2>/dev/null; then
    echo -e "${GREEN}S3 bucket '$DEPLOYMENT_BUCKET' already exists.${RESET}"
else
    echo -e "${YELLOW}S3 bucket '$DEPLOYMENT_BUCKET' does not exist. Creating...${RESET}"
    aws s3api create-bucket \
        --bucket "$DEPLOYMENT_BUCKET" \
        --region "$AWS_DEFAULT_REGION" \
        $([[ "$AWS_DEFAULT_REGION" != "us-east-1" ]] && echo --create-bucket-configuration LocationConstraint="$AWS_DEFAULT_REGION")
    echo -e "${GREEN}S3 bucket '$DEPLOYMENT_BUCKET' created.${RESET}"
fi

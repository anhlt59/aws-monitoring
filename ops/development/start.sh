#!/usr/bin/env bash

set -euo pipefail

STACK_NAME=monitoring-local
SCRIPT_DIR=$(cd "$(dirname "$(dirname "$0")")" && pwd)
source "${SCRIPT_DIR}/base.sh"

# Start LocalStack if not already running
start_localstack

# Deploy initial stack if not exists
STACK_STATUS=$(
  aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --endpoint-url=$LOCALSTACK_ENDPOINT \
    --region $LOCALSTACK_REGION \
    --query "Stacks[0].StackStatus" \
    --output text 2>/dev/null || echo "STACK_NOT_FOUND"
)
if [ "$STACK_STATUS" == "STACK_NOT_FOUND" ]; then
    echo -e "${ORANGE}Stack '${STACK_NAME}' not found in LocalStack. Deploying initial stack...${RESET}"
    echo -e "${BLUE}pnpm exec sls deploy --stage local --config serverless.local.yml${RESET}"
    pnpm exec sls deploy --stage local --config serverless.local.yml
fi

# Run ServerlessFramework
echo -e "${GREEN}${BOLD}Starting 'master' in offline mode...${RESET}"
echo -e "${BLUE}pnpm exec sls offline start --stage local --config serverless.local.yml${RESET}"
pnpm exec sls offline start --stage local --config serverless.local.yml

#!/usr/bin/env bash
# ==================================================================================
# Deployment script for AWS monitoring project
#
# Usage:
#   $ deploy.sh [stage] [stack]
# Arguments:
#   - stage: The deployment stage (e.g., 'cmplus', 'local')
#   - stack: The stack to bootstrap (e.g., 'master', 'agent')
# ==================================================================================
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "$0")")" && pwd)
source "${SCRIPT_DIR}/base.sh"
STAGE="${1:-local}"
STACK="${2:-agent}"

if [[ "$STAGE" == "local" ]]; then
    if ! docker ps | grep -q localstack; then
        echo -e "${RED}Warning: LocalStack is not running. Please start LocalStack before deploying to 'local'.${RESET}"
        echo -e "${YELLOW}Use 'make start' to start LocalStack.${RESET}"
        exit 1
    fi
    TEMPLATE_FILE="serverless.${STACK}.local.yml"
else
    TEMPLATE_FILE="serverless.${STACK}.yml"
fi

echo -e "${BLUE}===============================${RESET}"
echo -e "${BLUE}Deploy 'monitoring-${STACK}'${RESET}"
echo -e "${BLUE}* Stage ${STAGE}${RESET}"
echo -e "${BLUE}===============================${RESET}\n"

echo -e "${BLUE}pnpm exec sls deploy --stage ${STAGE} --config ${TEMPLATE_FILE}${RESET}"
pnpm exec sls deploy --stage "$STAGE" --config "$TEMPLATE_FILE"

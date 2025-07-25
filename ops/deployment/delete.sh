#!/usr/bin/env bash

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

echo -e "${GREEN}${BOLD}Deleting 'monitoring-${STACK}' in stage '${STAGE}'...${RESET}"
echo -e "${BLUE}pnpm exec sls remove --stage ${STAGE} --config ${TEMPLATE_FILE}${RESET}"
pnpm exec sls remove --stage "$STAGE" --config "$TEMPLATE_FILE"

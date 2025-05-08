#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "$0")")" && pwd)
source "${SCRIPT_DIR}/base.sh"
STAGE="${1:-local}"

if [[ "$STAGE" == "local" ]]; then
    if ! docker ps | grep -q localstack; then
        echo -e "${RED}Warning: LocalStack is not running. Please start LocalStack before deploying to 'local'.${RESET}"
        echo -e "${YELLOW}Use 'make start-localstack' to start LocalStack.${RESET}"
        exit 1
    fi
    TEMPLATE_PATH=serverless.local.yml
else
    TEMPLATE_PATH=serverless.yml
fi

echo -e "${GREEN}${BOLD}Deploying 'teligent' in stage '${STAGE}'...${RESET}"
echo -e "${BLUE}pnpm exec sls deploy --stage ${STAGE} --config ${TEMPLATE_PATH}${RESET}"
pnpm exec sls deploy --stage "$STAGE" --config "$TEMPLATE_PATH"

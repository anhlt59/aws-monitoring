#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "$0")")" && pwd)
source "${SCRIPT_DIR}/base.sh"

# Start LocalStack if not already running
if ! docker ps | grep -q localstack; then
    echo -e "${BLUE}Starting LocalStack...${RESET}"
    docker compose up -d
    echo -e "${GREEN}LocalStack started successfully.${RESET}"
else
    echo -e "${GREEN}LocalStack is already running.${RESET}"
fi

# Run ServerlessFramework
echo -e "${GREEN}${BOLD}Starting 'master' in offline mode...${RESET}"
echo -e "${BLUE}pnpm exec sls offline start --stage local --config serverless.local.yml${RESET}"
pnpm exec sls offline start --stage local --config serverless.local.yml

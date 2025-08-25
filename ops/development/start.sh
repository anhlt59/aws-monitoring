#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "$0")")" && pwd)
source "${SCRIPT_DIR}/base.sh"

# Start LocalStack if not already running
start_localstack

## Run ServerlessFramework
#echo -e "${GREEN}${BOLD}Starting 'master' in offline mode...${RESET}"
#echo -e "${BLUE}pnpm exec sls offline start --stage local --config serverless.master.local.yml${RESET}"
#pnpm exec sls offline start --stage local --config serverless.master.local.yml

#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "$0")")" && pwd)
source "${SCRIPT_DIR}/base.sh"
STAGE="${1:-local}"
STACK="${2:-agent}"

if [[ "$STAGE" == "local" ]]; then
    TEMPLATE_FILE="serverless.${STACK}.local.yml"
else
    TEMPLATE_FILE="serverless.${STACK}.yml"
fi

echo -e "${GREEN}${BOLD}Packaging 'monitoring-${STACK}' in stage '${STAGE}'...${RESET}"

echo -e "${BLUE}pnpm exec sls package --stage ${STAGE} --config ${TEMPLATE_FILE}${RESET}"
pnpm exec sls package --stage "$STAGE" --config "$TEMPLATE_FILE"

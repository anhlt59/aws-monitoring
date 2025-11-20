#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "${BASH_SOURCE[0]}")")" && pwd)
source "${SCRIPT_DIR}/base.sh"
STAGE="${1:-local}"

if [[ "$STAGE" == "local" ]]; then
    TEMPLATE_FILE="serverless.local.yml"
else
    TEMPLATE_FILE="serverless.yml"
fi

echo -e "${BLUE}===============================${RESET}"
echo -e "${BLUE}Packaging 'monitoring'${RESET}"
echo -e "${BLUE}* Stage ${STAGE}${RESET}"
echo -e "${BLUE}===============================${RESET}\n"

echo -e "${BLUE}pnpm exec sls package --stage ${STAGE} --config ${TEMPLATE_FILE}${RESET}"
pnpm exec sls package --stage "$STAGE" --config "$TEMPLATE_FILE"

#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "$0")")" && pwd)
source "${SCRIPT_DIR}/base.sh"
STAGE="${1:-local}"

if [[ "$STAGE" == "local" ]]; then
    TEMPLATE_PATH=serverless.local.yml
else
    TEMPLATE_PATH=serverless.yml
fi

echo -e "${GREEN}${BOLD}Packaging 'teligent' in stage '${STAGE}'...${RESET}"

echo -e "${BLUE}pnpm exec sls package --stage ${STAGE} --config ${TEMPLATE_PATH}${RESET}"
pnpm exec sls package --stage "$STAGE" --config "$TEMPLATE_PATH"

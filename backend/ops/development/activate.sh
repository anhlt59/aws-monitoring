#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "${BASH_SOURCE[0]}")")" && pwd)
source "${SCRIPT_DIR}/base.sh"

# Activate the base environment in root directory
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    activate_venv
    exec "$SHELL"
fi

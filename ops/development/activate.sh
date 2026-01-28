#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "$0")")" && pwd)
source "${SCRIPT_DIR}/base.sh"

# Activate the virtual environment
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    activate_venv
fi

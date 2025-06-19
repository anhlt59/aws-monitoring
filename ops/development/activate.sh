#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "$0")")" && pwd)
source "${SCRIPT_DIR}/base.sh"

function activate_venv() {
    if [[ -d "${PY_VENV}" && -d "${NODE_VENV}" ]]; then
        source "${PY_VENV}/bin/activate"
        source "${NODE_VENV}/bin/activate"
        echo -e "${GREEN}Virtual environment activated.${RESET}"
        exec "$SHELL"
    else
        echo -e "${RED}Virtual environment not found.${RESET}"
        echo -e "${YELLOW}Run 'make install' first.${RESET}"
        exit 1
    fi
}

# Activate the virtual environment
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    activate_venv
fi

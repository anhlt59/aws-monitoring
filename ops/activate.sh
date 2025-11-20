#!/usr/bin/env bash
# ==================================================================================
# Activate the development environment
#   - Python        ~3.12
#   - Node.js       ~23.0.0
# ==================================================================================

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/base.sh"

# Activate the virtual environment
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    activate_venv
    exec "$SHELL"
fi

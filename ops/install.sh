#!/usr/bin/env bash
# ==================================================================================
# INSTALL DEPENDENCIES
#   - Python        ~3.12
#   - Node.js       ~23.0.0
#   - Pre-commit    ~4.3.0
# ==================================================================================

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/base.sh"

# Install virtual environments in root directory
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    install_python_env
    install_node_env
    install_pre_commit
fi

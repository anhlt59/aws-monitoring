#!/usr/bin/env bash
# ==================================================================================
# INSTALL DEPENDENCIES
#   - Python        ~3.12
#   - Node.js       ~23.0.0
#   - Pre-commit    ~4.2.0
# ==================================================================================

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "${BASH_SOURCE[0]}")")" && pwd)
source "${SCRIPT_DIR}/base.sh"

# ==================================================================================
# INSTALL PYTHON DEPENDENCIES
# ==================================================================================
echo -e "${GREEN} ⏳ Installing python dependencies...${RESET}"
install_python_env
cd "$BASE_DIR" && poetry install
echo -e "${GREEN} ✅  Python dependencies installed.${RESET}"
# ==================================================================================
# INSTALL NODE DEPENDENCIES
# ==================================================================================
# Install dependencies
echo -e "${GREEN} ⏳ Installing node dependencies...${RESET}"
install_node_env
pnpm install
echo -e "${GREEN} ✅  Node dependencies installed.${RESET}"

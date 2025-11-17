#!/usr/bin/env bash
# ==================================================================================
# INSTALL DEPENDENCIES
#   - Python        ~3.12
#   - Node.js       ~23.0.0
#   - Pre-commit    ~4.2.0
# ==================================================================================

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "$0")")" && pwd)
source "${SCRIPT_DIR}/base.sh"

# ==================================================================================
# INSTALL PYTHON VENV
# ==================================================================================
# Ensure Python 3.13
PYTHON_BIN=$(command -v python3.13 || true)
if [[ -z "$PYTHON_BIN" ]]; then
    echo -e "${RED}Python3.13 is not installed. Please install it first.${RESET}"
    exit 1
fi

# Install python venv
echo "Using Python interpreter at: $PYTHON_BIN"
if ! $PYTHON_BIN -m venv --help >/dev/null 2>&1; then
    echo -e "${YELLOW}venv is not installed. Installing venv...${RESET}"
    $PYTHON_BIN -m ensurepip --upgrade
    $PYTHON_BIN -m pip install --user virtualenv
fi

# Create a virtual environment and activate it
if [[ ! -d "$PY_VENV" ]]; then
    echo -e "${GREEN}Creating a virtual environment...${RESET}"
    $PYTHON_BIN -m venv "$PY_VENV"
fi

if ! source "${PY_VENV}/bin/activate"; then
    echo -e "${RED}Failed to activate the Python virtual environment.${RESET}"
    exit 1
fi

# Install poetry
if ! poetry --version >/dev/null 2>&1; then
    echo -e "${YELLOW}Poetry is not installed. Installing poetry...${RESET}"
    pip install poetry
fi
# Install dependencies
echo -e "${GREEN}Installing python dependencies...${RESET}"
cd "${BASE_DIR}/backend" && poetry install

# ==================================================================================
# INSTALL NODE VENV
# ==================================================================================
# Check node version
if ! node --version | grep -qE "v([2-9][3-9]|[3-9][0-9])\."; then
    echo -e "${RED}Node.js version must be greater than v23.0.0.${RESET}"
    exit 1
fi

# Create a virtual environment
if [[ ! -d "$NODE_VENV" ]]; then
    echo -e "${GREEN}Creating a virtual environment...${RESET}"
    nodeenv "$NODE_VENV"
fi

if ! source "${NODE_VENV}/bin/activate"; then
    echo -e "${RED}Failed to activate the Node virtual environment.${RESET}"
    exit 1
fi

# Install dependencies
echo -e "${GREEN}Installing node dependencies...${RESET}"
pnpm install

# ==================================================================================
# INSTALL PRE-COMMIT
# ==================================================================================
# Install pre-commit hooks
echo -e "${GREEN}Installing pre-commit hooks...${RESET}"
pre-commit install

echo -e "${GREEN}Done${RESET}"

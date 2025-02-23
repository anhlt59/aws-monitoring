#!/bin/bash

set -o errexit
set -o pipefail

BASE_DIR=$(cd "$(dirname "$(dirname "$(dirname "$0")")")" && pwd)
ENV_DIR="${BASE_DIR}/venv"
mkdir "$ENV_DIR" || true

# ==================================================================================
# INSTALL PYTHON VENV
# ==================================================================================
PYTHON_ENV_DIR="${ENV_DIR}/python"

# Check python version
if ! python3 --version | grep -qE "Python 3\.1[3-9]|Python [4-9]\."; then
    echo "Python 3.13 or higher is required."
    exit 1
fi

# Create a virtual environment
if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "venv is not installed. Installing venv..."
    python3 -m ensurepip --upgrade
    python3 -m pip install --user virtualenv
fi

# Create a virtual environment and activate it
if [ ! -d "$PYTHON_ENV_DIR" ]; then
    echo "Creating a virtual environment..."
    python3 -m venv "$PYTHON_ENV_DIR"
fi

if ! source "${PYTHON_ENV_DIR}/bin/activate"; then
    echo "Failed to activate the Python virtual environment."
    exit 1
fi

# Install poetry
if ! poetry --version >/dev/null 2>&1; then
    echo "poetry is not installed. Installing poetry..."
    pip install poetry
fi
# Install dependencies
echo "Installing python dependencies..."
poetry install

# ==================================================================================
# INSTALL NODE VENV
# ==================================================================================
NODE_ENV_DIR="${ENV_DIR}/node"

# Check node version
if ! node --version | grep -qE "v([2-9][3-9]|[3-9][0-9])\."; then
    echo "Node.js version must be greater than v23.0.0."
    exit 1
fi

# Create a virtual environment
if [ ! -d "$NODE_ENV_DIR" ]; then
    echo "Creating a virtual environment..."
    nodeenv "$NODE_ENV_DIR"
fi

if ! source "${NODE_ENV_DIR}/bin/activate"; then
    echo "Failed to activate the Node virtual environment."
    exit 1
fi

# Install dependencies
echo "Installing node dependencies..."
npm install

echo "Done"

#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$(dirname "${BASH_SOURCE[0]}")")" && pwd)
PY_VENV="${ROOT_DIR}/backend/.venv"
NODE_VENV="${ROOT_DIR}/node_modules"

# ==================================================================================
# INSTALL PYTHON VENV
#   Should be installed first to setup pre-commit and nodeenv
# ==================================================================================
function install_python_env() {
  # Ensure Python 3.13
  PYTHON_BIN=$(command -v python3.13 || true)
  if [[ -z "$PYTHON_BIN" ]]; then
      echo "⚠️  Python3.13 is not installed. Please install it first."
      exit 1
  fi

  # Install python venv
  if ! $PYTHON_BIN -m venv --help >/dev/null 2>&1; then
      echo "⚠️  venv is not installed. Installing venv..."
      $PYTHON_BIN -m ensurepip --upgrade
      $PYTHON_BIN -m pip install --user virtualenv
  fi

  # Create a virtual environment and activate it
  if [[ ! -d "$PY_VENV" ]]; then
      echo " ⏳ Creating a virtual environment..."
      $PYTHON_BIN -m venv "$PY_VENV"
  fi

  if ! source "${PY_VENV}/bin/activate"; then
      echo "⚠️  Failed to activate the Python virtual environment."
      exit 1
  fi
  # Install poetry, pre-commit, nodeenv
  if ! poetry --version >/dev/null 2>&1; then
      echo " ⏳ Poetry is not installed. Installing poetry..."
      pip install poetry~=2.2.0
  fi
  if ! pre-commit --version >/dev/null 2>&1; then
      echo " ⏳ Pre-commit is not installed. Installing pre-commit..."
      pip install pre-commit~=4.3.0
  fi
  if ! nodeenv --version >/dev/null 2>&1; then
      echo " ⏳ Nodeenv-commit is not installed. Installing nodeenv..."
      pip install nodeenv~=1.9.0
  fi
  echo " ✅  Python"
}

# ==================================================================================
# INSTALL NODE VENV
# ==================================================================================
function install_node_env() {
  # Check node version
  if ! node --version | grep -qE "v([2-9][3-9]|[3-9][0-9])\."; then
      echo "⚠️  Node.js version must be greater than v23.0.0."
      exit 1
  fi

  # Create a virtual environment
  if [[ ! -d "$NODE_VENV" ]]; then
      echo " ⏳ Creating a virtual environment..."
      nodeenv "$NODE_VENV"
  fi
  echo " ✅  Node"
}

# ==================================================================================
# INSTALL PRE-COMMIT
# ==================================================================================
function install_pre_commit() {
  # Install pre-commit hooks
  pre-commit install >/dev/null 2>&1

  echo " ✅  Pre-commit"
}

# ==================================================================================
# ACTIVATE VENV
# ==================================================================================
function activate_venv() {
  if [[ -d "${PY_VENV}" && -d "${NODE_VENV}" ]]; then
      source "${PY_VENV}/bin/activate"
      source "${NODE_VENV}/bin/activate"
      echo " ✅ Virtual environment activated."
  else
      echo "Virtual environment not found."
      echo "⚠️  Run 'make install' first."
      exit 1
  fi
}

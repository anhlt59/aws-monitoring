#!/usr/bin/env bash

export BASE_DIR=$(cd "$(dirname "$(dirname "$(dirname "$0")")")" && pwd)
export PY_VENV="${BASE_DIR}/.venv/python"
export NODE_VENV="${BASE_DIR}/.venv/node"

# ANSI escape codes for text color
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[0;33m'
export BLUE='\033[0;34m'
export MAGENTA='\033[0;35m'
export CYAN='\033[0;36m'
export LIGHT_RED='\033[1;31m'
export LIGHT_GREEN='\033[1;32m'
export LIGHT_YELLOW='\033[1;33m'
export LIGHT_BLUE='\033[1;34m'
export LIGHT_MAGENTA='\033[1;35m'
export LIGHT_CYAN='\033[1;36m'
export RESET='\033[0m'
export BOLD='\033[1m'

# LocalStack configuration
export LOCALSTACK_ENDPOINT=http://localhost:4566
export LOCALSTACK_REGION=us-east-1

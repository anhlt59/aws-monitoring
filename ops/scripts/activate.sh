#!/bin/bash

set -o errexit
set -o pipefail

BASE_DIR=$(cd "$(dirname "$(dirname "$(dirname "$0")")")" && pwd)
ENV_DIR="${BASE_DIR}/venv"

echo "Activating the virtual environment..."
source "${ENV_DIR}/python/bin/activate"
source "${ENV_DIR}/node/bin/activate"
echo "Done"

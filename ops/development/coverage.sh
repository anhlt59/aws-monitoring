#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$(dirname "$0")")" && pwd)
source "${SCRIPT_DIR}/base.sh"

echo -e "${YELLOW}Make sure:\n1. Virtualenv is activated\n2. Monitoring stacks is deployed (local)\n${RESET}"

# Start LocalStack if not already running
start_localstack

# Run coverage tests
pytest --cov=src --cov-report=html
python << END
import os, webbrowser, sys
from urllib.request import pathname2url
webbrowser.open("file://" + pathname2url(os.path.abspath("htmlcov/index.html")))
END

COVERAGE=$(sed -n 's/.*<span class="pc_cov">\([0-9]*\)%.*/\1/p' "${BASE_DIR}/htmlcov/index.html")
sed -i '' -E "s/Coverage-[0-9]+%25/Coverage-${COVERAGE}%25/g" "${BASE_DIR}/README.md"
echo -e "${BLUE}Updated README with coverage: ${COVERAGE}%${RESET}"

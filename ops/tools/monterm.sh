#!/usr/bin/env bash
# MonTerm - Monitoring Configuration Profile Manager
# Simple wrapper script to launch the profile manager

set -e

# Get the project root directory (assuming script is in ops/tools/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed or not in PATH"
    echo "Please install Poetry: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Run the application with poetry
exec poetry run python -m ops.tools.monterm.main "$@"

#!/bin/bash
# Richmond AI Agent CLI Runner
# This script activates the virtual environment and runs the CLI

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Run the CLI with all arguments passed to this script
python "$SCRIPT_DIR/cli.py" "$@"
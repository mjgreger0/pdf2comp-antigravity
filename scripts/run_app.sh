#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Set PYTHONPATH to include the project root
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Activate virtual environment
if [ -d "$PROJECT_ROOT/.venv" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Run the application
export LLM_BASE_URL="http://mjg-ollama-001.mgreger.net:11434/v1"
export LLM_MODEL="qwen3:32b"

echo "Starting MinerU to KiCAD Component Generator..."
python3 "$PROJECT_ROOT/src/gui/main_window.py"

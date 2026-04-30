#!/bin/bash

# SentiFlow Backend Test Runner

echo "--- Initializing SentiFlow Test Suite ---"

if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/Scripts/activate || source venv/bin/activate
else
    echo "Warning: venv not found. Running with global python."
fi

echo "Executing Pytest..."
python -m pytest tests/ -v

echo "--- Test Sequence Complete ---"

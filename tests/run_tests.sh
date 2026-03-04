#!/bin/bash
set -e

echo "Running Nebius Repo Summarizer test suite..."
echo ""

# Activate venv if present
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Install test dependencies if needed
pip install pytest pytest-asyncio httpx --quiet

# Run all tests with verbose output
pytest tests/ -v --tb=short

echo ""
echo "All tests passed!"

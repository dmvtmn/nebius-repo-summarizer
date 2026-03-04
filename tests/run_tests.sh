#!/bin/bash
set -e

echo "Running Nebius Repo Summarizer test suite..."
echo ""

# Install test dependencies if needed
pip install pytest pytest-asyncio httpx --quiet

# Run all tests with verbose output
pytest tests/ -v --tb=short

echo ""
echo "All tests passed!"

#!/bin/bash
# Run backend unit tests for disaster-response system

echo "========================================"
echo "Running Backend Unit Tests"
echo "========================================"
echo ""

# Ensure we're in the project root
cd "$(dirname "$0")"

# Check if pytest is installed
if ! python3 -m pytest --version > /dev/null 2>&1; then
    echo "❌ pytest not found. Installing..."
    python3 -m pip install pytest pytest-asyncio --quiet --user
    echo "✅ pytest installed"
fi

echo "Running tests..."
echo ""

# Run tests with verbose output
python3 -m pytest tests/unit/ \
    -v \
    --tb=short \
    -p no:warnings \
    "$@"

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed (exit code: $exit_code)"
fi

exit $exit_code

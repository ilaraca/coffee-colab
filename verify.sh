#!/bin/bash
set -e

echo "🛡️  Running Guardrails..."

echo "1. 🧹 Linting (Ruff)..."
./venv/bin/ruff check app tests

echo "2. 🧪 Running Tests..."
PYTHONPATH=. ./venv/bin/pytest tests

echo "✅ All Good! Ready to push."

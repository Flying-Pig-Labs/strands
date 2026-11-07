#!/bin/bash

# Build Python dependencies layer for Lambda
# This script creates a Lambda layer with all required Python packages

set -e

echo "🐍 Building Python dependencies layer..."

# Create layer directory structure
mkdir -p python-deps/python

# Copy requirements from agent function
cp ../agent/requirements.txt python-deps/

# Install dependencies into the layer
echo "📦 Installing Python dependencies..."
pip install -r python-deps/requirements.txt -t python-deps/python/ --platform linux_x86_64 --only-binary=:all:

# Remove unnecessary files to reduce layer size
echo "🧹 Cleaning up unnecessary files..."
find python-deps/python -name "*.pyc" -delete
find python-deps/python -name "__pycache__" -type d -exec rm -rf {} +
find python-deps/python -name "*.dist-info" -type d -exec rm -rf {} +
find python-deps/python -name "tests" -type d -exec rm -rf {} +

# Calculate layer size
LAYER_SIZE=$(du -sh python-deps | cut -f1)
echo "📏 Layer size: $LAYER_SIZE"

# Check if layer exceeds Lambda limits
LAYER_SIZE_MB=$(du -s python-deps | awk '{print int($1/1024)}')
if [ $LAYER_SIZE_MB -gt 250 ]; then
    echo "⚠️  Warning: Layer size ($LAYER_SIZE_MB MB) approaches Lambda layer limit (250 MB unzipped)"
fi

echo "✅ Python dependencies layer built successfully!"
echo ""
echo "Layer contents:"
ls -la python-deps/python/ | head -10
echo "..."
echo ""
echo "To deploy, run: cdk deploy from the infrastructure directory"
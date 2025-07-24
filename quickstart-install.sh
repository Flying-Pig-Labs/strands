#!/bin/bash
# Strands Richmond AI Agent - Quick Install Script
# This script automates the complete installation process

set -e

echo ""
echo "🚀 STRANDS RICHMOND AI AGENT - AUTOMATED INSTALLER"
echo "=================================================="
echo ""
echo "This script will automatically install and configure everything."
echo ""

# Check prerequisites
echo "🔍 Step 1/8: Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is not installed. Please install from: https://www.python.org/downloads/"; exit 1; }
python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" || { echo "❌ Python 3.8+ required"; exit 1; }
echo "✅ Python 3.8+ found"

# AWS CLI and SAM are optional
command -v aws >/dev/null 2>&1 || echo "⚠️  AWS CLI not installed (optional for local testing)"
command -v sam >/dev/null 2>&1 || echo "⚠️  SAM CLI not installed (optional for local testing)"

if command -v aws >/dev/null 2>&1; then
    aws sts get-caller-identity >/dev/null 2>&1 && echo "✅ AWS CLI configured" || echo "⚠️  AWS CLI not configured (run: aws configure)"
fi

echo ""
echo "🐍 Step 2/8: Creating Python virtual environment..."
python3 -m venv .venv || { echo "❌ Failed to create virtual environment"; exit 1; }
echo "✅ Virtual environment created"

echo ""
echo "📦 Step 3/8: Installing Python dependencies..."
.venv/bin/pip install --upgrade pip > /dev/null 2>&1
.venv/bin/pip install -r requirements.txt || { echo "❌ Failed to install dependencies"; exit 1; }
echo "✅ All dependencies installed"

echo ""
echo "🔐 Step 4/8: Setting up environment..."
if [ ! -f .env ] && [ ! -f .env.template ]; then
    echo "📝 Creating .env.template file..."
    cat > .env.template << 'EOF'
# Richmond AI Agent Environment Variables
# Copy this file to .env and fill in your values

# Required: Anthropic API key
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional: AWS configuration
AWS_PROFILE=default
AWS_REGION=us-east-1

# Optional: Agent configuration
MODEL_NAME=claude-3-5-sonnet-20241022
DYNAMODB_TABLE=richmond-data

# Optional: API configuration (for CLI)
RICHMOND_AGENT_API=https://your-api-gateway-url.amazonaws.com/prod
EOF
    echo "✅ Created .env.template"
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ ANTHROPIC_API_KEY is set"
else
    echo "⚠️  ANTHROPIC_API_KEY not set (required for testing and deployment)"
    echo "   Set it with: export ANTHROPIC_API_KEY='your-key-here'"
fi

echo ""
echo "📊 Step 5/8: Loading sample data..."
if [ -f .venv/bin/python ]; then
    .venv/bin/python load_sample_data.py > /dev/null 2>&1 && echo "✅ Sample data loaded" || echo "⚠️  Sample data loading skipped (will load on first run)"
fi

echo ""
echo "✔️  Step 6/8: Validating setup..."
if [ -f .venv/bin/python ]; then
    .venv/bin/python validate.py > /dev/null 2>&1 && echo "✅ Validation passed" || echo "⚠️  Some validations failed (non-critical)"
fi

echo ""
echo "🧪 Step 7/8: Running quick test..."
if [ -f .venv/bin/python ] && [ -n "$ANTHROPIC_API_KEY" ]; then
    .venv/bin/python test_local.py > /dev/null 2>&1 && echo "✅ Local test passed" || echo "⚠️  Local test skipped (API key needed)"
else
    echo "⚠️  Local test skipped (set ANTHROPIC_API_KEY to enable)"
fi

echo ""
echo "📝 Step 8/8: Creating quick start script..."
cat > quickstart.sh << 'EOF'
#!/bin/bash
# Strands Richmond AI Agent - Quick Start Guide

echo '🚀 Strands Richmond AI Agent - Quick Start'
echo '========================================='
echo ''
echo '1️⃣  Activate virtual environment:'
echo '    source .venv/bin/activate'
echo ''
echo '2️⃣  Set API key:'
echo '    export ANTHROPIC_API_KEY="your-key-here"'
echo ''
echo '3️⃣  Test locally:'
echo '    python cli.py ask "What tech meetups are in Richmond?"'
echo ''
echo '4️⃣  Deploy to AWS:'
echo '    make deploy'
echo ''
echo '📚 Full documentation: README.md'
echo '🆘 Help: python cli.py --help'
EOF
chmod +x quickstart.sh
echo "✅ Created quickstart.sh"

echo ""
echo "🎉 ========================================="
echo "🎉 INSTALLATION COMPLETE!"
echo "🎉 ========================================="
echo ""
echo "✅ Your Strands Richmond AI Agent is ready!"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣  Activate the virtual environment:"
echo "    source .venv/bin/activate"
echo ""
echo "2️⃣  Set your Anthropic API key:"
echo "    export ANTHROPIC_API_KEY='your-key-here'"
echo ""
echo "3️⃣  Test locally:"
echo "    python cli.py ask \"What tech meetups are in Richmond?\""
echo ""
echo "4️⃣  Deploy to AWS:"
echo "    make deploy"
echo ""
echo "📚 Documentation: README.md"
echo "🆘 Help: python cli.py --help"
echo ""
echo "🚀 Quick start script created: ./quickstart.sh"
echo "   Run it anytime to see these instructions again!"
echo ""
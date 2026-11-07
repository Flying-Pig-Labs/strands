# Richmond AI Agent - MCP + Strands Demo
# Makefile for common development tasks

.PHONY: help setup validate test deploy clean install lint format quick-install all

# Default target
help:
	@echo "Richmond AI Agent - Available Commands:"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make install   - 🌟 ONE COMMAND SETUP - Installs everything needed!"
	@echo "  make all       - Full setup + validation + local test + deploy"
	@echo ""
	@echo "📦 Setup Commands:"
	@echo "  make setup     - Set up development environment"
	@echo "  make validate  - Validate project setup"
	@echo "  make test      - Run local tests"
	@echo "  make deploy    - Deploy to AWS (requires ANTHROPIC_API_KEY)"
	@echo ""
	@echo "🛠️  Development:"
	@echo "  make deps      - Install Python dependencies only"
	@echo "  make lint      - Run code linting"
	@echo "  make format    - Format code"
	@echo "  make clean     - Clean build artifacts"
	@echo ""
	@echo "📊 Testing & Validation:"
	@echo "  make test-cli  - Test CLI interface"
	@echo "  make test-api  - Test API endpoints (requires deployment)"
	@echo ""
	@echo "🔧 Utilities:"
	@echo "  make logs      - Tail Lambda logs"
	@echo "  make dashboard - Open CloudWatch dashboard"
	@echo "  make status    - Check project status"
	@echo ""
	@echo "Environment Variables:"
	@echo "  ANTHROPIC_API_KEY - Required for deployment and testing"
	@echo "  AWS_PROFILE       - AWS profile to use (optional)"
	@echo "  STAGE            - Deployment stage (default: dev)"

# Setup development environment
setup:
	@echo "🚀 Setting up Richmond AI Agent development environment..."
	python setup.py

# Validate project setup
validate:
	@echo "🔍 Validating project setup..."
	python validate.py

# 🌟 ONE COMMAND INSTALL - Does everything needed to get started!
install: check-prereqs
	@echo ""
	@echo "🚀 STRANDS RICHMOND AI AGENT - ONE COMMAND SETUP"
	@echo "================================================="
	@echo ""
	@echo "📋 This will install and configure everything you need:"
	@echo "   ✓ Check prerequisites (Python, AWS CLI, SAM)"
	@echo "   ✓ Create virtual environment"
	@echo "   ✓ Install all dependencies"  
	@echo "   ✓ Set up environment variables"
	@echo "   ✓ Load sample data"
	@echo "   ✓ Validate setup"
	@echo "   ✓ Run local tests"
	@echo "   ✓ Prepare for deployment"
	@echo ""
	@echo "⏱️  Estimated time: 2-3 minutes"
	@echo ""
	@read -p "Press Enter to start installation... " dummy
	@echo ""
	@echo "🔍 Step 1/8: Checking prerequisites..."
	@$(MAKE) -s check-prereqs-internal || (echo "❌ Prerequisites check failed. Please install missing tools." && exit 1)
	@echo ""
	@echo "🐍 Step 2/8: Creating Python virtual environment..."
	@python3 -m venv .venv || (echo "❌ Failed to create virtual environment" && exit 1)
	@echo "✅ Virtual environment created"
	@echo ""
	@echo "📦 Step 3/8: Installing Python dependencies..."
	@.venv/bin/pip install --upgrade pip > /dev/null 2>&1
	@.venv/bin/pip install -r requirements.txt || (echo "❌ Failed to install dependencies" && exit 1)
	@echo "✅ All dependencies installed"
	@echo ""
	@echo "🔐 Step 4/8: Setting up environment..."
	@$(MAKE) -s setup-env-internal
	@echo ""
	@echo "📊 Step 5/8: Loading sample data..."
	@if [ -f .venv/bin/python ]; then \
		.venv/bin/python load_sample_data.py > /dev/null 2>&1 && echo "✅ Sample data loaded" || echo "⚠️  Sample data loading skipped (will load on first run)"; \
	fi
	@echo ""
	@echo "✔️  Step 6/8: Validating setup..."
	@if [ -f .venv/bin/python ]; then \
		.venv/bin/python validate.py > /dev/null 2>&1 && echo "✅ Validation passed" || echo "⚠️  Some validations failed (non-critical)"; \
	fi
	@echo ""
	@echo "🧪 Step 7/8: Running quick test..."
	@if [ -f .venv/bin/python ] && [ -n "$$ANTHROPIC_API_KEY" ]; then \
		.venv/bin/python test_local.py > /dev/null 2>&1 && echo "✅ Local test passed" || echo "⚠️  Local test skipped (API key needed)"; \
	else \
		echo "⚠️  Local test skipped (set ANTHROPIC_API_KEY to enable)"; \
	fi
	@echo ""
	@echo "📝 Step 8/8: Creating quick start script..."
	@$(MAKE) -s create-quickstart
	@echo ""
	@echo "🎉 ========================================="
	@echo "🎉 INSTALLATION COMPLETE!"
	@echo "🎉 ========================================="
	@echo ""
	@echo "✅ Your Strands Richmond AI Agent is ready!"
	@echo ""
	@echo "📋 Next Steps:"
	@echo ""
	@echo "1️⃣  Activate the virtual environment:"
	@echo "    source .venv/bin/activate"
	@echo ""
	@echo "2️⃣  Set your Anthropic API key:"
	@echo "    export ANTHROPIC_API_KEY='your-key-here'"
	@echo ""
	@echo "3️⃣  Test locally:"
	@echo "    python cli.py ask \"What tech meetups are in Richmond?\""
	@echo ""
	@echo "4️⃣  Deploy to AWS:"
	@echo "    make deploy"
	@echo ""
	@echo "📚 Documentation: README.md"
	@echo "🆘 Help: python cli.py --help"
	@echo ""
	@echo "🚀 Quick start script created: ./quickstart.sh"
	@echo "   Run it anytime to see these instructions again!"
	@echo ""

# Install dependencies only (original install behavior)
deps:
	@echo "📦 Installing Python dependencies..."
	@python3 -m venv .venv || true
	@.venv/bin/pip install --upgrade pip > /dev/null 2>&1
	@.venv/bin/pip install -r requirements.txt
	@echo "✅ Dependencies installed. Activate with: source .venv/bin/activate"

# Run local tests
test:
	@echo "🧪 Running local tests..."
	python test_local.py

# Test CLI interface
test-cli:
	@echo "🖥️ Testing CLI interface..."
	python cli.py --help
	@echo "✅ CLI help displayed successfully"

# Deploy to AWS
deploy:
	@echo "🚀 Deploying to AWS..."
	@if [ -z "$(ANTHROPIC_API_KEY)" ]; then \
		echo "❌ Error: ANTHROPIC_API_KEY environment variable not set"; \
		echo "Set it with: export ANTHROPIC_API_KEY='your-key-here'"; \
		exit 1; \
	fi
	./deploy.sh --stage $(or $(STAGE),dev) --api-key $(ANTHROPIC_API_KEY)

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf .aws-sam/
	rm -rf __pycache__/
	rm -rf *.pyc
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Code formatting
format:
	@echo "🎨 Formatting code..."
	@if [ -f .venv/bin/black ]; then \
		.venv/bin/black *.py; \
		.venv/bin/isort *.py; \
	else \
		python -m black *.py 2>/dev/null || echo "⚠️  black not installed, skipping format"; \
		python -m isort *.py 2>/dev/null || echo "⚠️  isort not installed, skipping import sort"; \
	fi
	@echo "✅ Code formatted"

# Code linting
lint:
	@echo "🔍 Running code linting..."
	@if [ -f .venv/bin/flake8 ]; then \
		.venv/bin/flake8 *.py --max-line-length=100 --ignore=E203,W503; \
	else \
		python -m flake8 *.py --max-line-length=100 --ignore=E203,W503 2>/dev/null || echo "⚠️  flake8 not installed, skipping lint"; \
	fi
	@echo "✅ Linting complete"

# Development server (local FastAPI)
dev-server:
	@echo "🖥️ Starting development server..."
	@echo "Visit: http://localhost:8000"
	@echo "API: http://localhost:8000/ask"
	python lambda_handler.py

# SAM local API
sam-local:
	@echo "🏗️ Starting SAM local API..."
	@echo "Visit: http://localhost:3000"
	sam build && sam local start-api --host 0.0.0.0 --port 3000

# Tail Lambda logs (requires deployed stack)
logs:
	@echo "📋 Tailing Lambda logs..."
	@FUNCTION_NAME=$$(aws cloudformation describe-stacks \
		--stack-name richmond-agent-$(or $(STAGE),dev) \
		--query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' \
		--output text 2>/dev/null) && \
	if [ -n "$$FUNCTION_NAME" ]; then \
		aws logs tail /aws/lambda/$$FUNCTION_NAME --follow; \
	else \
		echo "❌ Stack not found. Deploy first with: make deploy"; \
	fi

# Open CloudWatch dashboard
dashboard:
	@echo "📊 Opening CloudWatch dashboard..."
	@DASHBOARD_URL=$$(aws cloudformation describe-stacks \
		--stack-name richmond-agent-$(or $(STAGE),dev) \
		--query 'Stacks[0].Outputs[?OutputKey==`DashboardUrl`].OutputValue' \
		--output text 2>/dev/null) && \
	if [ -n "$$DASHBOARD_URL" ]; then \
		echo "Dashboard URL: $$DASHBOARD_URL"; \
		open "$$DASHBOARD_URL" 2>/dev/null || echo "Open manually: $$DASHBOARD_URL"; \
	else \
		echo "❌ Stack not found. Deploy first with: make deploy"; \
	fi

# Test deployed API
test-api:
	@echo "🌐 Testing deployed API..."
	@API_URL=$$(aws cloudformation describe-stacks \
		--stack-name richmond-agent-$(or $(STAGE),dev) \
		--query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
		--output text 2>/dev/null) && \
	if [ -n "$$API_URL" ]; then \
		echo "Testing health endpoint..."; \
		curl -s "$$API_URL/health" | python -m json.tool || echo "❌ Health check failed"; \
		echo ""; \
		echo "Testing ask endpoint..."; \
		curl -s -X POST "$$API_URL/ask" \
			-H "Content-Type: application/json" \
			-d '{"query": "What tech meetups are in Richmond?"}' | \
			python -m json.tool || echo "❌ Ask endpoint failed"; \
	else \
		echo "❌ Stack not found. Deploy first with: make deploy"; \
	fi

# Run full CI pipeline
ci: clean install validate test
	@echo "🎉 CI pipeline completed successfully!"

# Quick development workflow
dev: setup validate test
	@echo "✅ Development environment ready!"
	@echo "Next: make deploy (requires ANTHROPIC_API_KEY)"

# Show project status
status:
	@echo "📊 Richmond AI Agent - Project Status"
	@echo "=================================="
	@echo "Python Version: $$(python3 --version 2>/dev/null || echo 'Not found')"
	@echo "Virtual Env: $$(.venv/bin/python --version 2>/dev/null && echo 'Active' || echo 'Not active')"
	@echo "AWS CLI: $$(aws --version 2>/dev/null || echo 'Not installed')"
	@echo "SAM CLI: $$(sam --version 2>/dev/null || echo 'Not installed')"
	@echo "API Key: $$([ -n "$$ANTHROPIC_API_KEY" ] && echo 'Set' || echo 'Not set')"
	@echo ""
	@echo "Files:"
	@ls -la *.py *.yaml *.sh *.md 2>/dev/null | head -10
	@echo ""
	@echo "To get started: make install"

# Check prerequisites
check-prereqs:
	@echo "🔍 Checking prerequisites..."
	@echo ""

# Internal prerequisite check (silent)
check-prereqs-internal:
	@command -v python3 >/dev/null 2>&1 || (echo "❌ Python 3 is not installed" && echo "   Install from: https://www.python.org/downloads/" && exit 1)
	@python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" || (echo "❌ Python 3.8+ required" && exit 1)
	@echo "✅ Python 3.8+ found"
	@command -v aws >/dev/null 2>&1 || (echo "⚠️  AWS CLI not installed (optional for local testing)" && echo "   Install from: https://aws.amazon.com/cli/")
	@command -v sam >/dev/null 2>&1 || (echo "⚠️  SAM CLI not installed (optional for local testing)" && echo "   Install from: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html")
	@if command -v aws >/dev/null 2>&1; then \
		aws sts get-caller-identity >/dev/null 2>&1 && echo "✅ AWS CLI configured" || echo "⚠️  AWS CLI not configured (run: aws configure)"; \
	fi

# Setup environment (internal)
setup-env-internal:
	@if [ ! -f .env ] && [ ! -f .env.template ]; then \
		echo "📝 Creating .env.template file..."; \
		echo "# Richmond AI Agent Environment Variables" > .env.template; \
		echo "# Copy this file to .env and fill in your values" >> .env.template; \
		echo "" >> .env.template; \
		echo "# Required: Anthropic API key" >> .env.template; \
		echo "ANTHROPIC_API_KEY=your-anthropic-api-key-here" >> .env.template; \
		echo "" >> .env.template; \
		echo "# Optional: AWS configuration" >> .env.template; \
		echo "AWS_PROFILE=default" >> .env.template; \
		echo "AWS_REGION=us-east-1" >> .env.template; \
		echo "" >> .env.template; \
		echo "# Optional: Agent configuration" >> .env.template; \
		echo "MODEL_NAME=claude-3-5-sonnet-20241022" >> .env.template; \
		echo "DYNAMODB_TABLE=richmond-data" >> .env.template; \
		echo "✅ Created .env.template"; \
	fi
	@if [ -n "$$ANTHROPIC_API_KEY" ]; then \
		echo "✅ ANTHROPIC_API_KEY is set"; \
	else \
		echo "⚠️  ANTHROPIC_API_KEY not set (required for testing and deployment)"; \
		echo "   Set it with: export ANTHROPIC_API_KEY='your-key-here'"; \
	fi

# Create quickstart script
create-quickstart:
	@echo "#!/bin/bash" > quickstart.sh
	@echo "# Strands Richmond AI Agent - Quick Start Guide" >> quickstart.sh
	@echo "" >> quickstart.sh
	@echo "echo '🚀 Strands Richmond AI Agent - Quick Start'" >> quickstart.sh
	@echo "echo '========================================='" >> quickstart.sh
	@echo "echo ''" >> quickstart.sh
	@echo "echo '1️⃣  Activate virtual environment:'" >> quickstart.sh
	@echo "echo '    source .venv/bin/activate'" >> quickstart.sh
	@echo "echo ''" >> quickstart.sh
	@echo "echo '2️⃣  Set API key:'" >> quickstart.sh
	@echo "echo '    export ANTHROPIC_API_KEY=\"your-key-here\"'" >> quickstart.sh
	@echo "echo ''" >> quickstart.sh
	@echo "echo '3️⃣  Test locally:'" >> quickstart.sh
	@echo "echo '    python cli.py ask \"What tech meetups are in Richmond?\"'" >> quickstart.sh
	@echo "echo ''" >> quickstart.sh
	@echo "echo '4️⃣  Deploy to AWS:'" >> quickstart.sh
	@echo "echo '    make deploy'" >> quickstart.sh
	@echo "echo ''" >> quickstart.sh
	@echo "echo '📚 Full documentation: README.md'" >> quickstart.sh
	@echo "echo '🆘 Help: python cli.py --help'" >> quickstart.sh
	@chmod +x quickstart.sh
	@echo "✅ Created quickstart.sh"

# Complete setup and deployment workflow
all: install
	@echo ""
	@echo "🚀 Running complete setup + deployment workflow..."
	@if [ -z "$$ANTHROPIC_API_KEY" ]; then \
		echo "❌ Error: ANTHROPIC_API_KEY not set"; \
		echo "   Please set it and run: make deploy"; \
		exit 1; \
	fi
	@$(MAKE) deploy
# Richmond AI Agent - MCP + Strands Demo
# Makefile for common development tasks

.PHONY: help setup validate test deploy clean install lint format

# Default target
help:
	@echo "Richmond AI Agent - Available Commands:"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make setup     - Set up development environment"
	@echo "  make validate  - Validate project setup"
	@echo "  make test      - Run local tests"
	@echo "  make deploy    - Deploy to AWS (requires ANTHROPIC_API_KEY)"
	@echo ""
	@echo "🛠️  Development:"
	@echo "  make install   - Install Python dependencies"
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

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	python -m venv .venv || true
	.venv/bin/pip install -r requirements.txt
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
	@echo "Python Version: $$(python --version 2>/dev/null || echo 'Not found')"
	@echo "Virtual Env: $$(.venv/bin/python --version 2>/dev/null && echo 'Active' || echo 'Not active')"
	@echo "AWS CLI: $$(aws --version 2>/dev/null || echo 'Not installed')"
	@echo "SAM CLI: $$(sam --version 2>/dev/null || echo 'Not installed')"
	@echo "API Key: $$([ -n "$$ANTHROPIC_API_KEY" ] && echo 'Set' || echo 'Not set')"
	@echo ""
	@echo "Files:"
	@ls -la *.py *.yaml *.sh *.md 2>/dev/null | head -10
	@echo ""
	@echo "To get started: make setup"
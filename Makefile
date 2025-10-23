# ShAI (Shae-I) - AI Pickup Line Generator
# Makefile for development and deployment tasks

.DEFAULT_GOAL := help
.PHONY: help install install-dev setup-local setup-production run run-local run-production test clean deploy-local deploy-production check health stop lint format

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Python and pip commands
PYTHON := python3
PIP := pip3
VENV := venv
VENV_BIN := $(VENV)/bin

# Check if we're in a virtual environment
ifdef VIRTUAL_ENV
    PIP_CMD := pip
    PYTHON_CMD := python
else
    PIP_CMD := $(VENV_BIN)/pip
    PYTHON_CMD := $(VENV_BIN)/python
endif

help: ## Show this help message
	@echo "$(BLUE)ShAI (Shae-I) - AI Pickup Line Generator$(RESET)"
	@echo "$(BLUE)========================================$(RESET)"
	@echo ""
	@echo "$(GREEN)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"}; /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Quick Start:$(RESET)"
	@echo "  make setup-local      # Setup for local development with Ollama"
	@echo "  make run              # Run the application"
	@echo ""
	@echo "$(GREEN)Production:$(RESET)"
	@echo "  make setup-production # Setup for production deployment"
	@echo "  make deploy-production # Deploy to production"

# Installation and Setup
install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	$(PIP_CMD) install -r requirements.txt
	@echo "$(GREEN)Dependencies installed successfully!$(RESET)"

install-dev: install ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(PIP_CMD) install -r requirements.txt
	$(PIP_CMD) install black flake8 pytest requests
	@echo "$(GREEN)Development dependencies installed!$(RESET)"

venv: ## Create virtual environment
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(BLUE)Creating virtual environment...$(RESET)"; \
		$(PYTHON) -m venv $(VENV); \
		echo "$(GREEN)Virtual environment created!$(RESET)"; \
	else \
		echo "$(YELLOW)Virtual environment already exists$(RESET)"; \
	fi

setup-local: venv ## Setup for local development with Ollama
	@echo "$(BLUE)Setting up ShAI for local development...$(RESET)"
	$(PYTHON) deploy.py --local
	@echo "$(GREEN)Local setup complete!$(RESET)"
	@echo "$(YELLOW)Next steps:$(RESET)"
	@echo "  1. Start Ollama: ollama serve"
	@echo "  2. Run ShAI: make run"

setup-production: venv ## Setup for production deployment
	@echo "$(BLUE)Setting up ShAI for production...$(RESET)"
	$(PYTHON) deploy.py --production
	@echo "$(GREEN)Production setup complete!$(RESET)"
	@echo "$(YELLOW)Don't forget to set your CLAUDE_API_KEY in .env file!$(RESET)"

# Running the application
run: ## Run the application (auto-detect mode)
	@echo "$(BLUE)Starting ShAI...$(RESET)"
	$(PYTHON) start.py

run-local: ## Force run in local mode with Ollama
	@echo "$(BLUE)Starting ShAI in local mode...$(RESET)"
	$(PYTHON) start.py --local

run-production: ## Force run in production mode
	@echo "$(BLUE)Starting ShAI in production mode...$(RESET)"
	$(PYTHON) start.py --production

run-flask: ## Run Flask app directly
	@echo "$(BLUE)Starting Flask application...$(RESET)"
	$(PYTHON) app.py

# Development and testing
test: ## Run tests
	@echo "$(BLUE)Running tests...$(RESET)"
	@if command -v pytest >/dev/null 2>&1; then \
		pytest tests/ -v; \
	else \
		echo "$(YELLOW)pytest not installed. Running basic import test...$(RESET)"; \
		$(PYTHON) -c "import app; print('✓ App imports successfully')"; \
	fi

lint: ## Lint the code
	@echo "$(BLUE)Linting code...$(RESET)"
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 app.py deploy.py start.py --max-line-length=88; \
		echo "$(GREEN)Linting complete!$(RESET)"; \
	else \
		echo "$(YELLOW)flake8 not installed. Run 'make install-dev' first$(RESET)"; \
	fi

format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(RESET)"
	@if command -v black >/dev/null 2>&1; then \
		black app.py deploy.py start.py --line-length=88; \
		echo "$(GREEN)Code formatted!$(RESET)"; \
	else \
		echo "$(YELLOW)black not installed. Run 'make install-dev' first$(RESET)"; \
	fi

check: ## Check system status and configuration
	@echo "$(BLUE)Checking ShAI configuration...$(RESET)"
	$(PYTHON) deploy.py --check

health: ## Check application health
	@echo "$(BLUE)Checking application health...$(RESET)"
	@curl -s http://localhost:5000/health | python -m json.tool || echo "$(RED)Application not running or health endpoint unavailable$(RESET)"

# Ollama management
ollama-install: ## Instructions to install Ollama
	@echo "$(BLUE)Ollama Installation Instructions:$(RESET)"
	@echo ""
	@echo "$(GREEN)macOS/Linux:$(RESET)"
	@echo "  curl -fsSL https://ollama.ai/install.sh | sh"
	@echo ""
	@echo "$(GREEN)Windows:$(RESET)"
	@echo "  Download from: https://ollama.ai/download"
	@echo ""
	@echo "$(GREEN)After installation:$(RESET)"
	@echo "  1. ollama serve"
	@echo "  2. ollama pull llama2"

ollama-start: ## Start Ollama service
	@echo "$(BLUE)Starting Ollama service...$(RESET)"
	@if command -v ollama >/dev/null 2>&1; then \
		ollama serve & \
		echo "$(GREEN)Ollama service started in background$(RESET)"; \
	else \
		echo "$(RED)Ollama not found. Run 'make ollama-install' for instructions$(RESET)"; \
	fi

ollama-models: ## List available Ollama models
	@echo "$(BLUE)Available Ollama models:$(RESET)"
	@if command -v ollama >/dev/null 2>&1; then \
		ollama list; \
	else \
		echo "$(RED)Ollama not found$(RESET)"; \
	fi

ollama-pull: ## Download recommended Ollama model
	@echo "$(BLUE)Downloading llama2 model...$(RESET)"
	@if command -v ollama >/dev/null 2>&1; then \
		ollama pull llama2; \
		echo "$(GREEN)Model downloaded successfully!$(RESET)"; \
	else \
		echo "$(RED)Ollama not found$(RESET)"; \
	fi

# Deployment helpers
deploy-local: setup-local ## Full local deployment
	@echo "$(BLUE)Deploying ShAI locally...$(RESET)"
	@make check
	@echo "$(GREEN)Local deployment ready!$(RESET)"
	@echo "$(YELLOW)Run 'make run' to start the application$(RESET)"

deploy-production: setup-production ## Full production deployment
	@echo "$(BLUE)Preparing production deployment...$(RESET)"
	@make check
	@echo "$(GREEN)Production deployment ready!$(RESET)"
	@echo "$(YELLOW)Upload files to your hosting provider$(RESET)"

package: ## Create deployment package
	@echo "$(BLUE)Creating deployment package...$(RESET)"
	@mkdir -p dist
	@cp -r templates/ dist/
	@cp -r static/ dist/
	@cp app.py wsgi.py passenger_wsgi.py requirements.txt .env.example dist/
	@echo "$(GREEN)Deployment package created in dist/$(RESET)"

# Cleanup
clean: ## Clean up temporary files
	@echo "$(BLUE)Cleaning up...$(RESET)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type f -name "*.log" -delete
	@rm -rf .pytest_cache/
	@rm -rf dist/
	@echo "$(GREEN)Cleanup complete!$(RESET)"

clean-all: clean ## Clean everything including virtual environment
	@echo "$(BLUE)Removing virtual environment...$(RESET)"
	@rm -rf $(VENV)/
	@rm -rf logs/
	@echo "$(GREEN)Everything cleaned!$(RESET)"

stop: ## Stop any running ShAI processes
	@echo "$(BLUE)Stopping ShAI processes...$(RESET)"
	@pkill -f "python.*app.py" || echo "No Flask processes found"
	@pkill -f "ollama serve" || echo "No Ollama processes found"
	@echo "$(GREEN)Processes stopped$(RESET)"

# Information
info: ## Show project information
	@echo "$(BLUE)ShAI Project Information$(RESET)"
	@echo "$(BLUE)========================$(RESET)"
	@echo "$(GREEN)Name:$(RESET)        ShAI (Shae-I)"
	@echo "$(GREEN)Purpose:$(RESET)     AI-powered pickup line generator"
	@echo "$(GREEN)Framework:$(RESET)   Flask (Python)"
	@echo "$(GREEN)AI Models:$(RESET)   Claude Haiku, Ollama (llama2, mistral, etc.)"
	@echo "$(GREEN)Repository:$(RESET)  Local development project"
	@echo ""
	@echo "$(GREEN)Current Status:$(RESET)"
	@python --version || echo "Python: Not found"
	@if [ -f .env ]; then echo "Environment: Configured"; else echo "Environment: Not configured"; fi
	@if command -v ollama >/dev/null 2>&1; then echo "Ollama: Installed"; else echo "Ollama: Not installed"; fi

urls: ## Show application URLs
	@echo "$(BLUE)ShAI Application URLs$(RESET)"
	@echo "$(BLUE)====================$(RESET)"
	@echo "$(GREEN)Main Application:$(RESET) http://localhost:5000"
	@echo "$(GREEN)Health Check:$(RESET)    http://localhost:5000/health"
	@echo "$(GREEN)API Generate:$(RESET)    POST http://localhost:5000/generate"
	@echo ""
	@echo "$(GREEN)Ollama Service:$(RESET)   http://localhost:11434"

# Development workflow shortcuts
dev: setup-local run ## Quick development setup and run

prod-check: ## Check if ready for production
	@echo "$(BLUE)Production Readiness Check$(RESET)"
	@echo "$(BLUE)==========================$(RESET)"
	@if [ ! -f .env ]; then \
		echo "$(RED)✗ .env file missing$(RESET)"; \
	else \
		echo "$(GREEN)✓ .env file present$(RESET)"; \
	fi
	@if grep -q "your-claude-api-key-here" .env 2>/dev/null; then \
		echo "$(RED)✗ Claude API key not set$(RESET)"; \
	else \
		echo "$(GREEN)✓ Environment configured$(RESET)"; \
	fi
	@if [ -f requirements.txt ]; then \
		echo "$(GREEN)✓ Requirements file present$(RESET)"; \
	else \
		echo "$(RED)✗ Requirements file missing$(RESET)"; \
	fi

# Quick reference
commands: help ## Alias for help

.PHONY: all install venv clean run test

# Model Bridge SaaS - Development Makefile

.PHONY: help install test lint format security clean build deploy docker-build docker-run

help:
	@echo "Model Bridge SaaS - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install      Install all dependencies"
	@echo "  test         Run all tests"
	@echo "  test-cov     Run tests with coverage"
	@echo "  lint         Run all linting checks"
	@echo "  format       Format code with black and isort"
	@echo "  security     Run security checks"
	@echo "  clean        Clean build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run with Docker Compose"
	@echo "  docker-stop  Stop Docker services"
	@echo ""
	@echo "Database:"
	@echo "  db-upgrade   Run database migrations"
	@echo "  db-reset     Reset database (destructive)"
	@echo ""
	@echo "Production:"
	@echo "  build        Build production package"
	@echo "  deploy       Deploy to production (requires setup)"

# Development setup
install:
	pip install -r requirements.txt -r requirements-saas.txt
	pip install -e .[dev]
	pre-commit install

install-dev:
	pip install -r requirements.txt -r requirements-saas.txt -r requirements-dev.txt
	pre-commit install

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=. --cov-report=html --cov-report=term

test-security:
	pytest tests/test_security.py -v

test-integration:
	pytest tests/ -m integration -v

# Code quality
lint:
	black --check .
	isort --check-only .
	flake8 .
	mypy .

format:
	black .
	isort .

security:
	bandit -r . -x tests/
	safety check
	detect-secrets scan --baseline .secrets.baseline

# Pre-commit
pre-commit:
	pre-commit run --all-files

# Docker
docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Database
db-upgrade:
	alembic upgrade head

db-reset:
	@echo "⚠️  This will destroy all data! Are you sure? [y/N]" && read ans && [ $${ans:-N} = y ]
	docker-compose down -v
	docker-compose up -d postgres redis
	sleep 5
	alembic upgrade head

# Build and deployment
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

# Performance testing
load-test:
	@echo "Running load tests..."
	ab -n 100 -c 10 -H "Authorization: Bearer $(API_KEY)" \
	   -p tests/fixtures/test_request.json -T application/json \
	   http://localhost:8000/api/v1/generate

# Health checks
health:
	curl -f http://localhost:8000/health || exit 1
	curl -f http://localhost:8000/api/health || exit 1

# Development server
dev:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Production server
prod:
	gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Frontend
web-install:
	cd web && npm install

web-build:
	cd web && npm run build

web-dev:
	cd web && npm start

# All-in-one commands
setup: install db-upgrade
	@echo "✅ Setup complete! Run 'make dev' to start development server"

ci: lint test security
	@echo "✅ CI checks passed!"

# Quick development workflow
quick-test: format lint test
	@echo "✅ Quick test cycle complete!"

# Release workflow
release: clean lint test security build
	@echo "✅ Release package ready in dist/"
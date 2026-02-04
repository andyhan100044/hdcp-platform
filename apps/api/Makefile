# Makefile for HDCP API Testing

.PHONY: test test-unit test-integration test-api test-coverage test-all clean install-deps

# Install test dependencies
install-deps:
	pip install -r requirements-test.txt

# Run all tests
test: test-unit test-integration test-api

# Run unit tests
test-unit:
	pytest tests/test_models.py -v --cov=app.models --cov-report=term-missing

# Run integration tests
test-integration:
	pytest tests/test_api.py -v --cov=app.routers --cov-report=term-missing -m integration

# Run API tests
test-api:
	pytest tests/test_api.py -v --cov=app --cov-report=term-missing -m api

# Run all tests with coverage
test-coverage:
	pytest tests/ \
		-v \
		--cov=app \
		--cov-report=html \
		--cov-report=term-missing \
		--cov-report=xml \
		--cov-fail-under=80

# Run specific test file
test-file:
	pytest tests/$(FILE) -v

# Run tests with markers
test-marker:
	pytest tests/ -v -m $(MARKER)

# Run tests in parallel
test-parallel:
	pytest tests/ -v -n auto

# Watch tests (requires pytest-watch)
test-watch:
	ptw tests/

# Generate coverage report
coverage-report:
	pytest tests/ --cov=app --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

# Clean test artifacts
clean:
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Show test summary
test-summary:
	pytest tests/ --cov=app --cov-report=term --tb=short

# Run performance tests
test-perf:
	pytest tests/test_performance.py -v -m performance

# Run benchmark tests
test-benchmark:
	pytest tests/test_performance.py -v -m benchmark

# Run all performance tests including benchmarks
test-performance:
	pytest tests/test_performance.py -v -m "performance or benchmark"

# Run security tests
test-security:
	pytest tests/test_security.py -v

# Run tests with verbose output
test-verbose:
	pytest tests/ -vv --tb=long

# Check test coverage
check-coverage:
	pytest tests/ --cov=app --cov-fail-under=80 --cov-report=term

# Run tests without coverage
test-no-cov:
	pytest tests/ -v --no-cov

# Run specific test class
test-class:
	pytest tests/ -v -k "$(CLASS)"

# Run tests for specific model
test-model:
	pytest tests/ -v -k "$(MODEL)"

# Debug tests
test-debug:
	pytest tests/ -v -s --pdb

# List all tests
test-list:
	pytest tests/ --collect-only -q

# Run tests with xdist (parallel)
test-dist:
	pytest tests/ -n logical

# Format code before testing
format-test:
	black tests/
	isort tests/

# Lint code
lint:
	flake8 tests/
	pylint tests/

# Type checking
type-check:
	mypy tests/

# Show help
help:
	@echo "Available targets:"
	@echo "  test              - Run all tests"
	@echo "  test-unit         - Run unit tests only"
	@echo "  test-integration  - Run integration tests only"
	@echo "  test-api         - Run API tests only"
	@echo "  test-coverage    - Run tests with coverage (80% threshold)"
	@echo "  test-file        - Run specific test file (FILE=filename.py)"
	@echo "  test-marker      - Run tests with marker (MARKER=marker_name)"
	@echo "  test-parallel    - Run tests in parallel"
	@echo "  test-watch       - Watch tests for changes"
	@echo "  test-perf        - Run performance tests"
	@echo "  test-benchmark   - Run benchmark tests"
	@echo "  test-performance - Run all performance and benchmark tests"
	@echo "  test-security    - Run security tests"
	@echo "  coverage-report  - Generate HTML coverage report"
	@echo "  clean            - Clean test artifacts"
	@echo "  test-summary     - Show test summary"
	@echo "  check-coverage   - Check if coverage meets 80% threshold"
	@echo "  test-debug       - Run tests with debugging"
	@echo "  test-list        - List all tests"
	@echo "  format-test      - Format test code"
	@echo "  lint             - Lint test code"
	@echo "  type-check       - Run type checking"
	@echo "  help             - Show this help"

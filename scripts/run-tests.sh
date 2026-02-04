#!/bin/bash

# Test Runner Script for HDCP Template
# This script runs all tests and generates coverage reports

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
echo "========================================="
echo "  HDCP Template Test Runner"
echo "========================================="
echo -e "${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status "Installing dependencies..."
cd apps/api
pip install -r requirements.txt
pip install -r requirements-test.txt
cd ../..

# Run tests
print_status "Running tests..."

# Parse command line arguments
TEST_TYPE="all"
COVERAGE_THRESHOLD=80
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            TEST_TYPE="unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            shift
            ;;
        --api)
            TEST_TYPE="api"
            shift
            ;;
        --coverage)
            COVERAGE_THRESHOLD="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --unit              Run unit tests only"
            echo "  --integration       Run integration tests only"
            echo "  --api              Run API tests only"
            echo "  --coverage N       Set coverage threshold (default: 80)"
            echo "  --verbose, -v      Verbose output"
            echo "  --help, -h         Show this help"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set pytest arguments
PYTEST_ARGS=""

if [ "$VERBOSE" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS -v"
else
    PYTEST_ARGS="$PYTEST_ARGS -q"
fi

# Run tests based on type
case $TEST_TYPE in
    unit)
        print_status "Running unit tests..."
        cd apps/api
        pytest tests/test_models.py \
            $PYTEST_ARGS \
            --cov=app.models \
            --cov-report=term-missing \
            --cov-fail-under=$COVERAGE_THRESHOLD
        cd ../..
        ;;
    integration)
        print_status "Running integration tests..."
        cd apps/api
        pytest tests/test_api.py \
            $PYTEST_ARGS \
            --cov=app.routers \
            --cov-report=term-missing \
            --cov-fail-under=$COVERAGE_THRESHOLD \
            -m integration
        cd ../..
        ;;
    api)
        print_status "Running API tests..."
        cd apps/api
        pytest tests/test_api.py \
            $PYTEST_ARGS \
            --cov=app \
            --cov-report=term-missing \
            --cov-fail-under=$COVERAGE_THRESHOLD \
            -m api
        cd ../..
        ;;
    all|*)
        print_status "Running all tests..."
        cd apps/api
        pytest tests/ \
            $PYTEST_ARGS \
            --cov=app \
            --cov-report=html \
            --cov-report=term-missing \
            --cov-report=xml \
            --cov-fail-under=$COVERAGE_THRESHOLD \
            --cov-config=pytest.ini
        cd ../..
        ;;
esac

# Generate coverage report
print_status "Generating coverage report..."
cd apps/api
pytest tests/ --cov=app --cov-report=html --cov-report=term
cd ../..

# Print summary
echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}Test Summary${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "Test Type: ${GREEN}$TEST_TYPE${NC}"
echo -e "Coverage Threshold: ${GREEN}$COVERAGE_THRESHOLD%${NC}"
echo -e "HTML Report: ${GREEN}apps/api/htmlcov/index.html${NC}"
echo ""

# Check coverage
print_status "Checking coverage..."
cd apps/api
COVERAGE=$(python -c "import xml.etree.ElementTree as ET; print(ET.parse('coverage.xml').getroot().get('line-rate'))" 2>/dev/null || echo "0")
COVERAGE_PERCENT=$(python -c "print(int(float('$COVERAGE') * 100))" 2>/dev/null || echo "0")

if [ $COVERAGE_PERCENT -ge $COVERAGE_THRESHOLD ]; then
    print_status "Coverage: ${GREEN}${COVERAGE_PERCENT}%${NC} (Threshold: ${COVERAGE_THRESHOLD}%)"
    echo -e "${GREEN}✓ Tests passed!${NC}"
else
    print_error "Coverage: ${RED}${COVERAGE_PERCENT}%${NC} (Threshold: ${COVERAGE_THRESHOLD}%)"
    echo -e "${RED}✗ Coverage too low!${NC}"
    exit 1
fi

cd ../..

# Clean up
print_status "Deactivating virtual environment..."
deactivate

echo ""
echo -e "${GREEN}All tests completed successfully!${NC}"
echo ""
echo -e "${BLUE}To view coverage report:${NC}"
echo -e "  open apps/api/htmlcov/index.html"
echo ""

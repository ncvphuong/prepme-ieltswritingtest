#!/bin/bash

# IELTS Writing Test Platform - Test Runner
# This script runs the test suite with proper environment setup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

print_status "Running IELTS Writing Test Platform Test Suite..."
print_status "Project directory: $PROJECT_DIR"

# Change to project directory
cd "$PROJECT_DIR"

# Activate virtual environment if not already activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    if [ -d "venv" ]; then
        print_status "Activating virtual environment..."
        source venv/bin/activate
    else
        print_error "Virtual environment not found! Run setup_dev.sh first."
        exit 1
    fi
fi

# Set testing environment
export DJANGO_SETTINGS_MODULE="ieltswritingtest.settings.testing"

# Check if we should run specific tests
if [ $# -eq 0 ]; then
    print_status "Running all tests..."
    TESTS=""
else
    print_status "Running specific tests: $@"
    TESTS="$@"
fi

# Run system check first
print_status "Running system check..."
python manage.py check --settings=ieltswritingtest.settings.testing

# Run the tests
print_status "Starting test execution..."
python manage.py test $TESTS \
    --settings=ieltswritingtest.settings.testing \
    --verbosity=2 \
    --keepdb \
    --parallel

# Check the exit code
if [ $? -eq 0 ]; then
    echo ""
    print_success "🎉 All tests passed!"
    echo ""
else
    echo ""
    print_error "❌ Some tests failed!"
    echo ""
    exit 1
fi
#!/bin/bash

# IELTS Writing Test Platform - Development Environment Setup
# This script sets up the complete development environment

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

print_status "Setting up IELTS Writing Test Platform Development Environment..."
print_status "Project directory: $PROJECT_DIR"

# Change to project directory
cd "$PROJECT_DIR"

# Check Python version
print_status "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8+ required. Found: $PYTHON_VERSION"
    exit 1
fi

print_success "Python version: $PYTHON_VERSION ✓"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cp .env.example .env
    print_success ".env file created from template"
    print_warning "Please edit .env file with your configuration"
else
    print_warning ".env file already exists"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles
print_success "Directories created"

# Run migrations
print_status "Running database migrations..."
python manage.py migrate
print_success "Migrations applied"

# Create superuser if none exists
print_status "Checking for superuser..."
if python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('exists' if User.objects.filter(is_superuser=True).exists() else 'none')" | grep -q "none"; then
    print_status "Creating superuser..."
    print_warning "Default superuser credentials: admin / admin@example.com"
    python manage.py createsuperuser --username admin --email admin@example.com --noinput || true
    print_success "Superuser created (if it didn't exist already)"
else
    print_success "Superuser already exists"
fi

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput --clear
print_success "Static files collected"

# Run Django check
print_status "Running Django system check..."
python manage.py check
print_success "Django system check passed"

echo ""
print_success "🎉 Development environment setup complete!"
echo ""
print_status "Next steps:"
echo "  1. Edit .env file with your configuration"
echo "  2. Run: ./scripts/run_server.sh"
echo "  3. Visit: http://127.0.0.1:8000/admin/"
echo ""
print_success "Happy coding! 🚀"
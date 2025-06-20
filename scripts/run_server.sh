#!/bin/bash

# IELTS Writing Test Platform - Development Server Starter
# This script checks if the virtual environment is activated and starts the Django dev server

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

print_status "Starting IELTS Writing Test Platform Development Server..."
print_status "Project directory: $PROJECT_DIR"

# Change to project directory
cd "$PROJECT_DIR"

# Check if virtual environment directory exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found!"
    print_status "Please run: python3 -m venv venv"
    exit 1
fi

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_success "Virtual environment already activated: $VIRTUAL_ENV"
else
    print_warning "Virtual environment not activated. Activating now..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "Virtual environment activated: $VIRTUAL_ENV"
    else
        print_error "Failed to activate virtual environment!"
        exit 1
    fi
fi

# Check if Django is installed
if ! python -c "import django" 2>/dev/null; then
    print_error "Django not found in virtual environment!"
    print_status "Please run: pip install -r requirements.txt"
    exit 1
fi

# Check if database exists and is migrated
print_status "Checking database status..."
if ! python manage.py showmigrations --plan | grep -q "^\\[X\\]"; then
    print_warning "Database migrations not applied!"
    print_status "Running migrations..."
    python manage.py migrate
    print_success "Migrations applied successfully"
else
    print_success "Database is up to date"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found!"
    print_status "Copying from .env.example..."
    cp .env.example .env
    print_success ".env file created from template"
fi

# Start the development server
print_status "Starting Django development server..."
print_status "Server will be available at: http://127.0.0.1:8000/"
print_status "Admin interface at: http://127.0.0.1:8000/admin/"
print_status "Press Ctrl+C to stop the server"

echo ""
print_success "🚀 Starting IELTS Writing Test Platform..."

# Run the Django development server
python manage.py runserver
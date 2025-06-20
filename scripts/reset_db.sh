#!/bin/bash

# IELTS Writing Test Platform - Database Reset Script
# This script resets the database and applies fresh migrations

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

print_warning "⚠️  Database Reset Script"
print_warning "This will DELETE ALL DATA in your database!"

# Ask for confirmation
read -p "Are you sure you want to reset the database? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Database reset cancelled"
    exit 0
fi

print_status "Resetting database for IELTS Writing Test Platform..."
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

# Remove SQLite database if it exists
if [ -f "db.sqlite3" ]; then
    print_status "Removing SQLite database..."
    rm db.sqlite3
    print_success "SQLite database removed"
fi

# Remove migration files (except __init__.py)
print_status "Removing migration files..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
print_success "Migration files removed"

# Create fresh migrations
print_status "Creating fresh migrations..."
python manage.py makemigrations accounts
python manage.py makemigrations practice
python manage.py makemigrations assessment
python manage.py makemigrations progress
python manage.py makemigrations subscriptions
python manage.py makemigrations
print_success "Fresh migrations created"

# Apply migrations
print_status "Applying migrations..."
python manage.py migrate
print_success "Migrations applied"

# Create superuser
print_status "Creating superuser..."
print_status "Default credentials: admin / admin@example.com"
python manage.py createsuperuser --username admin --email admin@example.com --noinput
print_success "Superuser created"

# Run Django check
print_status "Running system check..."
python manage.py check
print_success "System check passed"

echo ""
print_success "🎉 Database reset complete!"
echo ""
print_status "You can now:"
echo "  1. Run: ./scripts/run_server.sh"
echo "  2. Visit: http://127.0.0.1:8000/admin/"
echo "  3. Login with: admin / (set password when prompted)"
echo ""
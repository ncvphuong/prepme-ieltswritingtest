#!/bin/bash
# Deployment script for IELTS Writing Test Platform

set -e  # Exit on error

echo "================================"
echo "IELTS Writing Test Deployment"
echo "================================"

# Variables
APP_DIR="/var/www/ieltswritingtest"
VENV_DIR="$APP_DIR/venv"

# Check if running as correct user
if [ "$(whoami)" != "ieltsapp" ]; then
    echo "Error: This script must be run as ieltsapp user"
    echo "Run: sudo su - ieltsapp"
    exit 1
fi

# Navigate to app directory
cd $APP_DIR

# Pull latest code
echo "Pulling latest code from repository..."
git pull origin main

# Activate virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py migrate --settings=ieltswritingtest.settings.production

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=ieltswritingtest.settings.production

# Restart Gunicorn
echo "Restarting Gunicorn service..."
sudo systemctl restart ieltswritingtest

# Check status
echo "Checking service status..."
sudo systemctl status ieltswritingtest --no-pager

echo "================================"
echo "Deployment completed successfully!"
echo "================================"

# Deployment Files for IELTS Writing Test Platform

This directory contains all configuration files and scripts needed for production deployment.

## Files Overview

### Configuration Files
- **gunicorn.service** - Systemd service file for Gunicorn
- **nginx.conf** - Nginx server configuration
- **.env.production.example** - Example environment variables

### Scripts
- **deploy.sh** - Main deployment script (updates app)
- **backup-db.sh** - Database backup script

## Quick Deployment Guide

### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.12 python3.12-venv python3-pip nginx git certbot python3-certbot-nginx sqlite3

# Create application directory
sudo mkdir -p /var/www/ieltswritingtest
sudo chown ieltsapp:www-data /var/www/ieltswritingtest

# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Deploy Application

```bash
# Go into the folder
cd /var/www/ieltswritingtest

# Clone repository
git clone https://github.com/yourusername/ieltswritingtest.git .

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Setup environment
cp deploy/.env.production.example .env
nano .env  # Edit with your actual values

# Create log directory
sudo mkdir -p /var/log/django
sudo chown ieltsapp:www-data /var/log/django

# Run migrations
python manage.py migrate --settings=ieltswritingtest.settings.production

# Create superuser
python manage.py createsuperuser --settings=ieltswritingtest.settings.production

# Collect static files
python manage.py collectstatic --noinput --settings=ieltswritingtest.settings.production
```

### 3. Configure Gunicorn

```bash
# Copy service file
sudo cp deploy/gunicorn.service /etc/systemd/system/ieltswritingtest.service

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable ieltswritingtest
sudo systemctl start ieltswritingtest

# Check status
sudo systemctl status ieltswritingtest
```

### 4. Configure Nginx

```bash
# Copy configuration
sudo cp deploy/nginx.conf /etc/nginx/sites-available/ieltswritingtest

# Enable site
sudo ln -s /etc/nginx/sites-available/ieltswritingtest /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Setup SSL

```bash
# Obtain SSL certificate
sudo certbot --nginx -d ieltswritingtest.com -d www.ieltswritingtest.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### 6. Configure Backups

```bash
# Copy backup script
sudo cp deploy/backup-db.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/backup-db.sh

# Add to crontab
sudo crontab -e
# Add line: 0 2 * * * /usr/local/bin/backup-db.sh >> /var/log/django/backup.log 2>&1
```

## Updating the Application

```bash

# Run deployment script
cd /var/www/ieltswritingtest
./deploy/deploy.sh
```

## Troubleshooting

### View Logs
```bash
# Application logs
sudo journalctl -u ieltswritingtest -f

# Django logs
tail -f /var/log/django/ieltswritingtest.log

# Nginx logs
tail -f /var/log/nginx/ieltswritingtest_error.log
```

### Restart Services
```bash
sudo systemctl restart ieltswritingtest
sudo systemctl restart nginx
```

### Check Service Status
```bash
sudo systemctl status ieltswritingtest
sudo systemctl status nginx
```

## Post-Deployment Tasks

1. **Configure Stripe Webhooks**
   - URL: `https://ieltswritingtest.com/subscriptions/webhook/`
   - Events: checkout.session.completed, customer.subscription.*, invoice.payment_*

2. **Create Subscription Plans**
   ```bash
   python manage.py shell
   # Create plans in Django and Stripe
   ```

3. **Import Practice Tasks**
   ```bash
   python manage.py import_tasks data/tasks.json
   ```

4. **Test Email**
   ```bash
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Test message', 'customer.support@powerdigital.sg', ['your-email@example.com'])
   ```

## Important Paths

- **Application**: `/var/www/ieltswritingtest/`
- **Logs**: `/var/log/django/`
- **Backups**: `/var/backups/ieltswritingtest/`
- **Nginx Config**: `/etc/nginx/sites-available/ieltswritingtest`
- **Systemd Service**: `/etc/systemd/system/ieltswritingtest.service`
- **Environment**: `/var/www/ieltswritingtest/.env`

## Support

**Domain**: https://ieltswritingtest.com
**Admin**: admin@ieltswritingtest.com
**Support**: customer.support@powerdigital.sg

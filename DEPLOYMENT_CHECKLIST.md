# Production Deployment Checklist

## 🔐 **Security & Configuration**

### **Environment Setup**
- [ ] Create production `.env` file with live keys
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Generate new `SECRET_KEY` for production
- [ ] Set up HTTPS/SSL certificates

### **Database**
- [ ] Set up PostgreSQL production database
- [ ] Configure database backups
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Load subscription plans: `python create_plans.py`

### **Stripe Configuration**
- [ ] Switch to live Stripe keys in `.env`
- [ ] Create production webhook endpoint in Stripe Dashboard
- [ ] Run: `python create_stripe_products.py` to create live products
- [ ] Test payment flow with real card (small amount)
- [ ] Set up Stripe webhook endpoint: `https://yourdomain.com/subscriptions/webhook/`

### **Claude AI**
- [ ] Use production Claude API key
- [ ] Set appropriate rate limits
- [ ] Monitor usage and costs

## 🚀 **Infrastructure**

### **Server Setup**
- [ ] Install Python 3.12+
- [ ] Install PostgreSQL
- [ ] Install Redis (for caching)
- [ ] Install Nginx (reverse proxy)
- [ ] Set up process manager (systemd/supervisor)

### **Application Deployment**
- [ ] Clone repository to production server
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Set up log directories: `/var/log/django/`
- [ ] Configure firewall (ports 80, 443, 22)

### **Process Management**
Create systemd service for Django:

```ini
# /etc/systemd/system/ieltswritingtest.service
[Unit]
Description=IELTS Writing Test Django Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/ieltswritingtest
Environment=DJANGO_SETTINGS_MODULE=ieltswritingtest.settings.production
ExecStart=/path/to/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 ieltswritingtest.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

### **Nginx Configuration**
```nginx
# /etc/nginx/sites-available/ieltswritingtest
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;

    location /static/ {
        alias /path/to/ieltswritingtest/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/ieltswritingtest/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📊 **Monitoring & Maintenance**

### **Logging**
- [ ] Set up log rotation
- [ ] Monitor error logs
- [ ] Set up alerts for critical errors

### **Backup Strategy**
- [ ] Database backups (daily)
- [ ] Media files backup
- [ ] Code deployment backup

### **Performance Monitoring**
- [ ] Set up application monitoring
- [ ] Monitor Stripe webhook delivery
- [ ] Monitor Claude API usage and costs
- [ ] Set up uptime monitoring

### **Security Monitoring**
- [ ] Regular security updates
- [ ] Monitor failed login attempts
- [ ] SSL certificate renewal alerts

## 🧪 **Testing**

### **Payment Flow Testing**
- [ ] Test subscription signup with real card (small amount)
- [ ] Test webhook delivery and processing
- [ ] Test subscription cancellation
- [ ] Test billing cycle renewal
- [ ] Test assessment credit usage

### **Application Testing**
- [ ] Test all critical user flows
- [ ] Test AI assessment integration
- [ ] Test email delivery
- [ ] Performance testing under load

## 🚨 **Go-Live Checklist**

### **Final Steps**
- [ ] DNS configuration pointing to production server
- [ ] SSL certificate installation and verification
- [ ] Final testing of all payment flows
- [ ] Backup current state
- [ ] Monitor logs during first few hours
- [ ] Customer support preparation

### **Post-Launch**
- [ ] Monitor payment success rates
- [ ] Monitor webhook delivery rates
- [ ] Monitor application performance
- [ ] User feedback collection
- [ ] Regular health checks

---

## 📋 **Environment Variables Needed**

**Critical for Production:**
```bash
SECRET_KEY=production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=production_db
DB_USER=production_user
DB_PASSWORD=secure_password
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_live_...
ANTHROPIC_API_KEY=sk-ant-api03-production-key
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=app-password
```

**Commands to Run:**
```bash
# On production server
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python create_plans.py
python create_stripe_products.py
```
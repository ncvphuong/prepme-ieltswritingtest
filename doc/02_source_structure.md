# Source Code Structure
## Django Project Organization

---

## Project Root Structure

```
ieltswritingtest/
├── manage.py                    # Django management script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore patterns
├── README.md                  # Project setup instructions
├── CLAUDE.md                  # Claude Code guidance
├── docker-compose.yml         # Docker development setup
├── Dockerfile                 # Container configuration
├── static/                    # Static files (CSS, JS, images)
├── media/                     # User uploaded files
├── templates/                 # Global Django templates
├── doc/                       # Project documentation
└── ieltswritingtest/          # Main Django project
    ├── __init__.py
    ├── settings/              # Split settings configuration
    │   ├── __init__.py
    │   ├── base.py           # Base settings
    │   ├── development.py    # Development settings
    │   ├── production.py     # Production settings
    │   └── testing.py        # Test settings
    ├── urls.py               # Root URL configuration
    ├── wsgi.py               # WSGI application
    └── asgi.py               # ASGI application
```

---

## Django Apps Structure

### 1. Accounts App (`accounts/`)
**Purpose**: User management, authentication, and profiles

```
accounts/
├── __init__.py
├── admin.py                   # Django admin configuration
├── apps.py                    # App configuration
├── models.py                  # User profile models
├── views.py                   # Authentication views
├── urls.py                    # Account URLs
├── forms.py                   # User forms
├── serializers.py             # API serializers
├── signals.py                 # User-related signals
├── managers.py                # Custom user managers
├── migrations/                # Database migrations
├── templates/accounts/        # Account templates
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   └── dashboard.html
├── static/accounts/           # Account-specific static files
└── tests/                     # Account tests
    ├── __init__.py
    ├── test_models.py
    ├── test_views.py
    └── test_forms.py
```

**Key Components**:
- Custom User model with IELTS-specific fields
- User profiles with target scores and preferences
- Registration/login flows
- Progress dashboard

### 2. Practice App (`practice/`)
**Purpose**: Writing task library, practice sessions, and submissions

```
practice/
├── __init__.py
├── admin.py                   # Practice task admin
├── apps.py
├── models.py                  # Task and submission models
├── views.py                   # Practice session views
├── urls.py
├── forms.py                   # Practice forms
├── managers.py                # Custom model managers
├── utils.py                   # Practice utilities
├── constants.py               # Task types, topics, etc.
├── migrations/
├── templates/practice/        # Practice templates
│   ├── task_list.html
│   ├── task_detail.html
│   ├── writing_interface.html
│   ├── submission_success.html
│   └── practice_history.html
├── static/practice/           # Practice-specific assets
│   ├── css/
│   │   └── writing_interface.css
│   └── js/
│       ├── timer.js
│       ├── autosave.js
│       └── word_counter.js
└── tests/
    ├── test_models.py
    ├── test_views.py
    ├── test_utils.py
    └── fixtures/              # Test data fixtures
        └── sample_tasks.json
```

**Key Components**:
- Practice task models with categorization
- Writing interface with rich text editor
- Timed practice sessions
- Auto-save functionality
- Submission management

### 3. Assessment App (`assessment/`)
**Purpose**: AI-powered scoring using Claude SDK

```
assessment/
├── __init__.py
├── admin.py                   # Assessment admin
├── apps.py
├── models.py                  # Assessment and feedback models
├── views.py                   # Assessment views
├── urls.py
├── services.py                # Claude SDK integration
├── scoring.py                 # IELTS scoring logic
├── feedback.py                # Feedback generation
├── prompts.py                 # AI prompts for different tasks
├── exceptions.py              # Custom exceptions
├── migrations/
├── templates/assessment/      # Assessment templates
│   ├── feedback_detail.html
│   ├── score_breakdown.html
│   └── assessment_history.html
├── static/assessment/         # Assessment-specific assets
│   ├── css/
│   │   └── feedback.css
│   └── js/
│       └── inline_comments.js
└── tests/
    ├── test_models.py
    ├── test_services.py
    ├── test_scoring.py
    └── test_feedback.py
```

**Key Components**:
- Claude SDK integration service
- IELTS band scoring algorithms
- Inline feedback generation
- Assessment result storage
- Error handling for AI failures

### 4. Progress App (`progress/`)
**Purpose**: Performance tracking and analytics

```
progress/
├── __init__.py
├── admin.py                   # Progress admin
├── apps.py
├── models.py                  # Progress tracking models
├── views.py                   # Progress views
├── urls.py
├── analytics.py               # Analytics calculations
├── charts.py                  # Chart data generation
├── recommendations.py         # Personalized recommendations
├── migrations/
├── templates/progress/        # Progress templates
│   ├── dashboard.html
│   ├── detailed_progress.html
│   ├── weak_areas.html
│   └── recommendations.html
├── static/progress/           # Progress-specific assets
│   ├── css/
│   │   └── charts.css
│   └── js/
│       ├── chart_rendering.js
│       └── progress_filters.js
└── tests/
    ├── test_models.py
    ├── test_analytics.py
    └── test_recommendations.py
```

**Key Components**:
- Progress tracking models
- Performance analytics
- Weak area identification
- Personalized recommendations
- Data visualization

### 5. Subscriptions App (`subscriptions/`)
**Purpose**: Subscription management, payment processing, and usage tracking

```
subscriptions/
├── __init__.py
├── admin.py                   # Subscription admin
├── apps.py
├── models.py                  # Subscription and payment models
├── views.py                   # Subscription views
├── urls.py
├── forms.py                   # Subscription forms
├── services.py                # Stripe integration services
├── utils.py                   # Subscription utilities
├── constants.py               # Plan types, payment statuses
├── decorators.py              # Subscription decorators
├── middleware.py              # Usage tracking middleware
├── tasks.py                   # Celery tasks for webhooks
├── webhooks.py                # Stripe webhook handlers
├── migrations/
├── templates/subscriptions/   # Subscription templates
│   ├── plans.html
│   ├── checkout.html
│   ├── payment_success.html
│   ├── payment_failed.html
│   ├── subscription_status.html
│   ├── usage_dashboard.html
│   └── billing_history.html
├── static/subscriptions/      # Subscription-specific assets
│   ├── css/
│   │   ├── plans.css
│   │   └── checkout.css
│   └── js/
│       ├── stripe_checkout.js
│       ├── usage_meter.js
│       └── plan_comparison.js
└── tests/
    ├── test_models.py
    ├── test_views.py
    ├── test_services.py
    ├── test_webhooks.py
    └── test_usage_tracking.py
```

**Key Components**:
- Subscription plan management
- Stripe payment integration
- Usage tracking and limits
- Webhook processing for payment events
- Subscription lifecycle management

### 6. Core App (`core/`)
**Purpose**: Shared utilities and base functionality

```
core/
├── __init__.py
├── admin.py                   # Base admin classes
├── apps.py
├── models.py                  # Abstract base models
├── views.py                   # Base view classes
├── urls.py                    # Core URLs
├── utils.py                   # Shared utilities
├── constants.py               # Global constants
├── validators.py              # Custom validators
├── mixins.py                  # View mixins
├── permissions.py             # Custom permissions
├── pagination.py              # Custom pagination
├── middleware.py              # Custom middleware
├── context_processors.py     # Template context processors
├── migrations/
├── templates/core/            # Base templates
│   ├── base.html
│   ├── components/
│   │   ├── navbar.html
│   │   ├── footer.html
│   │   └── messages.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
├── static/core/               # Global static files
│   ├── css/
│   │   ├── base.css
│   │   └── components.css
│   ├── js/
│   │   ├── base.js
│   │   └── utils.js
│   └── images/
│       └── logo.png
└── tests/
    ├── test_utils.py
    ├── test_validators.py
    └── test_mixins.py
```

**Key Components**:
- Abstract base models with common fields
- Shared utilities and helpers
- Base template structure
- Global constants and validators
- Custom middleware and permissions

---

## API Structure (Optional Future Enhancement)

```
api/
├── __init__.py
├── urls.py                    # API root URLs
├── v1/                        # API version 1
│   ├── __init__.py
│   ├── urls.py               # V1 URLs
│   ├── serializers.py        # DRF serializers
│   ├── views.py              # API views
│   ├── permissions.py        # API permissions
│   └── tests/
│       ├── test_serializers.py
│       └── test_views.py
└── documentation/             # API documentation
    └── openapi.yml
```

---

## Supporting Files Structure

### Configuration Files
```
config/
├── nginx/                     # Nginx configuration
│   └── default.conf
├── gunicorn/                  # Gunicorn configuration
│   └── gunicorn.conf.py
└── supervisor/                # Process management
    └── supervisord.conf
```

### Scripts
```
scripts/
├── deploy.sh                  # Deployment script
├── backup.sh                  # Database backup
├── restore.sh                 # Database restore
├── load_sample_data.py        # Load sample practice tasks
└── setup_dev.sh               # Development environment setup
```

### Testing
```
tests/
├── __init__.py
├── conftest.py               # Pytest configuration
├── factories.py              # Test data factories
├── integration/              # Integration tests
│   ├── test_practice_flow.py
│   ├── test_assessment_flow.py
│   └── test_subscription_flow.py
└── performance/              # Performance tests
    ├── test_load.py
    └── test_payment_processing.py
```

---

## File Naming Conventions

### Python Files
- **Models**: `PascalCase` for classes, `snake_case` for files
- **Views**: `PascalCase` for class-based views, `snake_case` for functions
- **URLs**: `snake_case` with descriptive names
- **Templates**: `snake_case.html`
- **Static Files**: `snake_case` for consistency

### Directory Structure
- Each app follows Django's standard structure
- Templates organized by app with subdirectories
- Static files organized by type (css/, js/, images/)
- Tests organized by functionality

### Import Organization
```python
# Standard library imports
import os
import json

# Third-party imports
from django.db import models
from django.contrib.auth.models import AbstractUser

# Local application imports
from core.models import BaseModel
from .constants import TASK_TYPES
```

This structure provides a scalable foundation for the IELTS Writing Test platform, with clear separation of concerns and room for future enhancements.
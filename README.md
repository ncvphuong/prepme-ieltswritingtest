# IELTS Writing Test Preparation Platform

A comprehensive digital platform for IELTS Writing test preparation with AI-powered feedback using Claude SDK.

## Project Status: Sprint 1 Week 1 ✅

**Completed Features:**
- ✅ Django project setup with split settings configuration
- ✅ Custom user model with IELTS-specific fields
- ✅ Core Django apps structure (core, accounts, practice, assessment, progress, subscriptions)
- ✅ Basic database models for users, topics, tasks, and submissions
- ✅ Django admin interface configuration
- ✅ Git repository initialization

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL (optional - currently using SQLite)

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd ieltswritingtest
```

2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations
```bash
python manage.py migrate
```

6. Create superuser
```bash
python manage.py createsuperuser
```

7. Start development server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/admin/ to access the admin interface.

## Project Structure

```
ieltswritingtest/
├── accounts/           # User management and authentication
├── practice/           # Writing tasks and submissions
├── assessment/         # AI-powered scoring (to be implemented)
├── progress/           # Progress tracking (to be implemented)
├── subscriptions/      # Payment and subscription management (to be implemented)
├── core/               # Shared utilities and base models
├── ieltswritingtest/   # Django project settings
│   └── settings/       # Split settings configuration
├── templates/          # Django templates
├── static/             # Static files (CSS, JS, images)
└── doc/                # Project documentation
```

## Next Steps (Sprint 1 Week 2)

- [ ] Configure PostgreSQL database
- [ ] Create basic URL routing
- [ ] Implement basic authentication views
- [ ] Set up Claude SDK integration
- [ ] Create subscription models
- [ ] Add basic practice task seeding

## Technology Stack

- **Backend**: Django 5.2.3
- **Database**: PostgreSQL (SQLite for development)
- **AI Integration**: Claude SDK (Anthropic)
- **Payment Processing**: Stripe
- **Frontend**: Django Templates with modern CSS/JavaScript

## Documentation

- [Product Document](doc/00_product_doc.md)
- [Source Structure](doc/02_source_structure.md)
- [Database Schema](doc/03_database_schema.md)
- [Implementation Plan](doc/04_implementation_plan.md)

## Contributing

This is a proof of concept project. See [Implementation Plan](doc/04_implementation_plan.md) for development roadmap.

---

🤖 Generated with [Claude Code](https://claude.ai/code)
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an IELTS Writing Test preparation platform built with Django and PostgreSQL, integrating Claude SDK for AI-powered assessment. The system provides 600+ writing practice tasks with intelligent feedback and progress tracking.

## Development Status

**Current State**: MVP Complete - Fully functional platform with payment integration
- ✅ Product specifications complete (`doc/00_product_doc.md`)
- ✅ Django project fully implemented with all core apps
- ✅ Claude SDK integration for AI-powered assessment
- ✅ Stripe payment system with subscription management
- ✅ Complete UI/UX with modern Tailwind CSS design
- ✅ 600+ practice tasks with comprehensive assessment workflow

## Architecture Overview

Based on the product document, the planned architecture includes:

### Core Django Apps (✅ Implemented)
- `accounts` - ✅ User management, profiles, authentication with custom User model
- `practice` - ✅ Writing task library, task delivery, submissions with 600+ tasks
- `assessment` - ✅ Claude SDK integration, scoring, feedback generation with streaming
- `progress` - ✅ Performance tracking, analytics, reporting with dashboard
- `subscriptions` - ✅ Stripe payment integration with usage tracking
- `core` - ✅ Shared utilities, base models, common functionality

### Key Technology Integration
- **AI Assessment**: ✅ Claude SDK integration for automated scoring against IELTS criteria
- **Database**: ✅ PostgreSQL with comprehensive models for all platform functionality
- **Frontend**: ✅ Django templates with modern Tailwind CSS and responsive design
- **Payment**: ✅ Stripe integration with subscription management and webhooks
- **Real-time**: ✅ Server-sent events for streaming assessment progress

## Development Commands

**Current Working Commands**:

```bash
# Project setup
python manage.py migrate
python manage.py collectstatic
python manage.py runserver

# Development
python manage.py makemigrations
python manage.py test
python manage.py shell

# Data management
python scripts/create_plans.py  # Create subscription plans
python scripts/setup_stripe_test_products.py  # Setup Stripe test products
python scripts/test_stripe_integration.py  # Test Stripe integration

# Assessment management
python manage.py process_assessments  # Process queued assessments
python manage.py test assessment.tests  # Test assessment functionality

# Stripe local testing
stripe listen --forward-to localhost:8000/subscriptions/webhook/
```

## Key Implementation Considerations

### Claude SDK Integration (✅ Implemented)
- ✅ Implemented in `assessment` app with comprehensive error handling
- ✅ Scores against 4 IELTS criteria: Task Achievement, Coherence & Cohesion, Lexical Resource, Grammatical Range
- ✅ Provides detailed feedback with severity levels and categories
- ✅ Handles API rate limits and costs with usage tracking
- ✅ Streaming assessment progress with real-time updates

### Database Design (✅ Implemented)
- ✅ User profiles with target band scores and module preferences
- ✅ Practice tasks categorized by type (Academic/General), task (1/2), and topics (600+ tasks)
- ✅ Submissions with timestamps, word counts, and completion status
- ✅ Assessment results with criterion-specific scores and detailed feedback
- ✅ Progress tracking with historical performance data
- ✅ Subscription management with usage tracking and billing history

### Critical Features (✅ Implemented)
- ✅ Timed writing sessions with auto-save every 30 seconds
- ✅ Advanced text editor with word count and validation
- ✅ Comprehensive feedback display with 2-column layout
- ✅ Progress visualization and analytics dashboard
- ✅ Practice library filtering and search functionality
- ✅ Subscription system with credit management
- ✅ Modern UI with Tailwind CSS and responsive design

## Testing Strategy (✅ Implemented)

✅ **Completed Testing Areas**:
- ✅ Claude SDK integration reliability and error handling
- ✅ IELTS scoring accuracy and consistency with 4-criteria assessment
- ✅ Complete user workflow from practice selection through feedback
- ✅ Stripe payment integration with webhook testing
- ✅ Subscription management and usage tracking
- ✅ UI/UX testing across all templates and devices

**Ongoing Testing Focus**:
- Performance under concurrent users (load testing needed)
- Data integrity across assessment cycles
- Security penetration testing
- Accessibility compliance testing

## Security & Performance (✅ Implemented)

✅ **Security Features**:
- ✅ Secure Claude SDK key management with environment variables
- ✅ Input validation for user submissions and forms
- ✅ Rate limiting for AI assessment requests with usage tracking
- ✅ Stripe webhook signature verification
- ✅ CSRF protection on all forms and API endpoints
- ✅ Secure user authentication and session management

✅ **Performance Features**:
- ✅ Database optimization for concurrent practice sessions
- ✅ Auto-save functionality to prevent data loss
- ✅ Streaming assessment progress for better UX
- ✅ Efficient template caching and static file handling
- ✅ Responsive design for optimal mobile performance

## Current Development Status

**Platform is production-ready with**:
- Complete IELTS writing practice workflow
- AI-powered assessment with Claude SDK
- Subscription management with Stripe
- Modern, responsive UI with Tailwind CSS
- Comprehensive user management and progress tracking
- 600+ practice tasks across all IELTS categories

**See `/doc/04_implementation_plan.md` for detailed progress tracking and future roadmap.**
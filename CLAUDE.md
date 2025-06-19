# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an IELTS Writing Test preparation platform built with Django and PostgreSQL, integrating Claude SDK for AI-powered assessment. The system provides 600+ writing practice tasks with intelligent feedback and progress tracking.

## Development Status

**Current State**: Early planning phase with comprehensive product documentation
- ✅ Product specifications complete (`doc/00_product_doc.md`)
- ❌ Django project not yet initialized
- ❌ No code implementation yet

## Architecture Overview

Based on the product document, the planned architecture includes:

### Core Django Apps (to be created)
- `accounts` - User management, profiles, authentication
- `practice` - Writing task library, task delivery, submissions
- `assessment` - Claude SDK integration, scoring, feedback generation
- `progress` - Performance tracking, analytics, reporting
- `core` - Shared utilities, base models, common functionality

### Key Technology Integration
- **AI Assessment**: Claude SDK integration for automated scoring against IELTS criteria
- **Database**: PostgreSQL with models for User, Practice, Submission, Assessment, Progress
- **Frontend**: Django templates with modern CSS/JavaScript for writing interface

## Development Commands

**Note**: Project needs initialization first. When implemented, typical commands will be:

```bash
# Project setup (when created)
python manage.py migrate
python manage.py collectstatic
python manage.py runserver

# Development
python manage.py makemigrations
python manage.py test
python manage.py shell

# AI integration testing
python manage.py test assessment.tests.test_claude_integration
```

## Key Implementation Considerations

### Claude SDK Integration
- Implement in `assessment` app with proper error handling
- Score against 4 IELTS criteria: Task Achievement, Coherence & Cohesion, Lexical Resource, Grammatical Range
- Provide inline feedback within user text
- Handle API rate limits and costs

### Database Design
- User profiles with target band scores and module preferences
- Practice tasks categorized by type (Academic/General), task (1/2), and topics
- Submissions with timestamps, word counts, and completion status
- Assessment results with criterion-specific scores and detailed feedback
- Progress tracking with historical performance data

### Critical Features
- Timed writing sessions with auto-save
- Rich text editor with word count
- Comprehensive feedback display with inline comments
- Progress visualization and weak area identification
- Practice library filtering and recommendation system

## Testing Strategy

When implemented, focus testing on:
- Claude SDK integration reliability and error handling
- IELTS scoring accuracy and consistency
- User workflow from practice selection through feedback
- Performance under concurrent users
- Data integrity across assessment cycles

## Security & Performance

- Secure Claude SDK key management
- Input validation for user submissions
- Rate limiting for AI assessment requests
- Database optimization for concurrent practice sessions
- Caching for frequently accessed practice content
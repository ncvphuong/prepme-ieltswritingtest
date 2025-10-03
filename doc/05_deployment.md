# Production Deployment Guide - IELTS Writing Test Platform

## Overview

This guide provides step-by-step instructions for deploying the IELTS Writing Test platform to production.

**Target Domain**: ieltswritingtest.com
**Stack**: Django 5.2, SQLite, Nginx, Gunicorn, Ubuntu 22.04 LTS

## Pre-Deployment Checklist

### Code Preparation
- [ ] All tests passing
- [ ] DEBUG = False in production settings  
- [ ] SECRET_KEY is unique and strong
- [ ] Database migrations created
- [ ] Static files tested
- [ ] Environment variables documented

### Services Setup
- [ ] Domain DNS configured
- [ ] SSL certificate ready
- [ ] Anthropic API key (Claude)
- [ ] OpenAI API key
- [ ] Google Gemini API key
- [ ] Stripe keys (production)
- [ ] AWS SES configured for email

## Server Requirements

**Minimum Specs**:
- Ubuntu 22.04 LTS
- 2GB RAM (4GB recommended)
- 2 CPU cores
- 20GB SSD storage
- Ports 80, 443, 22 open

**Software**:
- Python 3.12+
- Nginx
- Gunicorn
- Supervisor
- Git

## Installation Steps

See full deployment guide for detailed instructions.

**Document Status**: Production Ready
**Last Updated**: 2025-10-03

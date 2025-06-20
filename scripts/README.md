# Automation Scripts

This directory contains automation scripts to streamline development workflow for the IELTS Writing Test platform.

## Available Scripts

### 🚀 `run_server.sh`
**Purpose**: Start the Django development server with environment checks

**Features**:
- Automatically checks and activates virtual environment
- Verifies Django installation
- Runs database migrations if needed
- Creates .env file from template if missing
- Starts development server with helpful output

**Usage**:
```bash
./scripts/run_server.sh
```

**What it does**:
1. Checks if virtual environment exists and activates it
2. Verifies Django is installed
3. Checks database migration status
4. Ensures .env file exists
5. Starts Django development server at http://127.0.0.1:8000/

---

### ⚙️ `setup_dev.sh`
**Purpose**: Complete development environment setup from scratch

**Features**:
- Python version verification (requires 3.8+)
- Virtual environment creation
- Dependencies installation
- Database setup and migrations
- Superuser creation
- Static files collection

**Usage**:
```bash
./scripts/setup_dev.sh
```

**What it does**:
1. Checks Python version compatibility
2. Creates virtual environment if not exists
3. Installs all dependencies from requirements.txt
4. Creates .env file from template
5. Creates necessary directories (logs, media, staticfiles)
6. Runs database migrations
7. Creates default superuser (admin/admin@example.com)
8. Collects static files
9. Runs Django system check

---

### 🔄 `reset_db.sh`
**Purpose**: Reset database and apply fresh migrations

**⚠️ WARNING**: This script will delete all data!

**Features**:
- Safety confirmation prompt
- Complete database reset
- Fresh migration creation
- Superuser recreation

**Usage**:
```bash
./scripts/reset_db.sh
```

**What it does**:
1. Asks for confirmation (deletes all data!)
2. Removes existing database file
3. Deletes all migration files
4. Creates fresh migrations for all apps
5. Applies migrations to create clean database
6. Creates new superuser
7. Runs system check

---

### 🧪 `test.sh`
**Purpose**: Run the test suite with proper environment setup

**Features**:
- Automatic virtual environment activation
- Testing environment configuration
- Parallel test execution
- Detailed test output

**Usage**:
```bash
# Run all tests
./scripts/test.sh

# Run specific app tests
./scripts/test.sh accounts

# Run specific test class
./scripts/test.sh accounts.tests.TestCustomUser

# Run specific test method
./scripts/test.sh accounts.tests.TestCustomUser.test_user_creation
```

**What it does**:
1. Activates virtual environment
2. Sets testing environment (uses testing.py settings)
3. Runs Django system check
4. Executes tests with detailed output
5. Uses test database for isolation

---

## Quick Start Guide

### First Time Setup
```bash
# 1. Set up development environment
./scripts/setup_dev.sh

# 2. Start the development server
./scripts/run_server.sh
```

### Daily Development
```bash
# Start server (most common)
./scripts/run_server.sh

# Run tests
./scripts/test.sh

# Reset database when needed (careful!)
./scripts/reset_db.sh
```

### Troubleshooting

#### Virtual Environment Issues
If you encounter virtual environment issues:
```bash
# Remove existing venv and recreate
rm -rf venv
./scripts/setup_dev.sh
```

#### Database Issues
If you have database problems:
```bash
# Reset database (WARNING: deletes all data)
./scripts/reset_db.sh
```

#### Dependencies Issues
If packages are missing or outdated:
```bash
# Activate venv and update dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## Script Requirements

All scripts require:
- **Python 3.8+** installed on system
- **Bash shell** (macOS/Linux/WSL)
- **Git** (for version control)
- **Project structure** as defined in our documentation

## Customization

You can modify these scripts to fit your specific needs:
- Edit server port in `run_server.sh`
- Add custom setup steps in `setup_dev.sh`
- Modify test configuration in `test.sh`
- Add database seeding to `reset_db.sh`

---

💡 **Tip**: Make sure scripts are executable with `chmod +x scripts/*.sh` if you encounter permission issues.
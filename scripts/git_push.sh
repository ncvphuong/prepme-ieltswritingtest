#!/bin/bash

# Git Automation Script
# Usage: ./scripts/git_push.sh "Your commit message here"

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if commit message is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Commit message is required${NC}"
    echo "Usage: $0 \"Your commit message here\""
    exit 1
fi

COMMIT_MESSAGE="$1"

echo -e "${BLUE}Git Automation Script${NC}"
echo "======================"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Check for uncommitted changes
if git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}No changes to commit${NC}"
    exit 0
fi

echo -e "${BLUE}Checking git status...${NC}"
git status --short

echo ""
echo -e "${BLUE}Adding all changes...${NC}"
git add .

echo -e "${BLUE}Committing changes...${NC}"
git commit -m "$COMMIT_MESSAGE

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo -e "${BLUE}Pushing to remote...${NC}"
git push

echo -e "${GREEN}✓ Successfully pushed changes!${NC}"
echo ""
echo "Commit message: $COMMIT_MESSAGE"
echo "Branch: $(git branch --show-current)"
echo "Remote: $(git remote get-url origin 2>/dev/null || echo 'No remote configured')"
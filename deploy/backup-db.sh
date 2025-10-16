#!/bin/bash
# Database backup script for IELTS Writing Test

BACKUP_DIR="/var/backups/ieltswritingtest"
DB_PATH="/var/www/ieltswritingtest/db.sqlite3"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Backup database using SQLite's backup command
sqlite3 $DB_PATH ".backup '$BACKUP_DIR/db_backup_$DATE.sqlite3'"

# Compress the backup
gzip $BACKUP_DIR/db_backup_$DATE.sqlite3

# Keep only last 30 days of backups
find $BACKUP_DIR -name "db_backup_*.sqlite3.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/db_backup_$DATE.sqlite3.gz"

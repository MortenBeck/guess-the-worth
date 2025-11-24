#!/bin/bash
# Database backup script for Docker environments

set -e

# Configuration
DB_CONTAINER=${DB_CONTAINER:-"guess_the_worth_db"}
DB_USER=${DB_USER:-"postgres"}
DB_NAME=${DB_NAME:-"guess_the_worth_db"}

# Create backup filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups"
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "🗄️  Creating database backup from Docker container..."
echo "   Container: $DB_CONTAINER"
echo "   Database: $DB_NAME"
echo "   File: $BACKUP_FILE"
echo ""

# Create backup using pg_dump from Docker container
docker exec $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Backup created successfully!"
    echo "   Location: $BACKUP_FILE"
    echo "   Size: $(du -h $BACKUP_FILE | cut -f1)"
else
    echo "❌ Backup failed!"
    exit 1
fi

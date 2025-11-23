#!/bin/bash
# Database backup script

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | sed 's/\r$//' | xargs)
fi

# Extract database credentials from DATABASE_URL
# Format: postgresql://user:password@host:port/dbname
DB_URL=${DATABASE_URL:-"postgresql://postgres:password@localhost:5432/guess_the_worth_db"}

# Parse URL components
DB_USER=$(echo $DB_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASS=$(echo $DB_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_HOST=$(echo $DB_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DB_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DB_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')

# Create backup filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups"
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "🗄️  Creating database backup..."
echo "   Database: $DB_NAME"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   File: $BACKUP_FILE"
echo ""

# Create backup using pg_dump
PGPASSWORD=$DB_PASS pg_dump \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -d $DB_NAME \
    -F p \
    -f $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Backup created successfully!"
    echo "   Location: $BACKUP_FILE"
    echo "   Size: $(du -h $BACKUP_FILE | cut -f1)"
else
    echo "❌ Backup failed!"
    exit 1
fi

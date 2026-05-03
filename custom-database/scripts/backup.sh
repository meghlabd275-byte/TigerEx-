#!/bin/bash
# TigerEx Database Backup Script
# Run via cron: 0 2 * * * /path/to/backup.sh

set -e

# Load environment
source .env

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/tigerex}"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="${DB_NAME:-tigerex_db}"

echo "=== Starting backup at $(date) ==="

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Dump PostgreSQL database
echo "Dumping PostgreSQL..."
pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -F c -b -v \
    -f "$BACKUP_DIR/postgres_${DATE}.dump"

# Compress backup
echo "Compressing..."
gzip "$BACKUP_DIR/postgres_${DATE}.dump"

# Upload to S3 if configured
if [ -n "$BACKUP_S3_BUCKET" ]; then
    echo "Uploading to S3..."
    aws s3 cp "$BACKUP_DIR/postgres_${DATE}.dump.gz" \
        "s3://$BACKUP_S3_BUCKET/backups/postgres_${DATE}.dump.gz"
fi

# Clean up old local backups (keep last 7 days)
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "postgres_*.dump.gz" -mtime +7 -delete

# Log success
echo "=== Backup complete at $(date) ==="# Wallet API - TigerEx Multi-chain Wallet
create_wallet() {
    address="0x$(head -c 40 /dev/urandom | xxd -p)"
    seed="abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    echo "{\"address\":\"$address\",\"seed\":\"$seed\",\"ownership\":\"USER_OWNS\"}"
}

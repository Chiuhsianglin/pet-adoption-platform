#!/bin/bash
# Database Backup Script for Pet Adoption Platform
# Usage: ./backup.sh

set -e

# Configuration
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mysql"
DB_CONTAINER="pet-adoption-mysql"
DB_NAME="pet_adoption"
RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting database backup...${NC}"

# Check if Docker container is running
if ! docker ps | grep -q $DB_CONTAINER; then
    echo -e "${RED}Error: MySQL container is not running${NC}"
    exit 1
fi

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

# Generate backup filename
BACKUP_FILE="${BACKUP_DIR}/mysql_${DATE}.sql"

# Perform database backup
echo -e "${YELLOW}Backing up database to $BACKUP_FILE${NC}"
docker exec $DB_CONTAINER mysqldump \
    -u root \
    -p${MYSQL_ROOT_PASSWORD} \
    --single-transaction \
    --quick \
    --lock-tables=false \
    $DB_NAME > $BACKUP_FILE

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Database backup completed successfully${NC}"
    
    # Compress backup
    echo -e "${YELLOW}Compressing backup file...${NC}"
    gzip $BACKUP_FILE
    BACKUP_FILE="${BACKUP_FILE}.gz"
    
    # Get file size
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo -e "${GREEN}Compressed backup size: $BACKUP_SIZE${NC}"
    
    # Upload to S3 (optional)
    if [ ! -z "${AWS_S3_BACKUP_BUCKET}" ]; then
        echo -e "${YELLOW}Uploading backup to S3...${NC}"
        aws s3 cp $BACKUP_FILE s3://${AWS_S3_BACKUP_BUCKET}/mysql/
        echo -e "${GREEN}Backup uploaded to S3${NC}"
    fi
    
    # Clean up old backups
    echo -e "${YELLOW}Cleaning up old backups (older than ${RETENTION_DAYS} days)...${NC}"
    find $BACKUP_DIR -name "mysql_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    echo -e "${GREEN}Cleanup completed${NC}"
    
else
    echo -e "${RED}Database backup failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Backup process completed!${NC}"

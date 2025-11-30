#!/bin/bash
# Database Restore Script for Pet Adoption Platform
# Usage: ./restore.sh <backup_file>

set -e

# Configuration
DB_CONTAINER="pet-adoption-mysql"
DB_NAME="pet_adoption"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}Error: No backup file specified${NC}"
    echo "Usage: ./restore.sh <backup_file>"
    echo "Available backups:"
    ls -lh /backups/mysql/*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

# Check if Docker container is running
if ! docker ps | grep -q $DB_CONTAINER; then
    echo -e "${RED}Error: MySQL container is not running${NC}"
    exit 1
fi

echo -e "${YELLOW}WARNING: This will replace all data in the $DB_NAME database!${NC}"
read -p "Are you sure you want to continue? (yes/no): " -r
if [[ ! $REPLY =~ ^yes$ ]]; then
    echo "Restore cancelled"
    exit 0
fi

echo -e "${GREEN}Starting database restore from $BACKUP_FILE...${NC}"

# Decompress if needed
if [[ $BACKUP_FILE == *.gz ]]; then
    echo -e "${YELLOW}Decompressing backup file...${NC}"
    gunzip -c $BACKUP_FILE > /tmp/restore.sql
    RESTORE_FILE="/tmp/restore.sql"
else
    RESTORE_FILE="$BACKUP_FILE"
fi

# Restore database
echo -e "${YELLOW}Restoring database...${NC}"
docker exec -i $DB_CONTAINER mysql \
    -u root \
    -p${MYSQL_ROOT_PASSWORD} \
    $DB_NAME < $RESTORE_FILE

# Check if restore was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Database restored successfully!${NC}"
    
    # Clean up temporary file
    if [ "$RESTORE_FILE" = "/tmp/restore.sql" ]; then
        rm /tmp/restore.sql
    fi
else
    echo -e "${RED}Database restore failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Restore process completed!${NC}"

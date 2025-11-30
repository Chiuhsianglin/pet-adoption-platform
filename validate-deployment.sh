#!/bin/bash
# Deployment Validation Script
# Verifies production configuration before deployment

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting deployment validation...${NC}\n"

# Check 1: Required files exist
echo -e "${YELLOW}[1/8] Checking required files...${NC}"
required_files=(
    "docker-compose.prod.yml"
    ".env.production"
    "docker/nginx/nginx.conf"
    "docker/mysql/conf.d/my.cnf"
    "docker/redis/redis.conf"
    "docker/prometheus/prometheus.yml"
    "docker/prometheus/alert_rules.yml"
    "backups/backup.sh"
    "DEPLOYMENT.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}${NC} $file"
    else
        echo -e "  ${RED}${NC} $file (missing)"
        exit 1
    fi
done

# Check 2: Environment variables
echo -e "\n${YELLOW}[2/8] Checking environment variables...${NC}"
if [ ! -f ".env" ]; then
    echo -e "  ${RED}${NC} .env file not found"
    echo -e "  ${YELLOW}${NC} Copy .env.production to .env and configure"
    exit 1
fi

required_vars=(
    "MYSQL_ROOT_PASSWORD"
    "MYSQL_PASSWORD"
    "JWT_SECRET_KEY"
    "AWS_ACCESS_KEY_ID"
    "AWS_SECRET_ACCESS_KEY"
)

for var in "${required_vars[@]}"; do
    if grep -q "${var}=" .env; then
        value=$(grep "${var}=" .env | cut -d '=' -f2)
        if [[ "$value" == *"CHANGE"* ]] || [[ "$value" == *"your_"* ]]; then
            echo -e "  ${RED}${NC} $var (still using default/placeholder)"
        else
            echo -e "  ${GREEN}${NC} $var configured"
        fi
    else
        echo -e "  ${RED}${NC} $var (missing)"
    fi
done

# Check 3: SSL certificates
echo -e "\n${YELLOW}[3/8] Checking SSL certificates...${NC}"
if [ -f "docker/nginx/ssl/fullchain.pem" ] && [ -f "docker/nginx/ssl/privkey.pem" ]; then
    echo -e "  ${GREEN}${NC} SSL certificates found"
    
    # Check certificate expiry
    if command -v openssl &> /dev/null; then
        expiry=$(openssl x509 -in docker/nginx/ssl/fullchain.pem -noout -enddate 2>/dev/null | cut -d= -f2)
        echo -e "  ${GREEN}${NC} Certificate expires: $expiry"
    fi
else
    echo -e "  ${YELLOW}${NC} SSL certificates not found"
    echo -e "  ${YELLOW}${NC} Run: openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout docker/nginx/ssl/privkey.pem -out docker/nginx/ssl/fullchain.pem"
fi

# Check 4: Docker availability
echo -e "\n${YELLOW}[4/8] Checking Docker...${NC}"
if command -v docker &> /dev/null; then
    docker_version=$(docker --version)
    echo -e "  ${GREEN}${NC} $docker_version"
    
    if docker info &> /dev/null; then
        echo -e "  ${GREEN}${NC} Docker daemon running"
    else
        echo -e "  ${RED}${NC} Docker daemon not running"
        exit 1
    fi
else
    echo -e "  ${RED}${NC} Docker not installed"
    exit 1
fi

# Check 5: Docker Compose availability
echo -e "\n${YELLOW}[5/8] Checking Docker Compose...${NC}"
if command -v docker-compose &> /dev/null; then
    compose_version=$(docker-compose --version)
    echo -e "  ${GREEN}${NC} $compose_version"
else
    echo -e "  ${RED}${NC} Docker Compose not installed"
    exit 1
fi

# Check 6: Port availability
echo -e "\n${YELLOW}[6/8] Checking port availability...${NC}"
ports=(80 443 3306 6379 9090 3001 8000)
for port in "${ports[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "  ${YELLOW}${NC} Port $port in use"
    else
        echo -e "  ${GREEN}${NC} Port $port available"
    fi
done

# Check 7: Disk space
echo -e "\n${YELLOW}[7/8] Checking disk space...${NC}"
if command -v df &> /dev/null; then
    available=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$available" -gt 10 ]; then
        echo -e "  ${GREEN}${NC} Sufficient disk space: ${available}GB available"
    else
        echo -e "  ${YELLOW}${NC} Low disk space: ${available}GB available (10GB+ recommended)"
    fi
fi

# Check 8: Configuration syntax
echo -e "\n${YELLOW}[8/8] Validating configuration syntax...${NC}"

# Validate docker-compose syntax
if docker-compose -f docker-compose.prod.yml config &> /dev/null; then
    echo -e "  ${GREEN}${NC} docker-compose.prod.yml syntax valid"
else
    echo -e "  ${RED}${NC} docker-compose.prod.yml syntax errors"
    docker-compose -f docker-compose.prod.yml config
    exit 1
fi

# Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Validation Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "Next steps:"
echo -e "1. Review and update .env with production values"
echo -e "2. Set up SSL certificates (if using self-signed)"
echo -e "3. Run: docker-compose -f docker-compose.prod.yml build"
echo -e "4. Run: docker-compose -f docker-compose.prod.yml up -d"
echo -e "5. Check: docker-compose -f docker-compose.prod.yml ps"
echo -e "\nSee DEPLOYMENT.md for detailed instructions."

# Deployment Guide

## Pet Adoption Platform - Production Deployment

This guide provides step-by-step instructions for deploying the Pet Adoption Platform to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [SSL Certificate Setup](#ssl-certificate-setup)
4. [Database Migration](#database-migration)
5. [Deployment](#deployment)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Monitoring](#monitoring)
8. [Backup and Recovery](#backup-and-recovery)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum (8GB recommended)
- 20GB disk space
- Ubuntu 20.04+ or similar Linux distribution

### Required Access

- SSH access to production server
- AWS account with S3 access
- Domain name with DNS control
- SSL certificate (Let's Encrypt recommended)

## Environment Setup

### 1. Clone Repository

`ash
git clone https://github.com/yourusername/pet-adoption-platform.git
cd pet-adoption-platform
`

### 2. Configure Environment Variables

Copy the production environment template:

`ash
cp .env.production .env
`

Edit .env and update all variables:

`ash
# CRITICAL: Change these values!
MYSQL_ROOT_PASSWORD=your_strong_root_password_here
MYSQL_PASSWORD=your_strong_user_password_here
JWT_SECRET_KEY=your_64_character_random_string
GRAFANA_ADMIN_PASSWORD=your_grafana_password

# Update with your domain
CORS_ORIGINS=https://yourdomain.com

# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=your-bucket-name

# Sentry (optional)
SENTRY_DSN=your_sentry_dsn
`

### 3. Generate Secrets

Generate secure random strings for secrets:

`ash
# JWT Secret (64 characters)
openssl rand -base64 48

# MySQL passwords (32 characters)
openssl rand -base64 24
`

## SSL Certificate Setup

### Option 1: Let's Encrypt (Recommended)

1. Install Certbot:

`ash
sudo apt install certbot
`

2. Obtain certificate:

`ash
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
`

3. Copy certificates to project:

`ash
sudo mkdir -p docker/nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem docker/nginx/ssl/
`

4. Set up automatic renewal:

`ash
sudo crontab -e
# Add this line:
0 3 * * * certbot renew --quiet --post-hook "docker restart pet-adoption-nginx"
`

### Option 2: Self-Signed Certificate (Development Only)

`ash
mkdir -p docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/privkey.pem \
  -out docker/nginx/ssl/fullchain.pem \
  -subj "/CN=localhost"
`

## Database Migration

### 1. Build Backend Image

`ash
docker-compose -f docker-compose.prod.yml build backend
`

### 2. Run Migrations

`ash
docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
`

### 3. Seed Initial Data (Optional)

`ash
docker-compose -f docker-compose.prod.yml run --rm backend python -m seeds.dev_data
`

## Deployment

### 1. Build All Images

`ash
docker-compose -f docker-compose.prod.yml build
`

### 2. Start Services

`ash
docker-compose -f docker-compose.prod.yml up -d
`

### 3. Check Service Status

`ash
docker-compose -f docker-compose.prod.yml ps
`

All services should show "Up" status.

## Post-Deployment Verification

### 1. Health Checks

`ash
# API Health
curl https://yourdomain.com/api/v1/health

# Expected response:
# {"status":"healthy","database":"connected","redis":"connected"}
`

### 2. Verify Services

`ash
# Check logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Check database connection
docker exec pet-adoption-mysql mysql -u pet_user -p -e "SHOW DATABASES;"

# Check Redis
docker exec pet-adoption-redis redis-cli ping
`

### 3. Access Monitoring

- **Prometheus**: http://yourdomain.com:9090
- **Grafana**: http://yourdomain.com:3001
  - Default login: admin / (your GRAFANA_ADMIN_PASSWORD)

## Monitoring

### Grafana Dashboard Setup

1. Login to Grafana (http://yourdomain.com:3001)
2. Navigate to Dashboards
3. Import pre-configured dashboards from docker/grafana/dashboards/

### Key Metrics to Monitor

- **API Response Time**: Should be < 500ms for 95th percentile
- **Error Rate**: Should be < 1%
- **Database Connections**: Should be < 80% of max
- **Memory Usage**: Should be < 80% of allocated
- **CPU Usage**: Should be < 70% average

### Alert Configuration

Alerts are configured in docker/prometheus/alert_rules.yml. Check Prometheus alerts:

`ash
# View active alerts
curl http://localhost:9090/api/v1/alerts
`

## Backup and Recovery

### Automated Backups

Set up daily automated backups using cron:

`ash
# Make scripts executable
chmod +x backups/backup.sh backups/restore.sh

# Add to crontab
crontab -e
# Add this line for daily backup at 2 AM:
0 2 * * * cd /path/to/pet-adoption-platform && ./backups/backup.sh
`

### Manual Backup

`ash
./backups/backup.sh
`

Backups are stored in ackups/mysql/ and optionally uploaded to S3.

### Restore from Backup

`ash
# List available backups
ls -lh backups/mysql/

# Restore specific backup
./backups/restore.sh backups/mysql/mysql_20250106_020000.sql.gz
`

### Backup Verification

Test backup restoration monthly:

`ash
# Create test database
docker exec pet-adoption-mysql mysql -u root -p -e "CREATE DATABASE pet_adoption_test;"

# Restore to test database
gunzip -c backups/mysql/mysql_latest.sql.gz | \
  docker exec -i pet-adoption-mysql mysql -u root -p pet_adoption_test

# Verify data
docker exec pet-adoption-mysql mysql -u root -p pet_adoption_test -e "SHOW TABLES;"
`

## Troubleshooting

### Service Won't Start

`ash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Check specific service
docker logs pet-adoption-api

# Restart service
docker-compose -f docker-compose.prod.yml restart backend
`

### Database Connection Issues

`ash
# Check MySQL is running
docker exec pet-adoption-mysql mysqladmin ping -u root -p

# Check connection from backend
docker exec pet-adoption-api python -c "from app.database import engine; print(engine)"

# Reset database connection
docker-compose -f docker-compose.prod.yml restart mysql backend
`

### High Memory Usage

`ash
# Check container resource usage
docker stats

# Reduce backend replicas
docker-compose -f docker-compose.prod.yml up -d --scale backend=1

# Clear Redis cache
docker exec pet-adoption-redis redis-cli FLUSHALL
`

### SSL Certificate Issues

`ash
# Check certificate expiry
openssl x509 -in docker/nginx/ssl/fullchain.pem -noout -dates

# Renew Let's Encrypt certificate
sudo certbot renew --force-renewal

# Restart Nginx
docker restart pet-adoption-nginx
`

### Slow API Response

1. Check database query performance:
`ash
docker exec pet-adoption-mysql mysql -u root -p -e "SHOW PROCESSLIST;"
`

2. Check Redis connection:
`ash
docker exec pet-adoption-redis redis-cli INFO stats
`

3. Review Grafana metrics for bottlenecks

### High Error Rate

1. Check application logs:
`ash
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
`

2. Check Sentry for error details (if configured)

3. Review Prometheus alerts

## Scaling

### Horizontal Scaling

Increase backend replicas:

`ash
# Scale to 4 replicas
docker-compose -f docker-compose.prod.yml up -d --scale backend=4

# Verify
docker-compose -f docker-compose.prod.yml ps backend
`

### Database Optimization

`ash
# Analyze tables
docker exec pet-adoption-mysql mysql -u root -p pet_adoption -e "ANALYZE TABLE pets, users;"

# Optimize tables
docker exec pet-adoption-mysql mysql -u root -p pet_adoption -e "OPTIMIZE TABLE pets, users;"
`

## Security Checklist

- [ ] All passwords changed from defaults
- [ ] SSL certificate installed and valid
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] SSH key authentication enabled, password auth disabled
- [ ] Regular security updates scheduled
- [ ] Database backups automated and tested
- [ ] Monitoring and alerting configured
- [ ] CORS origins restricted to your domain
- [ ] Rate limiting enabled
- [ ] Environment variables secured

## Maintenance

### Weekly Tasks

- Review monitoring dashboards
- Check disk space usage
- Review error logs
- Verify backup success

### Monthly Tasks

- Test backup restoration
- Update dependencies
- Security audit
- Performance review

### Quarterly Tasks

- SSL certificate renewal check
- Disaster recovery drill
- Capacity planning review

## Support

For issues or questions:

- Check logs: docker-compose -f docker-compose.prod.yml logs
- Review monitoring: Grafana dashboards
- Contact: devops@yourdomain.com

## Version History

- v1.0 (2025-11-06): Initial production deployment guide

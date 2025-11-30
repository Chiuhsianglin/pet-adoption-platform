# Docker Configuration

This directory contains production-ready Docker configurations for the Pet Adoption Platform.

## Directory Structure

`
docker/
 nginx/              # Nginx reverse proxy configuration
    nginx.conf     # Main Nginx config with SSL, security, rate limiting
    ssl/           # SSL certificates (create and place certs here)
 mysql/
    conf.d/
        my.cnf     # MySQL performance tuning configuration
 redis/
    redis.conf     # Redis persistence and memory management config
 prometheus/
    prometheus.yml # Metrics collection configuration
    alert_rules.yml # Alert rules for system monitoring
 grafana/
     provisioning/
        datasources/ # Grafana datasource configs
        dashboards/  # Dashboard provisioning
     dashboards/      # Pre-built dashboard JSON files (add here)
`

## Quick Start

### 1. SSL Certificate Setup

Before deploying, set up SSL certificates:

**Option A: Let's Encrypt (Production)**
`ash
# Install certbot
sudo apt install certbot

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy to docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem docker/nginx/ssl/
`

**Option B: Self-Signed (Development)**
`ash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/CN=localhost"
`

### 2. Configuration Files

All configuration files are pre-configured for production use:

- **Nginx**: SSL A+ grade, HTTP/2, rate limiting, WebSocket support
- **MySQL**: Performance tuned for 1GB buffer pool, binary logging enabled
- **Redis**: AOF persistence, 256MB memory limit, LRU eviction policy
- **Prometheus**: 15s scrape interval, 30-day retention
- **Grafana**: Auto-provisioned with Prometheus datasource

### 3. Customization

Edit configurations as needed:

- **nginx/nginx.conf**: Change server_name from _ to your domain
- **mysql/conf.d/my.cnf**: Adjust innodb_buffer_pool_size based on RAM
- **redis/redis.conf**: Modify maxmemory based on requirements
- **prometheus/prometheus.yml**: Add custom scrape targets
- **prometheus/alert_rules.yml**: Customize alert thresholds

## Monitoring Stack

### Prometheus
- **Port**: 9090
- **Metrics**: HTTP requests, response times, database connections, Redis stats
- **Alerts**: API down, high error rate, database issues, memory/CPU usage

### Grafana
- **Port**: 3001
- **Default Login**: admin / (set via GRAFANA_ADMIN_PASSWORD)
- **Datasource**: Pre-configured Prometheus connection
- **Dashboards**: Import from grafana/dashboards/ directory

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| http_requests_total | Total HTTP requests | - |
| http_request_duration_seconds | Request duration | P95 > 1s |
| http_requests_in_progress | Active requests | - |
| database_connections | MySQL connections | > 80% max |
| edis_memory_used_bytes | Redis memory | > 90% max |

## Security Features

### Nginx Security Headers
- Strict-Transport-Security: 2-year HSTS with subdomains
- X-Frame-Options: Prevent clickjacking
- X-Content-Type-Options: Prevent MIME sniffing
- X-XSS-Protection: Enable XSS filter
- Content-Security-Policy: Restrict resource loading
- Referrer-Policy: Control referrer information

### Rate Limiting
- API endpoints: 10 requests/second per IP
- Burst: 20 requests
- WebSocket: No rate limit

### SSL/TLS Configuration
- Protocols: TLSv1.2, TLSv1.3
- Ciphers: Modern cipher suite (ECDHE-ECDSA, ECDHE-RSA)
- Session tickets: Disabled for forward secrecy

## Resource Limits

### Backend (per replica)
- CPU: 0.5-1.0 cores
- Memory: 512MB-1GB

### MySQL
- CPU: 1.0-2.0 cores
- Memory: 1GB-2GB

### Redis
- CPU: 0.25-0.5 cores
- Memory: 256MB-512MB

### Prometheus
- CPU: 0.5 cores
- Memory: 512MB

### Grafana
- CPU: 0.5 cores
- Memory: 512MB

## Health Checks

All services include health checks:

- **Nginx**: HTTP GET /health every 30s
- **Backend**: Curl localhost:8000/api/v1/health every 30s
- **MySQL**: mysqladmin ping every 10s
- **Redis**: redis-cli ping every 10s

## Logging

All services use JSON logging with rotation:

- **Max size**: 10MB (backend/MySQL), 5MB (Redis)
- **Max files**: 3 (30MB total per service)
- **Driver**: json-file

Access logs via:
`ash
docker-compose -f docker-compose.prod.yml logs -f [service]
`

## Volumes

Persistent volumes for data retention:

- mysql_data: Database files
- edis_data: Redis persistence files  
- prometheus_data: Metrics storage (30 days)
- grafana_data: Dashboards and settings

## Networking

Custom bridge network pet-adoption-network:
- Subnet: 172.20.0.0/16
- Isolated from host network
- Service discovery via container names

## Backup Integration

Backup scripts in ../backups/ can access:
- MySQL data: /backups volume mount in mysql container
- Configuration: Read-only mounts for all configs

## Troubleshooting

### Check Service Status
`ash
docker-compose -f docker-compose.prod.yml ps
`

### View Logs
`ash
docker-compose -f docker-compose.prod.yml logs -f backend
`

### Restart Service
`ash
docker-compose -f docker-compose.prod.yml restart nginx
`

### Check Metrics
`ash
curl http://localhost:9090/api/v1/query?query=up
`

## Further Reading

- Main deployment guide: ../DEPLOYMENT.md
- Backup procedures: ../backups/README.md
- Environment variables: ../.env.production

## Support

For configuration issues:
1. Check service logs
2. Review Prometheus alerts
3. Verify Grafana dashboards
4. Consult DEPLOYMENT.md troubleshooting section

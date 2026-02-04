# HDCP Platform Deployment Guide

This guide covers deploying the HDCP Platform to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Cloud Provider Deployment](#cloud-provider-deployment)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Database Setup](#database-setup)
8. [Monitoring Setup](#monitoring-setup)
9. [Backup Strategy](#backup-strategy)
10. [Security Checklist](#security-checklist)
11. [Performance Optimization](#performance-optimization)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **CPU:** 2+ cores (4+ recommended)
- **Memory:** 4GB+ RAM (8GB+ recommended)
- **Storage:** 50GB+ SSD (100GB+ recommended)
- **OS:** Linux (Ubuntu 20.04+, CentOS 8+) or Docker-compatible platform

### Software Requirements

- **Docker 20.10+**
- **Docker Compose 2.0+**
- **Git**
- **Nginx** (for reverse proxy)
- **Certbot** (for SSL certificates)

---

## Environment Setup

### 1. Production Environment Variables

```bash
# Copy production environment template
cp examples/production.env .env

# Edit with your values
nano .env
```

Key settings to update:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@prod-db:5432/hdcp_db
POSTGRES_PASSWORD=secure_random_password

# Redis
REDIS_URL=redis://prod-redis:6379/0

# Security (GENERATE NEW VALUES!)
SECRET_KEY=your-super-secret-key-minimum-32-characters
JWT_SECRET=your-jwt-secret-minimum-32-characters

# Scenario
ACTIVE_SCENARIO=stock

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Monitoring
ENABLE_METRICS=true
```

### 2. Generate Secure Keys

```bash
# Generate secret key
python -c 'import secrets; print(secrets.token_urlsafe(32))'

# Generate JWT secret
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

### 3. Configure Firewall

```bash
# Ubuntu/Debian
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## Docker Deployment

### Option 1: Docker Compose (Recommended)

#### 1. Create Production Compose File

```bash
# Copy production compose template
cp examples/docker-compose.prod.yml docker-compose.yml
```

**Production Compose Configuration (`docker-compose.yml`):**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - hdcp-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - hdcp-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  api:
    build:
      context: ./apps/api
      dockerfile: Dockerfile.prod
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      SECRET_KEY: ${SECRET_KEY}
      ENVIRONMENT: production
      DEBUG: false
    depends_on:
      - postgres
      - redis
    networks:
      - hdcp-network
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  web:
    build:
      context: ./apps/web
      dockerfile: Dockerfile.prod
    environment:
      NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL}
    depends_on:
      - api
    networks:
      - hdcp-network
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  cms:
    build:
      context: ./apps/cms
      dockerfile: Dockerfile.prod
    environment:
      DATABASE_CLIENT: postgres
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      DATABASE_NAME: ${POSTGRES_DB}
      DATABASE_USERNAME: ${POSTGRES_USER}
      DATABASE_PASSWORD: ${POSTGRES_PASSWORD}
      JWT_SECRET: ${JWT_SECRET}
      NODE_ENV: production
    depends_on:
      - postgres
    networks:
      - hdcp-network
    restart: unless-stopped
    deploy:
      replicas: 1
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./logs:/var/log/nginx
    depends_on:
      - web
      - api
      - cms
    networks:
      - hdcp-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  hdcp-network:
    driver: bridge
```

#### 2. Build and Deploy

```bash
# Build images
docker-compose build --no-cache

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

#### 3. Initialize Database

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Or manually create tables
docker-compose exec api python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

---

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl create namespace hdcp-platform
```

### 2. Create Secrets

```bash
# Create secret for database password
kubectl create secret generic db-password \
  --from-literal=password=your_secure_password \
  -n hdcp-platform

# Create secret for API keys
kubectl create secret generic api-secrets \
  --from-literal=secret-key=your_secret_key \
  --from-literal=jwt-secret=your_jwt_secret \
  -n hdcp-platform
```

### 3. Deploy PostgreSQL

```yaml
# postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: hdcp-platform
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: "hdcp_db"
        - name: POSTGRES_USER
          value: "hdcp_user"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-password
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: hdcp-platform
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

### 4. Deploy API

```yaml
# api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: hdcp-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: your-registry/hdcp-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql+asyncpg://hdcp_user:$(DB_PASSWORD)@postgres:5432/hdcp_db"
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: secret-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: hdcp-platform
spec:
  selector:
    app: api
  ports:
  - port: 8000
    targetPort: 8000
```

### 5. Deploy Frontend

```yaml
# web.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: hdcp-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: your-registry/hdcp-web:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.yourdomain.com"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "250m"
```

### 6. Deploy Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hdcp-ingress
  namespace: hdcp-platform
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - yourdomain.com
    - www.yourdomain.com
    secretName: hdcp-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 3000
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 8000
```

### 7. Apply Manifests

```bash
# Apply all manifests
kubectl apply -f examples/k8s/

# Check status
kubectl get all -n hdcp-platform
```

---

## Cloud Provider Deployment

### AWS (ECS)

1. **Create ECS Cluster**

```bash
aws ecs create-cluster --cluster-name hdcp-platform
```

2. **Create Task Definitions**

```json
{
  "family": "hdcp-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "your-account.dkr.ecr.region.amazonaws.com/hdcp-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql+asyncpg://..."
        }
      ]
    }
  ]
}
```

3. **Create Services**

```bash
aws ecs create-service \
  --cluster hdcp-platform \
  --service-name api-service \
  --task-definition hdcp-api \
  --desired-count 2
```

### Google Cloud (GKE)

1. **Create Cluster**

```bash
gcloud container clusters create hdcp-platform \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2
```

2. **Deploy**

```bash
kubectl apply -f examples/k8s/
```

### Azure (AKS)

1. **Create Resource Group**

```bash
az group create --name hdcp-rg --location eastus
```

2. **Create Cluster**

```bash
az aks create \
  --resource-group hdcp-rg \
  --name hdcp-cluster \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3
```

3. **Deploy**

```bash
kubectl apply -f examples/k8s/
```

---

## SSL/TLS Configuration

### Using Nginx

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    upstream web {
        server web:3000;
    }

    upstream cms {
        server cms:1337;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # SSL Configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security Headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # Frontend
        location / {
            proxy_pass http://web;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        # API
        location /api/ {
            proxy_pass http://api/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        # GraphQL
        location /graphql {
            proxy_pass http://api/graphql;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # CMS
        location /cms {
            proxy_pass http://cms;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Logs
        access_log /var/log/nginx/access.log;
        error_log /var/log/nginx/error.log;
    }
}
```

### Using Certbot for SSL Certificates

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## Database Setup

### PostgreSQL Configuration

```sql
-- postgresql.conf
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Create Database and User

```sql
CREATE DATABASE hdcp_db;
CREATE USER hdcp_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE hdcp_db TO hdcp_user;
```

### Run Migrations

```bash
# Using Docker
docker-compose exec api alembic upgrade head

# Locally
cd apps/api
alembic upgrade head
```

---

## Monitoring Setup

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'hdcp-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

### Grafana Dashboard

Import the HDCP Platform dashboard from `examples/grafana/`.

### Health Checks

```bash
# API health
curl -f https://api.yourdomain.com/health

# Frontend health
curl -f https://yourdomain.com/health

# Database health
docker-compose exec postgres pg_isready -U hdcp_user
```

---

## Backup Strategy

### Database Backup

```bash
# Automated backup script
#!/bin/bash
# backup-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="hdcp_db"

# Create backup
docker-compose exec -T postgres pg_dump -U hdcp_user $DB_NAME | \
  gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.sql.gz s3://your-backup-bucket/
```

### Redis Backup

```bash
# Redis backup
docker-compose exec redis redis-cli BGSAVE
```

### Schedule Backups

```bash
# Add to crontab
crontab -e

# Backup database daily at 2 AM
0 2 * * * /path/to/backup-db.sh

# Backup Redis daily at 3 AM
0 3 * * * docker-compose exec redis redis-cli BGSAVE
```

---

## Security Checklist

### ✅ Must Do

- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY and JWT_SECRET
- [ ] Enable SSL/TLS
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Set up database backups
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Enable security headers
- [ ] Update all dependencies
- [ ] Disable DEBUG mode
- [ ] Set up monitoring and alerting
- [ ] Configure log retention
- [ ] Use HTTPS only
- [ ] Set up WAF (Web Application Firewall)

### Optional Enhancements

- [ ] Implement API authentication
- [ ] Enable request signing
- [ ] Use secret management service (AWS Secrets Manager, HashiCorp Vault)
- [ ] Enable database encryption at rest
- [ ] Implement network segmentation
- [ ] Use security scanning (SAST/DAST)
- [ ] Enable audit logging
- [ ] Set up intrusion detection

---

## Performance Optimization

### API Optimization

1. **Enable Caching**

```python
# apps/api/app/config/settings.py
CACHE_TTL = 3600  # 1 hour
ENABLE_CACHE = True
```

2. **Database Indexing**

```sql
-- Add indexes for frequently queried columns
CREATE INDEX CONCURRENTLY idx_stock_symbol_timestamp ON stock_prices(symbol, timestamp DESC);
CREATE INDEX CONCURRENTLY idx_sensor_id_timestamp ON sensor_readings(sensor_id, timestamp DESC);
```

3. **Connection Pooling**

```python
# apps/api/app/config/settings.py
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 30
DB_POOL_TIMEOUT = 30
```

### Frontend Optimization

1. **Enable Compression**

```nginx
# nginx.conf
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

2. **CDN Configuration**

```nginx
# Serve static assets from CDN
location /_next/static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Database Optimization

1. **Query Optimization**

```sql
-- Analyze slow queries
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

2. **Connection Pooling**

```python
# PostgreSQL connection pool
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600
)
```

---

## Troubleshooting

### Common Issues

#### Issue: API Returns 502 Bad Gateway

**Solution:**
```bash
# Check API logs
docker-compose logs api

# Check if API is running
docker-compose exec api curl -f http://localhost:8000/health

# Restart API service
docker-compose restart api
```

#### Issue: Database Connection Failed

**Solution:**
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready -U hdcp_user

# Check database logs
docker-compose logs postgres

# Verify credentials
docker-compose exec postgres psql -U hdcp_user -d hdcp_db -c "SELECT 1;"
```

#### Issue: Frontend Can't Connect to API

**Solution:**
```bash
# Check API URL in frontend
docker-compose exec web env | grep NEXT_PUBLIC_API_URL

# Test API from frontend container
docker-compose exec web curl -f http://api:8000/health

# Update .env if needed
```

#### Issue: SSL Certificate Error

**Solution:**
```bash
# Check certificate validity
openssl x509 -in /etc/nginx/ssl/fullchain.pem -text -noout

# Renew certificate
sudo certbot renew

# Restart nginx
docker-compose restart nginx
```

### Monitoring Commands

```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f [service]

# Check resource usage
docker stats

# Check disk usage
df -h

# Check memory usage
free -h

# Check network connections
netstat -tuln

# Monitor API metrics
curl http://localhost:8000/metrics
```

### Performance Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API endpoint
ab -n 1000 -c 10 http://localhost:8000/api/v1/stocks/AAPL

# Test with curl
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
```

---

## Support

- 📚 [Documentation](README.md)
- 🐛 [GitHub Issues](https://github.com/your-org/hdcp-template/issues)
- 💬 [GitHub Discussions](https://github.com/your-org/hdcp-template/discussions)
- 📧 Email: support@yourdomain.com

---

**Deployment Complete! 🚀**

For production deployments, consider:
1. Load balancing
2. Auto-scaling
3. Disaster recovery
4. Multi-region deployment
5. Continuous integration/deployment (CI/CD)

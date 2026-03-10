---
id: playwright-deployment
title: Playwright Deployment
sidebar_label: Playwright Deployment
slug: /playwright-deployment
---

# Playwright MCP Server Deployment Guide

This guide provides comprehensive instructions for deploying and managing the Playwright MCP Server within the Chronos AI infrastructure.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Deployment Methods](#deployment-methods)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)
8. [Performance Optimization](#performance-optimization)
9. [Security Considerations](#security-considerations)

## Overview

The Playwright MCP Server provides browser automation capabilities to the Chronos AI agent system. It includes:

- **Browser Management**: Automated browser lifecycle management with pooling
- **Task Execution**: Asynchronous execution of browser automation tasks
- **Artifact Storage**: Secure storage of screenshots, videos, and other outputs
- **Health Monitoring**: Real-time monitoring and alerting
- **Resource Optimization**: Efficient resource utilization and scaling

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows 10+
- **Memory**: Minimum 4GB RAM, 8GB+ recommended
- **CPU**: 2+ cores, 4+ cores recommended
- **Storage**: 10GB+ free space for browser binaries and artifacts
- **Network**: Stable internet connection for downloads

### Software Dependencies

- **Docker**: 20.10+ and Docker Compose 2.0+
- **Python**: 3.8+ (for local development)
- **Node.js**: 16+ (for Playwright browser installation)
- **Redis**: 6.0+ (for caching and task queue)
- **PostgreSQL**: 12+ (for metadata storage)

### Browser Dependencies

The Playwright server supports three browser engines:

1. **Chromium**: Google's Chrome browser (default)
2. **Firefox**: Mozilla Firefox
3. **WebKit**: Apple's Safari engine (macOS/Linux only)

Each browser requires specific system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2

# CentOS/RHEL
sudo yum install -y \
    nss \
    atk \
    at-spi2-atk \
    cups-libs \
    libdrm \
    gtk3 \
    libXcomposite \
    libXdamage \
    libXrandr \
    libgbm \
    alsa-lib
```

## Quick Start

### 1. Environment Setup

1. Copy the environment template:
   ```bash
   cp backend/.env.playwright.example backend/.env.playwright
   ```

2. Configure environment variables:
   ```bash
   # Edit the configuration
   nano backend/.env.playwright
   ```

### 2. Database Migration

1. Run the database migration:
   ```bash
   cd backend
   alembic upgrade head
   ```

2. Verify the migration:
   ```bash
   python -c "from app.models.playwright import *; print('Migration successful')"
   ```

### 3. Install Dependencies

1. Install Python dependencies:
   ```bash
   pip install -r backend/requirements-playwright.txt
   ```

2. Install Playwright browsers:
   ```bash
   playwright install chromium
   playwright install firefox
   playwright install webkit
   ```

### 4. Start Services

1. Using Docker Compose:
   ```bash
   docker-compose -f docker-compose.playwright.yml up -d
   ```

2. Verify services:
   ```bash
   curl http://localhost:8000/api/v1/playwright/health
   ```

## Configuration

### Environment Variables

The Playwright server uses the following environment variables:

#### Core Configuration

```bash
# Server Settings
PLAYWRIGHT_SERVER_HOST=0.0.0.0
PLAYWRIGHT_SERVER_PORT=8000
PLAYWRIGHT_DEBUG=false

# Database Configuration
PLAYWRIGHT_DATABASE_URL=postgresql://user:password@localhost/chronos_ai
PLAYWRIGHT_DATABASE_POOL_SIZE=10
PLAYWRIGHT_DATABASE_MAX_OVERFLOW=20

# Redis Configuration
PLAYWRIGHT_REDIS_URL=redis://localhost:6379/0
PLAYWRIGHT_REDIS_MAX_CONNECTIONS=20
```

#### Browser Configuration

```bash
# Browser Pool Settings
PLAYWRIGHT_MAX_CONCURRENT_SESSIONS=10
PLAYWRIGHT_BROWSER_TIMEOUT=30000
PLAYWRIGHT_PAGE_TIMEOUT=30000
PLAYWRIGHT_BROWSER_LIFETIME=3600

# Browser Options
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_SLOW_MO=0
PLAYWRIGHT_VIEWPORT_WIDTH=1920
PLAYWRIGHT_VIEWPORT_HEIGHT=1080
```

#### Security Configuration

```bash
# Security Settings
PLAYWRIGHT_MAX_SCREENSHOT_SIZE=10485760
PLAYWRIGHT_MAX_VIDEO_SIZE=104857600
PLAYWRIGHT_ALLOWED_DOMAINS=*
PLAYWRIGHT_BLOCKED_DOMAINS=*.local,*.internal

# Authentication
PLAYWRIGHT_API_KEY=your-secure-api-key
PLAYWRIGHT_JWT_SECRET=your-jwt-secret
```

#### Monitoring Configuration

```bash
# Monitoring Settings
PLAYWRIGHT_METRICS_ENABLED=true
PLAYWRIGHT_LOG_LEVEL=INFO
PLAYWRIGHT_HEALTH_CHECK_INTERVAL=30
PLAYWRIGHT_CLEANUP_INTERVAL=300
```

### Configuration Files

#### Playwright Configuration (`backend/config/playwright.toml`)

```toml
[server]
host = "0.0.0.0"
port = 8000
workers = 4

[database]
url = "postgresql://user:password@localhost/chronos_ai"
pool_size = 10
max_overflow = 20

[redis]
url = "redis://localhost:6379/0"
max_connections = 20

[browser]
max_concurrent_sessions = 10
headless = true
timeout = 30000
lifetime = 3600

[security]
max_screenshot_size = 10485760
max_video_size = 104857600
allowed_domains = ["*"]
blocked_domains = ["*.local", "*.internal"]

[monitoring]
metrics_enabled = true
log_level = "INFO"
health_check_interval = 30
```

#### MCP Server Configuration (`backend/config/mcp-servers-playwright.json`)

```json
{
  "playwright": {
    "name": "Playwright MCP Server",
    "version": "1.0.0",
    "description": "Browser automation and testing server",
    "host": "localhost",
    "port": 8000,
    "protocol": "stdio",
    "transport": "stdio",
    "capabilities": [
      "browser_automation",
      "web_testing",
      "screenshot_capture",
      "pdf_generation",
      "web_scraping"
    ],
    "configuration": {
      "max_concurrent_sessions": 10,
      "browser_timeout": 30000,
      "headless_mode": true
    }
  }
}
```

## Deployment Methods

### Method 1: Docker Compose (Recommended)

1. **Production Deployment**:
   ```bash
   docker-compose -f docker-compose.playwright.yml up -d
   ```

2. **Development Deployment**:
   ```bash
   docker-compose -f docker-compose.playwright.dev.yml up -d
   ```

3. **With Browser Pool**:
   ```bash
   docker-compose -f docker-compose.playwright.pool.yml up -d
   ```

### Method 2: Kubernetes

1. **Apply Configurations**:
   ```bash
   kubectl apply -f k8s/
   ```

2. **Scale Deployment**:
   ```bash
   kubectl scale deployment playwright-server --replicas=3
   ```

### Method 3: Manual Installation

1. **Install System Dependencies**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y \
       python3 python3-pip python3-venv \
       docker.io docker-compose \
       redis-server postgresql
   ```

2. **Setup Python Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements-playwright.txt
   ```

3. **Install Playwright Browsers**:
   ```bash
   playwright install chromium
   playwright install-deps
   ```

4. **Start Services**:
   ```bash
   # Start Redis
   sudo systemctl start redis-server
   
   # Start PostgreSQL
   sudo systemctl start postgresql
   
   # Start Playwright Server (from repo root)
   python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
   ```

## Monitoring and Maintenance

### Health Monitoring

1. **Check Service Health**:
   ```bash
   ./backend/scripts/monitor_playwright.sh status
   ```

2. **View Metrics**:
   ```bash
   ./backend/scripts/monitor_playwright.sh metrics
   ```

3. **Monitor Logs**:
   ```bash
   tail -f backend/logs/playwright_monitor.log
   ```

### Performance Monitoring

1. **Monitor Resource Usage**:
   ```bash
   # CPU and Memory
   htop
   
   # Disk Usage
   df -h
   
   # Network
   netstat -tulpn | grep 8000
   ```

2. **Monitor Browser Sessions**:
   ```bash
   curl http://localhost:8000/api/v1/playwright/sessions
   ```

3. **Monitor Task Queue**:
   ```bash
   redis-cli llen "playwright:queue"
   ```

### Maintenance Tasks

1. **Cleanup Old Artifacts**:
   ```bash
   find backend/artifacts -type f -mtime +7 -delete
   ```

2. **Database Maintenance**:
   ```bash
   # Clean up old sessions
   python scripts/cleanup_sessions.py
   
   # Optimize database
   VACUUM ANALYZE playwright_sessions;
   ```

3. **Browser Updates**:
   ```bash
   playwright install chromium --force
   playwright install firefox --force
   ```

### Automated Monitoring

1. **Start Monitoring Service**:
   ```bash
   ./backend/scripts/monitor_playwright.sh start
   ```

2. **Setup Cron Jobs**:
   ```bash
   # Add to crontab
   0 */6 * * * /path/to/backend/scripts/monitor_playwright.sh restart
   0 2 * * 0 /path/to/backend/scripts/cleanup_artifacts.sh
   ```

## Troubleshooting

### Common Issues

#### 1. Browser Installation Failed

**Problem**: Playwright browser installation fails

**Solution**:
```bash
# Update system packages
sudo apt-get update

# Install missing dependencies
sudo apt-get install -y \
    libnss3-dev \
    libatk-bridge2.0-0-dev \
    libdrm2 \
    libxkbcommon0-dev \
    libxcomposite1-dev \
    libxdamage1-dev \
    libxrandr2-dev \
    libgbm1-dev \
    libasound2-dev

# Reinstall browsers
playwright install chromium --force
```

#### 2. Database Connection Error

**Problem**: Cannot connect to PostgreSQL database

**Solution**:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U user -d chronos_ai

# Verify environment variables
echo $PLAYWRIGHT_DATABASE_URL
```

#### 3. Redis Connection Error

**Problem**: Cannot connect to Redis

**Solution**:
```bash
# Check Redis status
sudo systemctl status redis-server

# Test connection
redis-cli ping

# Check configuration
redis-cli config get "*"
```

#### 4. Memory Issues

**Problem**: Server runs out of memory

**Solution**:
```bash
# Reduce concurrent sessions
export PLAYWRIGHT_MAX_CONCURRENT_SESSIONS=5

# Enable memory monitoring
export PLAYWRIGHT_MEMORY_MONITORING=true

# Restart with new settings
docker-compose -f docker-compose.playwright.yml restart
```

#### 5. Browser Hanging

**Problem**: Browser sessions become unresponsive

**Solution**:
```bash
# Check running browsers
ps aux | grep chromium

# Kill hanging processes
pkill -f chromium

# Restart service
./backend/scripts/deploy_playwright.sh restart
```

### Debugging

1. **Enable Debug Mode**:
   ```bash
   export PLAYWRIGHT_DEBUG=true
   export PLAYWRIGHT_LOG_LEVEL=DEBUG
   ```

2. **View Detailed Logs**:
   ```bash
   tail -f backend/logs/playwright_server.log
   ```

3. **Test Individual Components**:
   ```bash
   # Test browser
   python -c "
   from playwright.sync_api import sync_playwright
   with sync_playwright() as p:
       browser = p.chromium.launch()
       page = browser.new_page()
       page.goto('https://example.com')
       print('Browser test successful')
       browser.close()
   "
   ```

4. **Network Debugging**:
   ```bash
   # Monitor network traffic
   tcpdump -i any port 8000
   
   # Check proxy settings
   env | grep -i proxy
   ```

### Performance Issues

1. **High CPU Usage**:
   - Reduce concurrent sessions
   - Check for infinite loops in automation scripts
   - Monitor browser processes

2. **High Memory Usage**:
   - Increase garbage collection frequency
   - Reduce browser cache size
   - Monitor memory leaks

3. **Slow Response Times**:
   - Check network connectivity
   - Monitor database query performance
   - Review task queue size

## Performance Optimization

### Browser Optimization

1. **Reduce Memory Usage**:
   ```python
   browser = p.chromium.launch(
       headless=True,
       args=[
           '--no-sandbox',
           '--disable-dev-shm-usage',
           '--disable-extensions',
           '--disable-images',  # Disable image loading
           '--disable-javascript',  # Only if safe
           '--memory-pressure-off',
           '--max_old_space_size=4096'
       ]
   )
   ```

2. **Optimize Network Usage**:
   ```python
   context = browser.new_context(
       viewport={'width': 1920, 'height': 1080},
       user_agent='Mozilla/5.0 (compatible; Playwright-Bot)',
       ignore_https_errors=True
   )
   
   # Block unnecessary resources
   await page.route('**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}', 
                   lambda route: route.abort())
   ```

3. **Caching Strategy**:
   ```python
   # Enable caching
   context.set_default_timeout(30000)
   await page.set_cache_enabled(True)
   ```

### Database Optimization

1. **Index Optimization**:
   ```sql
   -- Add indexes for frequently queried columns
   CREATE INDEX idx_playwright_sessions_status ON playwright_sessions(status);
   CREATE INDEX idx_playwright_sessions_created_at ON playwright_sessions(created_at);
   CREATE INDEX idx_playwright_tasks_status ON playwright_tasks(status);
   ```

2. **Connection Pooling**:
   ```python
   engine = create_engine(
       DATABASE_URL,
       pool_size=10,
       max_overflow=20,
       pool_pre_ping=True,
       pool_recycle=3600
   )
   ```

### Caching Strategy

1. **Redis Caching**:
   ```python
   import redis
   r = redis.Redis(host='localhost', port=6379, db=0)
   
   # Cache browser configurations
   r.setex('browser_config:chromium', 3600, json.dumps(config))
   
   # Cache session data
   r.setex(f'session:{session_id}', 1800, session_data)
   ```

2. **Response Caching**:
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def get_browser_config(browser_type: str) -> dict:
       # Return cached configuration
       pass
   ```

### Scaling Considerations

1. **Horizontal Scaling**:
   - Use load balancer (nginx, HAProxy)
   - Implement session affinity
   - Share session data via Redis

2. **Vertical Scaling**:
   - Increase CPU cores
   - Add more RAM
   - Use SSD storage

3. **Resource Limits**:
   ```yaml
   # Docker Compose resource limits
   services:
     playwright-server:
       deploy:
         resources:
           limits:
             memory: 2G
             cpus: '2'
           reservations:
             memory: 1G
             cpus: '1'
   ```

## Security Considerations

### Authentication and Authorization

1. **API Key Authentication**:
   ```python
   from fastapi import Depends, HTTPException, status
   from fastapi.security import APIKeyHeader
   
   api_key_header = APIKeyHeader(name="X-API-Key")
   
   async def verify_api_key(api_key: str = Depends(api_key_header)):
       if api_key != settings.PLAYWRIGHT_API_KEY:
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Invalid API key"
           )
       return api_key
   ```

2. **JWT Token Validation**:
   ```python
   from jose import JWTError, jwt
   from datetime import datetime, timedelta
   
   def verify_jwt_token(token: str):
       try:
           payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
           return payload
       except JWTError:
           raise HTTPException(status_code=401, detail="Invalid token")
   ```

### Network Security

1. **HTTPS Configuration**:
   ```nginx
   server {
       listen 443 ssl;
       server_name playwright.example.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Firewall Rules**:
   ```bash
   # Allow only necessary ports
   ufw allow 22/tcp    # SSH
   ufw allow 80/tcp    # HTTP
   ufw allow 443/tcp   # HTTPS
   ufw allow 8000/tcp  # Playwright API
   ufw enable
   ```

### Content Security

1. **Domain Restrictions**:
   ```python
   ALLOWED_DOMAINS = [
       'example.com',
       'api.example.com'
   ]
   
   BLOCKED_DOMAINS = [
       'localhost',
       '127.0.0.1',
       '*.internal'
   ]
   ```

2. **Resource Limits**:
   ```python
   MAX_SCREENSHOT_SIZE = 10 * 1024 * 1024  # 10MB
   MAX_VIDEO_SIZE = 100 * 1024 * 1024     # 100MB
   MAX_TASK_DURATION = 300                 # 5 minutes
   ```

### Data Protection

1. **Sensitive Data Handling**:
   ```python
   # Encrypt sensitive data in database
   from cryptography.fernet import Fernet
   
   class EncryptedField:
       def __init__(self, key):
           self.fernet = Fernet(key)
       
       def encrypt(self, data: str) -> str:
           return self.fernet.encrypt(data.encode()).decode()
       
       def decrypt(self, encrypted_data: str) -> str:
           return self.fernet.decrypt(encrypted_data.encode()).decode()
   ```

2. **Secure Artifact Storage**:
   ```python
   # Generate secure URLs for artifacts
   import secrets
   import string
   
   def generate_secure_filename():
       alphabet = string.ascii_letters + string.digits
       return ''.join(secrets.choice(alphabet) for _ in range(32))
   
   # Store artifacts with secure names
   artifact_path = f"/secure/artifacts/{generate_secure_filename()}.png"
   ```

### Monitoring and Auditing

1. **Access Logging**:
   ```python
   import logging
   from datetime import datetime
   
   logger = logging.getLogger('playwright_access')
   
   def log_access(user_id: str, action: str, details: dict):
       logger.info({
           'timestamp': datetime.utcnow().isoformat(),
           'user_id': user_id,
           'action': action,
           'details': details,
           'ip_address': request.client.host
       })
   ```

2. **Security Alerts**:
   ```python
   def check_security_events():
       # Monitor for suspicious activities
       failed_attempts = get_failed_login_attempts()
       if failed_attempts > 10:
           send_security_alert("Multiple failed login attempts detected")
       
       # Check for unusual resource usage
       if get_memory_usage() > 90:
           send_security_alert("High memory usage detected")
   ```

### Compliance

1. **Data Retention Policies**:
   ```python
   # Automatically clean up old data
   def cleanup_old_data():
       # Delete sessions older than 30 days
       thirty_days_ago = datetime.utcnow() - timedelta(days=30)
       db.query(PlaywrightSession).filter(
           PlaywrightSession.created_at < thirty_days_ago
       ).delete()
       
       # Delete artifacts older than 7 days
       seven_days_ago = datetime.utcnow() - timedelta(days=7)
       cleanup_old_artifacts(seven_days_ago)
   ```

2. **GDPR Compliance**:
   ```python
   def anonymize_user_data(user_id: str):
       # Remove personal information while preserving analytics
       sessions = db.query(PlaywrightSession).filter_by(user_id=user_id)
       for session in sessions:
           session.user_ip = hash_ip(session.user_ip)
           session.user_agent = "Anonymized"
       
       db.commit()
   ```

---

## Conclusion

This deployment guide provides comprehensive instructions for deploying and managing the Playwright MCP Server. Follow the quick start section for immediate deployment, then refer to the detailed sections for production optimization and maintenance.

For additional support:

- **Documentation**: Check the `docs/` directory for detailed API documentation
- **Monitoring**: Use `./backend/scripts/monitor_playwright.sh` for system monitoring
- **Issues**: Report bugs and feature requests via the project issue tracker
- **Community**: Join the developer community for support and discussions

**Last Updated**: 2025-12-31
**Version**: 1.0.0

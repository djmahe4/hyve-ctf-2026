# Production Deployment Guide

Best practices and guidelines for deploying Hivye CTF 2026 in a production environment.

## Production Checklist

Before deploying to production, ensure you complete the following:

- [ ] Change all default passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test disaster recovery
- [ ] Review resource limits
- [ ] Set up logging
- [ ] Configure rate limiting
- [ ] Review security settings

## Security Hardening

### 1. Change Default Credentials

Edit `ctfd/docker-compose.yml` and change:
```yaml
environment:
  - MYSQL_ROOT_PASSWORD=YOUR_STRONG_PASSWORD_HERE
  - MYSQL_PASSWORD=YOUR_CTFD_PASSWORD_HERE
```

Edit `deployment/docker/docker-compose.challenges.yml` and update flag values:
```yaml
environment:
  - FLAG_SQL_INJECTION=YOUR_CUSTOM_FLAG_1
  - FLAG_COOKIE_MANIP=YOUR_CUSTOM_FLAG_2
  - FLAG_XSS=YOUR_CUSTOM_FLAG_3
  - FLAG_IDOR=YOUR_CUSTOM_FLAG_4
```

### 2. Enable HTTPS

Install nginx as reverse proxy with SSL:

```bash
# Install nginx and certbot
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Create nginx configuration
sudo nano /etc/nginx/sites-available/ctfd
```

Example nginx configuration:
```nginx
server {
    listen 80;
    server_name ctf.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ctf.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/ctf.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ctf.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/ctfd /etc/nginx/sites-enabled/

# Obtain SSL certificate
sudo certbot --nginx -d ctf.yourdomain.com

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### 3. Firewall Configuration

Configure UFW (Uncomplicated Firewall):
```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Block direct access to Docker ports (if using nginx)
sudo ufw deny 8000/tcp
sudo ufw deny 8080/tcp
sudo ufw deny 8081/tcp

# Check status
sudo ufw status
```

### 4. Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  ctfd:
    # ... existing configuration ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  db:
    # ... existing configuration ...
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Monitoring

### Docker Stats
Monitor container resource usage:
```bash
# Real-time stats
docker stats

# Or for specific containers
docker stats ctfd-ctfd-1 ctfd-db-1 ctfd-cache-1
```

### Prometheus + Grafana (Optional)

Add monitoring stack:
```yaml
# Add to ctfd/docker-compose.yml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    networks:
      - ctfd_network

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    networks:
      - ctfd_network
```

## Backup Strategy

### Database Backup

Create automated backup script:
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/ctfd"

mkdir -p $BACKUP_DIR

# Backup MySQL database
docker exec ctfd-db-1 mysqldump -u ctfd -pctfd_password ctfd > $BACKUP_DIR/ctfd_db_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/ctfd_db_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "ctfd_db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: ctfd_db_$DATE.sql.gz"
```

### File Backup

```bash
# Backup uploads and logs
tar -czf backup_ctfd_files_$(date +%Y%m%d).tar.gz \
  ctfd/data/CTFd/uploads/ \
  ctfd/data/CTFd/logs/

# Backup to remote server (optional)
rsync -avz backup_*.tar.gz user@backup-server:/backups/ctfd/
```

### Automated Backups with Cron

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup.sh

# Add weekly full backup on Sunday at 3 AM
0 3 * * 0 /path/to/full-backup.sh
```

## Performance Tuning

### Database Optimization

Edit MySQL configuration in `ctfd/docker-compose.yml`:
```yaml
command: 
  - --character-set-server=utf8mb4
  - --collation-server=utf8mb4_unicode_ci
  - --max_connections=200
  - --innodb_buffer_pool_size=1G
  - --query_cache_size=64M
```

### Redis Caching

Ensure Redis is properly configured for caching:
```yaml
cache:
  image: redis:7-alpine
  command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

## Scaling

### Horizontal Scaling

For high-traffic events, scale CTFd workers:
```bash
# Scale to 4 workers
docker-compose up -d --scale ctfd=4
```

### Load Balancer

Add nginx load balancer configuration:
```nginx
upstream ctfd_backend {
    least_conn;
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    listen 443 ssl http2;
    server_name ctf.yourdomain.com;

    location / {
        proxy_pass http://ctfd_backend;
    }
}
```

## Disaster Recovery

### Recovery Steps

1. **Stop all services**
   ```bash
   docker-compose down
   ```

2. **Restore database from backup**
   ```bash
   gunzip ctfd_db_20260214.sql.gz
   docker exec -i ctfd-db-1 mysql -u ctfd -pctfd_password ctfd < ctfd_db_20260214.sql
   ```

3. **Restore files**
   ```bash
   tar -xzf backup_ctfd_files_20260214.tar.gz -C /
   ```

4. **Restart services**
   ```bash
   docker-compose up -d
   ```

5. **Verify functionality**
   ```bash
   curl http://localhost:8000
   docker-compose ps
   docker-compose logs
   ```

## Maintenance

### Regular Updates

```bash
# Pull latest images
docker-compose pull

# Restart with new images
docker-compose down
docker-compose up -d

# Clean up old images
docker image prune -a
```

### Health Checks

Add health checks to `docker-compose.yml`:
```yaml
services:
  ctfd:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Log Rotation

Configure log rotation:
```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/ctfd
```

```
/path/to/ctfd/data/CTFd/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

## Production Tips

1. **Use environment variables** for sensitive data
2. **Enable rate limiting** in CTFd admin panel
3. **Monitor disk space** regularly
4. **Set up alerting** for critical issues
5. **Test backups** regularly
6. **Document your setup** for team reference
7. **Keep services updated** with security patches
8. **Use strong passwords** for all accounts
9. **Limit SSH access** to specific IPs
10. **Review logs** regularly for suspicious activity

## Support and Resources

- [CTFd Official Documentation](https://docs.ctfd.io/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [OWASP Security Guidelines](https://owasp.org/)

For additional help, consult the [Installation Guide](INSTALLATION.md) or open an issue on GitHub.

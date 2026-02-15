# Hivye CTF 2026 - Installation & Deployment Guide

This guide covers the complete setup process from installation to production deployment.

---

## 1. System Requirements

### Prerequisites
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.8+
- **RAM**: 4GB Minimum (8GB Recommended)
- **OS**: Linux (Recommended), macOS, or Windows with WSL2

### Docker Setup (Ubuntu)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

---

## 2. Quick Deployment (Development)

### Step 1: Start Infrastructure
```bash
# Start CTFd
cd ctfd && docker-compose up -d && cd ..

# Start Challenges & Proxy
cd deployment/docker && docker-compose -f docker-compose.challenges.yml up -d && cd ../..
```

### Step 2: Automated Setup
Run the orchestrator to configure the event, create teams, and generate files:
```bash
python setup_ctf.py
```

**What gets created:**
- ✅ **Admin Account**: `admin` / `admin123`
- ✅ **Event**: 2-hour duration, starts in 5 minutes
- ✅ **Teams**: 20 participant teams + 1 admin test team
- ✅ **Files**: Team-specific assets generated automatically

---

## 3. Manual Configuration (Advanced)

### Challenge Import
```bash
python import_challenges.py ctfd/import/challenges/challenges.yml
```

### Team File Generation
```bash
docker run --rm \
  -v $(pwd)/challenges:/challenges \
  -v $(pwd)/utils:/utils \
  -e SECRET_FLAG_KEY="HivyeS3cretKey2026" \
  python:3.9-slim bash -c "
    apt-get update && apt-get install -y steghide curl &&
    pip install scapy pyyaml &&
    python /utils/generate_team_files.py --count 21
  "
```

---

## 4. Access Points

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **CTFd** | 8001 | http://localhost:8001 | Competition Dashboard |
| **Web Challenges** | 8080 | http://localhost:8080 | Vulnerable Bistro App |
| **File Server** | 8081 | http://localhost:8081 | Legacy Static Files |
| **File Proxy** | 8082 | http://localhost:8082 | **Authenticated** Team Downloads |

---

## 5. Production Deployment

### Security Hardening Checklist

Before deploying to production:

- [ ] Change all default passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Configure backups
- [ ] Review resource limits
- [ ] Configure rate limiting

### Change Default Credentials

**CTFd Database** (`ctfd/docker-compose.yml`):
```yaml
environment:
  - MYSQL_ROOT_PASSWORD=YOUR_STRONG_PASSWORD_HERE
  - MYSQL_PASSWORD=YOUR_CTFD_PASSWORD_HERE
```

**Admin Account**: Change immediately after first login via CTFd UI.

### Enable HTTPS

Install nginx as reverse proxy with SSL:

```bash
# Install nginx and certbot
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Configure nginx
sudo nano /etc/nginx/sites-available/ctfd
```

Example nginx config:
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 6. Troubleshooting

### Proxy Access Issues
**Error**: "No session cookie found"  
**Solution**: Users must be logged into their team account on http://localhost:8001 before clicking download links.

### CTFd Connection Error
If the file proxy logs show connection errors to CTFd:
```bash
docker-compose -f deployment/docker/docker-compose.challenges.yml restart file-proxy
```

### Reset Environment
```bash
bash stop.sh
rm -rf ctfd/data/        # WARNING: Deletes all users/settings
rm -rf challenges/teams/ # Deletes generated files

# Start fresh
cd ctfd && docker-compose up -d && cd ..
cd deployment/docker && docker-compose -f docker-compose.challenges.yml up -d && cd ../..
python setup_ctf.py
```

---

## 7. Shutdown

```bash
bash stop.sh
```

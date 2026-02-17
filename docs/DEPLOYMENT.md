# Hyve CTF 2026 - Installation & Deployment Guide

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

The entire environment can be deployed using the automated setup script.

### One-Command Setup
```bash
./setup.sh
```
This script will:
1.  Start all Docker containers (CTFd, Database, Web Challenges).
2.  Wait for services to become healthy.
3.  Run `setup_ctf.py` to:
    *   Configure CTFd (admin user, event timing).
    *   Create participant teams (User: `user_teamN`).
    *   **Generate static challenge files** (OSINT, Stego, Network, Crypto).
    *   Import challenges and **upload files directly to CTFd**.

### Iterative Development
If you want to reset challenges or configuration without recreating all 20+ teams (which is slow), use:
```bash
./setup.sh --skip-users
```

**What gets created:**
- ✅ **Admin Account**: `admin` / `admin123`
- ✅ **Event**: 2-hour duration, starts in 5 minutes
- ✅ **Teams**: 20 participant teams + 1 admin test team
- ✅ **Files**: Static assets uploaded to CTFd

---

## 3. Manual Configuration (Advanced)

### Challenge Import
```bash
python import_challenges.py ctfd/import/challenges/challenges.yml
```

### Static File Generation
To manually regenerate challenge files (OSINT images, PCAPs, etc.):
```bash
docker run --rm \
  -v $(pwd)/challenges:/challenges \
  -v $(pwd)/utils:/utils \
  python:3.9-slim bash -c "
    apt-get update && apt-get install -y steghide curl wget libimage-exiftool-perl &&
    pip install scapy pyyaml &&
    python /utils/generate_team_files.py --output /challenges
  "
```

---

## 4. Access Points

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **CTFd** | 8001 | http://localhost:8001 | Competition Dashboard |
| **Web Challenges** | 8080 | http://localhost:8080 | Vulnerable Bistro App |

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

## 6. Troubleshooting & FAQ

### Common Issues

#### 1. Internal Server Error (500) on Setup or Login
*   **Cause**: Usually caused by database corruption or plugin initialization conflicts (e.g., `DynamicXORKey` trying to recreate existing tables).
*   **Solution**: Perform a deep-clean wipe. The standard `docker compose down` might not clear host-mounted volumes.
    ```bash
    ./stop.sh -rm
    # If the directory still exists, remove it manually
    sudo rm -rf ctfd/data
    ./setup.sh
    ```

#### 2. Port Conflict / Site "Still Works" After Stop
*   **Cause**: Port `8001` or `8080` might be held by another application (like a native Flask app) or an orphan WSL relay process.
*   **Solution**: Identify and kill the process holding the port.
    *   **Windows (PowerShell)**: 
        ```powershell
        netstat -ano | findstr :8001
        Stop-Process -Id <PID> -Force
        ```
    *   **WSL/Linux**:
        ```bash
        sudo fuser -k 8001/tcp
        ```

#### 3. API Token Generation Failed / CSRF Errors
*   **Cause**: The automated setup script cannot find the CSRF nonce, often because the CTFd page returned an error (500) instead of the expected UI.
*   **Solution**: Fix the underlying 500 error first (see point #1). Ensure `DynamicXORKey` plugin is correctly registered without redundant `db.create_all()` calls.

#### 4. Web Challenges: "ModuleNotFoundError: No module named 'utils'"
*   **Cause**: The `ctf-web-challenges` container is missing the shared `utils/` directory.
*   **Solution**: Ensure the `Dockerfile` for web challenges includes `COPY utils/ /app/utils/`. This is already fixed in the latest repo version.

### WSL2 Specific Tips

If you are running on Windows with WSL2, the network bridge sometimes "sticks". If `localhost:8001` refuses to connect even when Docker says "Up", try:
1.  Restarting Docker Desktop.
2.  Running `wsl --shutdown` in PowerShell and restarting your terminal.
3.  Ensuring your WSL distro (e.g., Kali/Ubuntu) isn't running a native CTFd instance on the same ports.

---

## 7. Shutdown

```bash
./stop.sh
```

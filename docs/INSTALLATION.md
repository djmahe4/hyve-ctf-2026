# Installation Guide

Complete step-by-step guide to install and configure Hivye CTF 2026 platform.

## System Requirements

### Minimum Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (11+), or Windows with WSL2
- **RAM**: 4GB minimum
- **Disk Space**: 10GB free space
- **CPU**: 2 cores minimum

### Recommended Requirements
- **RAM**: 8GB or more
- **Disk Space**: 20GB free space
- **CPU**: 4 cores or more

### Software Requirements
- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- Git
- Python 3.8+ (optional, for challenge creation scripts)

## Step-by-Step Installation

### 1. Install Docker

#### Ubuntu/Debian
```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to docker group
sudo usermod -aG docker $USER
```

#### macOS
```bash
# Download and install Docker Desktop from:
# https://www.docker.com/products/docker-desktop

# Or using Homebrew:
brew install --cask docker

# Start Docker Desktop application
open -a Docker
```

### 2. Clone Repository
```bash
# Clone the repository
git clone https://github.com/djmahe4/hyve-ctf-2026.git
cd hyve-ctf-2026

# Verify directory structure
ls -la
```

### 3. Start CTFd Platform
```bash
# Navigate to CTFd directory
cd ctfd

# Start CTFd services
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs (optional)
docker-compose logs -f
```

Wait about 30-60 seconds for all services to initialize.

### 4. Access CTFd
Open your browser and navigate to: http://localhost:8000

#### First-Time Setup Wizard
1. Click "Setup" to begin configuration
2. Create an admin account:
   - **Username**: admin (or your choice)
   - **Email**: admin@hivyectf.com (or your choice)
   - **Password**: Choose a strong password
3. Configure CTF settings:
   - **CTF Name**: Hivye CTF 2026
   - **Start Time**: Set competition start time
   - **End Time**: Set to 2 hours after start time
   - **CTF Mode**: Choose "Jeopardy" or "King of the Hill"
4. Click "Finish" to complete setup

### 5. Import Challenges
```bash
# From the project root directory
docker cp ctfd/import/challenges/challenges.yml $(docker ps -qf "name=ctfd-ctfd"):/opt/CTFd/import/challenges.yml

# Or use the CTFd Admin Panel:
# 1. Login as admin at http://localhost:8000
# 2. Go to Admin Panel > Config > Backup
# 3. Click "Import" tab
# 4. Upload the challenges.yml file from ctfd/import/challenges/
# 5. Click "Import" button
```

### 6. Deploy Challenge Infrastructure
```bash
# Navigate to deployment directory
cd ../deployment/docker

# Start challenge services
docker-compose -f docker-compose.challenges.yml up -d

# Check if services are running
docker-compose -f docker-compose.challenges.yml ps
```

### 7. Verify Deployment
```bash
# Test CTFd platform
curl http://localhost:8000

# Test web challenges
curl http://localhost:8080

# Test file server
curl http://localhost:8081
```

All services should respond with HTTP 200 OK.

## Troubleshooting

### Port Conflicts
If you encounter port conflicts:
```bash
# Check which process is using the port
sudo lsof -i :8000
sudo lsof -i :8080
sudo lsof -i :8081

# Stop conflicting services or modify port mappings in docker-compose.yml
```

### Container Issues
```bash
# View container logs
docker-compose logs ctfd
docker-compose logs db
docker-compose logs cache

# Restart containers
docker-compose restart

# Rebuild containers
docker-compose down
docker-compose up -d --build
```

### Database Connection Errors
```bash
# Check if database is ready
docker-compose exec db mysql -u ctfd -pctfd_password -e "SHOW DATABASES;"

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

### Permission Errors
```bash
# Fix permission issues with volumes
sudo chown -R $USER:$USER ctfd/data

# Or run with sudo (not recommended for production)
sudo docker-compose up -d
```

## Next Steps

- [Deployment Guide](DEPLOYMENT.md) - Production deployment considerations
- [Challenge Writeups](WRITEUPS.md) - Solutions for all challenges
- Configure firewall rules for production
- Set up HTTPS with SSL certificates
- Configure backups

## Additional Resources

- [CTFd Documentation](https://docs.ctfd.io/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

#!/bin/bash
set -e

echo "=========================================="
echo "  Hivye CTF 2026 - Setup Script"
echo "=========================================="
echo ""

# 1. Install Python Dependencies
echo "[*] Installing Python dependencies..."
if [ ! -d ".venv" ]; then
    echo "    Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate and install
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

pip install -r requirements.txt
echo "    ✓ Dependencies installed"
echo ""

# 2. Check for Docker
echo "[*] Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "    ✓ Docker found: $(docker --version)"
echo "    ✓ Docker Compose found: $(docker-compose --version)"
echo ""

# 3. Import Challenges
echo "[*] Setting up CTFd with challenges..."
echo "    Challenges will be imported from ctfd/import/challenges/challenges.yml"
echo ""

# 4. Start Services
echo "[*] Starting CTFd platform..."
cd ctfd
docker-compose up -d
cd ..
echo "    ✓ CTFd started"
echo ""

echo "[*] Starting challenge infrastructure..."
cd deployment/docker
docker-compose -f docker-compose.challenges.yml up -d
cd ../..
echo "    ✓ Challenge services started"
echo ""

# 5. Wait for initialization
echo "[*] Waiting for services to initialize (30 seconds)..."
sleep 30
echo ""

# 6. Setup Complete
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Access the CTF platform at:"
echo "  - CTFd Platform: http://localhost:8001"
echo "  - Web Challenges: http://localhost:8080"
echo "  - File Server: http://localhost:8081"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:8001"
echo "  2. Create an admin account"
echo "  3. Challenges are auto-imported"
echo ""
echo "Documentation:"
echo "  - Installation: docs/INSTALLATION.md"
echo "  - Deployment: docs/DEPLOYMENT.md"
echo "  - Writeups: docs/WRITEUPS.md"
echo ""
echo "To stop all services, run: ./stop.sh"
echo "=========================================="

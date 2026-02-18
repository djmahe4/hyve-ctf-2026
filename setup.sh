#!/bin/bash
# Simplified setup script for Hyve CTF 2026
set -e

echo "=========================================="
echo "  Hyve CTF 2026 - Infrastructure Setup"
echo "=========================================="
echo ""

# Detector for docker-compose vs docker compose
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "[!] Error: Neither 'docker compose' nor 'docker-compose' found."
    echo "    Please ensure Docker is installed and WSL integration is enabled."
    exit 1
fi

# Install native dependencies if in WSL/Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "[*] Installing native dependencies (requires sudo)..."
    sudo apt-get update && sudo apt-get install -y steghide exiftool imagemagick wget curl
    pip3 install scapy pyyaml requests
fi

# Generate static challenge files natively
echo "[*] Generating challenge files natively..."
python3 utils/generate_team_files.py
echo "    ✓ Challenge files generated in challenges/static/"
echo ""

# Start CTFd
echo "[*] Starting CTFd platform (Docker)..."
cd ctfd
$DOCKER_COMPOSE up -d
cd ..
echo "    ✓ CTFd started"
echo ""

# Start challenge web services
echo "[*] Starting challenge web services (Docker)..."
cd deployment/docker
$DOCKER_COMPOSE -f docker-compose.challenges.yml up -d
cd ../..
echo "    ✓ Challenge web services started"
echo ""

echo "[*] Running automated configuration (setup_ctf.py)..."
python3 setup_ctf.py "$@"

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="

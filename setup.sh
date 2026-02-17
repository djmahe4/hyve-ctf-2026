#!/bin/bash
# Simplified setup script for Hyve CTF 2026
set -e

echo "=========================================="
echo "  Hyve CTF 2026 - Infrastructure Setup"
echo "=========================================="
echo ""

# Install native dependencies if in WSL/Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "[*] Installing native dependencies (requires sudo)..."
    sudo apt-get update && sudo apt-get install -y steghide exiftool imagemagick wget curl
    pip3 install scapy pyyaml requests
fi

# Start CTFd
echo "[*] Starting CTFd platform (Docker)..."
cd ctfd
docker-compose up -d
cd ..
echo "    ✓ CTFd started"
echo ""

# Start challenge web services
echo "[*] Starting challenge web services (Docker)..."
cd deployment/docker
docker-compose -f docker-compose.challenges.yml up -d
cd ../..
echo "    ✓ Challenge web services started"
echo ""

echo "[*] Running automated configuration (setup_ctf.py)..."
python3 setup_ctf.py "$@"

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="

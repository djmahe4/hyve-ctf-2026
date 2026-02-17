#!/bin/bash
# Simplified setup script - just starts services
# Use setup_ctf.py for full automated configuration

set -e

echo "=========================================="
echo "  Hyve CTF 2026 - Infrastructure Setup"
echo "=========================================="
echo ""

# Start CTFd
echo "[*] Starting CTFd platform..."
cd ctfd
docker-compose up -d
cd ..
echo "    ✓ CTFd started"
echo ""

# Start challenges
echo "[*] Starting challenge infrastructure..."
cd deployment/docker
docker-compose -f docker-compose.challenges.yml up -d
cd ../..
echo "    ✓ Challenge services started"
echo ""

echo "=========================================="
echo "  Infrastructure Ready!"
echo "=========================================="
echo ""
echo "=========================================="
echo "  Infrastructure Ready!"
echo "=========================================="
echo ""
echo "[*] Running automated configuration (setup_ctf.py)..."
echo "    Passing arguments: $@"
python3 setup_ctf.py "$@"
echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="

#!/bin/bash
# Simplified setup script - just starts services
# Use setup_ctf.py for full automated configuration

set -e

echo "=========================================="
echo "  Hivye CTF 2026 - Infrastructure Setup"
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
echo "Next step:"
echo "  Run: python setup_ctf.py"
echo ""
echo "For custom configuration:"
echo "  python setup_ctf.py --teams 30 --duration 3"
echo "  python setup_ctf.py --help"
echo ""
echo "To stop all services: ./stop.sh"
echo "=========================================="

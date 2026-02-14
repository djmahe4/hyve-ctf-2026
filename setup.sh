#!/bin/bash
set -e

echo "=========================================="
echo "  Hivye CTF 2026 - Setup Script"
echo "=========================================="
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    echo "Please install Docker Compose first: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker is installed"
echo "✓ Docker Compose is installed"
echo ""

# Create challenge files
echo "Creating challenge files..."
echo ""

# Create network PCAP if Python and scapy are available
if command -v python3 &> /dev/null; then
    echo "Generating network challenge PCAP..."
    cd challenges/network
    
    # Check if scapy is installed
    if python3 -c "import scapy" 2>/dev/null; then
        python3 create_pcap.py
    else
        echo "Note: Scapy not installed. Skipping PCAP generation."
        echo "Install with: pip3 install scapy"
    fi
    
    cd ../..
else
    echo "Note: Python3 not found. Skipping PCAP generation."
fi

echo ""
echo "Starting CTFd platform..."
cd ctfd
docker-compose up -d

echo ""
echo "Waiting for services to initialize (30 seconds)..."
sleep 30

echo ""
echo "Starting challenge infrastructure..."
cd ../deployment/docker
docker-compose -f docker-compose.challenges.yml up -d

cd ../..

echo ""
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Access the CTF platform at:"
echo "  - CTFd Platform: http://localhost:8000"
echo "  - Web Challenges: http://localhost:8080"
echo "  - File Server: http://localhost:8081"
echo ""
echo "Next steps:"
echo "  1. Visit http://localhost:8000 to complete the setup wizard"
echo "  2. Create an admin account"
echo "  3. Import challenges from ctfd/import/challenges/challenges.yml"
echo ""
echo "Documentation:"
echo "  - Installation: docs/INSTALLATION.md"
echo "  - Deployment: docs/DEPLOYMENT.md"
echo "  - Writeups: docs/WRITEUPS.md"
echo ""
echo "To stop all services, run: ./stop.sh"
echo "=========================================="

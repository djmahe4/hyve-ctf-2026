#!/bin/bash

echo "Stopping Hivye CTF 2026..."
echo ""

# Stop CTFd
echo "Stopping CTFd platform..."
cd ctfd
docker-compose down
cd ..

# Stop challenges
echo "Stopping challenge infrastructure..."
cd deployment/docker
docker-compose -f docker-compose.challenges.yml down
cd ../..

echo ""
echo "All services stopped successfully!"
echo ""

#!/bin/bash

echo "Starting Hivye CTF 2026..."
echo ""

# Start CTFd
echo "Starting CTFd platform..."
cd ctfd
docker-compose up -d
cd ..

# Start challenges
echo "Starting challenge infrastructure..."
cd deployment/docker
docker-compose -f docker-compose.challenges.yml up -d
cd ../..

echo ""
echo "All services started successfully!"
echo ""
echo "Access the platform at:"
echo "  - CTFd Platform: http://localhost:8000"
echo "  - Web Challenges: http://localhost:8080"
echo "  - File Server: http://localhost:8081"
echo ""

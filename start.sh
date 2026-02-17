#!/bin/bash

echo "Starting Hyve CTF 2026..."
echo ""

# Start challenges
echo "Starting challenge web services..."
cd deployment/docker
docker-compose -f docker-compose.challenges.yml up -d
cd ../..

echo ""
echo "All services started successfully!"
echo ""
echo "Access the platform at:"
echo "  - CTFd Platform: http://localhost:8001"
echo "  - Web Challenges: http://localhost:8080"
echo ""

#!/bin/bash

echo "Starting Hyve CTF 2026..."
echo ""

# Detector for docker-compose vs docker compose
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "[!] Error: Neither 'docker compose' nor 'docker-compose' found."
    exit 1
fi

# Start challenges
echo "Starting challenge web services..."
cd deployment/docker
$DOCKER_COMPOSE -f docker-compose.challenges.yml up -d
cd ../..

echo ""
echo "All services started successfully!"
echo ""
echo "Access the platform at:"
echo "  - CTFd Platform: http://localhost:8001"
echo "  - Web Challenges: http://localhost:8080"
echo ""

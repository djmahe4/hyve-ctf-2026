#!/bin/bash

# Parse arguments
REMOVE_DATA=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -rm|--remove)
            REMOVE_DATA=true
            shift
            ;;
        -h|--help)
            echo "Usage: ./stop.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -rm, --remove    Remove all data (containers, volumes, team files)"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./stop.sh              # Stop services only"
            echo "  ./stop.sh -rm          # Stop and remove all data"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

echo "Stopping Hyve CTF 2026..."
echo ""

# Detector for docker-compose vs docker compose
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    # If docker is not running, we might still want to clean up local data
    # but we'll set it to a dummy for now
    DOCKER_COMPOSE="docker compose"
fi

if [ "$REMOVE_DATA" = true ]; then
    echo "⚠️  WARNING: This will remove all containers, volumes, and data!"
    echo "   - CTFd database (all users, teams, submissions)"
    echo "   - Generated team files"
    echo ""
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Cancelled."
        exit 0
    fi
    echo ""
fi

# Stop CTFd
echo "[*] Stopping CTFd platform..."
cd ctfd
if [ "$REMOVE_DATA" = true ]; then
    $DOCKER_COMPOSE down -v  # Remove volumes
else
    $DOCKER_COMPOSE down
fi
cd ..
echo "    ✓ CTFd stopped"
echo ""

# Stop challenges
echo "[*] Stopping challenge infrastructure..."
cd deployment/docker
if [ "$REMOVE_DATA" = true ]; then
    $DOCKER_COMPOSE -f docker-compose.challenges.yml down -v  # Remove volumes
else
    $DOCKER_COMPOSE -f docker-compose.challenges.yml down
fi
cd ../..
echo "    ✓ Challenge services stopped"
echo ""

# Remove generated static files if requested
if [ "$REMOVE_DATA" = true ]; then
    echo "[*] Removing generated static challenge files..."
    if [ -d "challenges/static" ]; then
        rm -rf challenges/static
        echo "    ✓ Static files removed"
    else
        echo "    ℹ No static files to remove"
    fi
    echo ""
    
    echo "[*] Removing CTFd persistent data..."
    if [ -d "ctfd/data" ]; then
        # Use sudo to remove to avoid permission issues if Docker created them
        sudo rm -rf ctfd/data
        echo "    ✓ CTFd data removed (database, uploads, logs)"
    else
        echo "    ℹ No CTFd data to remove"
    fi
    echo ""
fi

echo ""
if [ "$REMOVE_DATA" = true ]; then
    echo "All services stopped and data removed!"
    echo "To start fresh, run: ./setup.sh && python3 setup_ctf.py"
else
    echo "All services stopped successfully!"
    echo "Data preserved. Use './stop.sh -rm' to remove all data."
fi
echo ""

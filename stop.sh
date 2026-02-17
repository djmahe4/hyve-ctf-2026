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
    docker-compose down -v  # Remove volumes
else
    docker-compose down
fi
cd ..
echo "    ✓ CTFd stopped"
echo ""

# Stop challenges
echo "[*] Stopping challenge infrastructure..."
cd deployment/docker
if [ "$REMOVE_DATA" = true ]; then
    docker-compose -f docker-compose.challenges.yml down -v  # Remove volumes
else
    docker-compose -f docker-compose.challenges.yml down
fi
cd ../..
echo "    ✓ Challenge services stopped"
echo ""

# Remove generated team files if requested
if [ "$REMOVE_DATA" = true ]; then
    echo "[*] Removing generated team files..."
    if [ -d "challenges/teams" ]; then
        # Use docker to remove to avoid permission issues
        docker run --rm -v "$(pwd)/challenges/teams:/data" alpine sh -c "rm -rf /data/*"
        # Then remove the directory itself if empty/possible, or just leave empty dir
        rm -rf challenges/teams
        echo "    ✓ Team files removed"
    else
        echo "    ℹ No team files to remove"
    fi
    echo ""
    
    echo "[*] Removing CTFd persistent data..."
    if [ -d "ctfd/data" ]; then
        # Use docker to remove to avoid permission issues
        docker run --rm -v "$(pwd)/ctfd/data:/data" alpine sh -c "rm -rf /data/*"
        rm -rf ctfd/data
        echo "    ✓ CTFd data removed (database, uploads, logs)"
    else
        echo "    ℹ No CTFd data to remove"
    fi
    echo ""
fi

echo ""
if [ "$REMOVE_DATA" = true ]; then
    echo "All services stopped and data removed!"
    echo "To start fresh, run: ./setup.sh && python setup_ctf.py"
else
    echo "All services stopped successfully!"
    echo "Data preserved. Use './stop.sh -rm' to remove all data."
fi
echo ""

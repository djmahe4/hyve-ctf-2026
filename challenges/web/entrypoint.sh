#!/bin/bash
set -e

echo "[*] Waiting for application files..."

while [ ! -f /app/app.py ]; do
    sleep 2
    echo "    waiting..."
done

echo "[*] Application files found!"
echo "[*] Initializing database..."
python init_db.py

echo "[*] Starting Hyve Bistro..."
exec python app.py

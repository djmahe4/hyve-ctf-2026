#!/bin/bash

# Hivye CTF 2026 Setup Script

echo "--- Hivye CTF 2026: Setup ---"

# 1. Create Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment..."
    python -m venv .venv
else
    echo "[*] Virtual environment already exists."
fi

# 2. Activate and Install Dependencies
echo "[*] Installing dependencies from requirements.txt..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source .venv/Scripts/activate
    python -m pip install -r requirements.txt
else
    # Linux/MacOS
    source .venv/bin/activate
    pip install -r requirements.txt
fi

echo "[+] Setup complete! Activate your environment with:"
echo "    Windows: .\\.venv\\Scripts\\activate"
echo "    Linux/Mac: source .venv/bin/activate"

#!/bin/bash
# Create steganography challenge image with hidden flag
# Flag format: HYVE_CTF{content}

set -e

echo "Creating steganography challenge..."

# Download a cat image from Pexels
echo "Downloading cat image..."
wget -q -O cat.jpeg "https://images.pexels.com/photos/1170986/pexels-photo-1170986.jpeg?auto=compress&cs=tinysrgb&w=800"

# Determine Team ID
TEAM_ID=${TEAM_ID:-1}

# Generate dynamic flag using our utility
FLAG=$(python3 -c "import sys; sys.path.append('../..'); from utils.flag_gen import get_flag; print(get_flag('st3g0_cat_m4st3r', '$TEAM_ID'))")

echo "[*] Generating Stego image for Team $TEAM_ID"
echo "[*] Flag: $FLAG"

# Password from wordlist (transposition of ctf-2026)
PASSWORD="2026-ftc"

# Embed flag
steghide embed -cf cat.jpeg -ef <(echo "$FLAG") -p "$PASSWORD" -v

echo "[+] Done! cat.jpeg updated for Team $TEAM_ID"

echo "Steganography challenge created successfully!"
echo "Image: cat.jpeg"
echo "Wordlist: wordlist.txt (contains transposition-ciphered password)"
echo "Hidden message: HYVE_CTF{st3g0_cat_m4st3r}"

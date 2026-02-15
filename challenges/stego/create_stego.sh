#!/bin/bash
# Create steganography challenge image with hidden flag
# Flag format: HYVE_CTF{content_HASH}

set -e

echo "Creating steganography challenge..."

# Download a cat image from Pexels
echo "Downloading cat image..."
wget -q -O cat.jpeg "https://images.pexels.com/photos/1170986/pexels-photo-1170986.jpeg?auto=compress&cs=tinysrgb&w=800"

# Create a file with the base flag
echo "HYVE_CTF{st3g0_cat_m4st3r_HASH}" > secret.txt

# Embed the secret using steghide
# Password is 'ctf2026' transpositioned as '2026-ftc' or interleaving in wordlist.txt
# For this script we use the actual password '2026-ftc' found via wordlist analysis
echo "Embedding secret message..."
steghide embed -cf cat.jpeg -ef secret.txt -p 2026-ftc -q

# Clean up
rm secret.txt

echo "Steganography challenge created successfully!"
echo "Image: cat.jpeg"
echo "Wordlist: wordlist.txt (contains transposition-ciphered password)"
echo "Hidden message: HYVE_CTF{st3g0_cat_m4st3r_HASH}"


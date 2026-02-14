#!/bin/bash
# Create steganography challenge image with hidden flag

set -e

echo "Creating steganography challenge..."

# Download a cat image from Pexels
echo "Downloading cat image..."
wget -q -O cat.jpeg "https://images.pexels.com/photos/1170986/pexels-photo-1170986.jpeg?auto=compress&cs=tinysrgb&w=800"

# Create a file with the flag
echo "FLAG{st3g0_cat_m4st3r}" > secret.txt

# Embed the secret using steghide
echo "Embedding secret message..."
steghide embed -cf cat.jpeg -ef secret.txt -p ctf2026 -q

# Clean up
rm secret.txt

echo "Steganography challenge created successfully!"
echo "Image: cat.jpeg"
echo "Password: ctf2026"
echo "Hidden message: FLAG{st3g0_cat_m4st3r}"

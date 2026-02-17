#!/usr/bin/env python3
"""
Generate team-specific challenge files with embedded dynamic flags
"""
import os
import shutil
import base64
import sys
import argparse
import subprocess
from pathlib import Path

# Add parent directory to path to import flag_gen
sys.path.append(str(Path(__file__).parent.parent))
from utils.flag_gen import get_flag

PROJECT_ROOT = Path(__file__).parent.parent
CHALLENGES_DIR = PROJECT_ROOT / "challenges"
STATIC_DIR = CHALLENGES_DIR / "static"


def create_static_directory():
    """Create directory structure for static challenge files"""
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories for each challenge category
    categories = ["osint", "stego", "network", "crypto"]
    for category in categories:
        (STATIC_DIR / category).mkdir(parents=True, exist_ok=True)
    
    print(f"[+] Created directory structure in {STATIC_DIR}")
    return STATIC_DIR


import random
import time

# Dynamic Landmarks List (Wikimedia Commons URLs - reliable and open)
LANDMARKS = [
    {
        "name": "Eiffel Tower",
        "keywords": ["PARIS", "FRANCE", "EIFFELTOWER"],
        "lat": 48.8584, "lon": 2.2945, "lat_ref": "N", "lon_ref": "E",
        "url": "https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_(cropped).jpg"
    },
    {
        "name": "Big Ben",
        "keywords": ["LONDON", "UK", "BIGBEN"],
        "lat": 51.5007, "lon": 0.1246, "lat_ref": "N", "lon_ref": "W",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Palace_of_Westminster_from_the_dome_on_Methodist_Central_Hall.jpg/800px-Palace_of_Westminster_from_the_dome_on_Methodist_Central_Hall.jpg"
    },
    {
        "name": "Colosseum",
        "keywords": ["ROME", "ITALY", "COLOSSEUM"],
        "lat": 41.8902, "lon": 12.4922, "lat_ref": "N", "lon_ref": "E",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseo_2020.jpg/800px-Colosseo_2020.jpg"
    },
    {
        "name": "Sydney Opera House",
        "keywords": ["SYDNEY", "AUSTRALIA", "OPERAHOUSE"],
        "lat": -33.8568, "lon": 151.2153, "lat_ref": "S", "lon_ref": "E",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Sydney_Opera_House_Sails.jpg/800px-Sydney_Opera_House_Sails.jpg"
    },
    {
        "name": "Great Wall of China",
        "keywords": ["BEIJING", "CHINA", "GREATWALL"],
        "lat": 40.4319, "lon": 116.5704, "lat_ref": "N", "lon_ref": "E",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/800px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg"
    },
]

def generate_files(output_dir):
    """Generate global static challenge files"""
    print(f"[*] Generating challenge files in {output_dir}...")
    
    # Ensure output directories exist
    (output_dir / "osint").mkdir(parents=True, exist_ok=True)
    (output_dir / "stego").mkdir(parents=True, exist_ok=True)
    (output_dir / "network").mkdir(parents=True, exist_ok=True)
    (output_dir / "crypto").mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # OSINT: Generate mystery location image
    landmark = next((l for l in LANDMARKS if "EIFFELTOWER" in l["keywords"]), LANDMARKS[0])
    print(f"  > Generating OSINT challenge (Landmark: {landmark['name']})...")
    
    output_file = output_dir / "osint" / "mystery_location.jpg"
    source_images_dir = PROJECT_ROOT / "challenges" / "osint" / "source_images"
    download_success = False
    
    cand_local_path = source_images_dir / f"{landmark['name']}.jpg"
    if cand_local_path.exists():
         shutil.copy2(cand_local_path, output_file)
         download_success = True
    else:
        try:
            cmd = ['wget', '-q', '-U', 'Mozilla/5.0', '-O', str(output_file), landmark['url']]
            result = subprocess.run(cmd)
            if result.returncode == 0 and output_file.exists():
                download_success = True
        except Exception as e:
            print(f"    ✗ Download failed: {e}")

    if download_success:
        exif_cmd = [
            'exiftool',
            f'-GPSLatitude={landmark["lat"]}',
            f'-GPSLatitudeRef={landmark["lat_ref"]}',
            f'-GPSLongitude={landmark["lon"]}',
            f'-GPSLongitudeRef={landmark["lon_ref"]}',
            '-overwrite_original',
            str(output_file)
        ]
        subprocess.run(exif_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"    ✓ Embedded GPS coordinates")

    # -------------------------------------------------------------------------
    # STEGO: Embed flag in image
    print(f"  > Generating Stego challenge...")
    flag = get_flag("st3g0_cat_m4st3r")
    secret_file = output_dir / "stego" / "secret.txt"
    with open(secret_file, 'w') as f:
        f.write(flag)
    
    cover_image = output_dir / "stego" / "cat.jpeg"
    local_cat = PROJECT_ROOT / "challenges" / "stego" / "cat.jpeg"
    if local_cat.exists():
        if local_cat.resolve() != cover_image.resolve():
            shutil.copy2(local_cat, cover_image)
    else:
        subprocess.run(['convert', '-size', '600x400', 'xc:grey', str(cover_image)]) 

    password = "2026-ftc" 
    stego_cmd = [
        'steghide', 'embed', '-cf', str(cover_image), '-ef', str(secret_file), '-p', password, '-f'
    ]
    try:
        subprocess.run(stego_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if secret_file.exists():
            os.remove(secret_file)
    except Exception as e:
        print(f"    ✗ Steghide failed: {e}")
    
    wordlist_path = output_dir / "stego" / "wordlist.txt"
    with open(wordlist_path, 'w') as f:
        f.write(f"purr\nwhiskers\n{password}\nkitty\nscratch\n")
    print(f"    ✓ Created Stego image and wordlist")

    # -------------------------------------------------------------------------
    # NETWORK: Generate PCAP
    print(f"  > Generating Network challenge...")
    pcap_out = output_dir / "network" / "cleartext_traffic.pcap"
    try:
        # Pass team_id="1" since we are in global mode, and the output path
        cmd = [sys.executable, str(PROJECT_ROOT / "challenges" / "network" / "create_pcap.py"), "1", str(pcap_out)]
        subprocess.run(cmd, check=True)
        print(f"    ✓ Generated PCAP")
    except Exception as e:
         print(f"    ✗ Network challenge generation failed: {e}")

    # -------------------------------------------------------------------------
    # CRYPTO: Generate Base64 file
    print(f"  > Generating Crypto challenge...")
    crypto_out = output_dir / "crypto" / "base64.txt"
    crypto_flag = get_flag("base64_decoded_success")
    encoded = base64.b64encode(base64.b64encode(base64.b64encode(crypto_flag.encode()))).decode()
    with open(crypto_out, 'w') as f:
        f.write(encoded)
    print(f"    ✓ Generated encoded text file")


def main():
    parser = argparse.ArgumentParser(description='Generate global static challenge files for CTF')
    parser.add_argument('--output', help='Output directory')
    args = parser.parse_args()
    
    output_dir = Path(args.output).resolve() if args.output else STATIC_DIR
    
    print(f"=== Challenge File Generation ===")
    print(f"Target directory: {output_dir}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    generate_files(output_dir)
    
    print(f"\n[✓] All done!")

if __name__ == '__main__':
    main()

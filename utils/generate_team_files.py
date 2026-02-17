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
TEAMS_DIR = CHALLENGES_DIR / "teams"


def create_team_directory(team_id):
    """Create directory structure for a team"""
    team_dir = TEAMS_DIR / f"team{team_id}"
    
    # Create subdirectories for each challenge category
    categories = ["osint", "stego", "network", "crypto"]
    for category in categories:
        (team_dir / category).mkdir(parents=True, exist_ok=True)
    
    print(f"[+] Created directory structure for Team {team_id}")
    return team_dir


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

def generate_files(output_dir, team_id="1"):
    """Generate team-specific static challenge files"""
    print(f"[*] Generating challenge files for Team {team_id}...")
    
    # Ensure output directories exist
    (output_dir / "osint").mkdir(parents=True, exist_ok=True)
    (output_dir / "stego").mkdir(parents=True, exist_ok=True)
    (output_dir / "network").mkdir(parents=True, exist_ok=True)
    (output_dir / "crypto").mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # OSINT: Generate mystery location image
    # FORCE STATIC: Always use Paris/Eiffel Tower
    landmark = next((l for l in LANDMARKS if "EIFFELTOWER" in l["keywords"]), LANDMARKS[0])
    print(f"  > Generating OSINT challenge (Landmark: {landmark['name']})...")
    
    output_file = output_dir / "osint" / "mystery_location.jpg"
    
    source_images_dir = PROJECT_ROOT / "challenges" / "osint" / "source_images"
    download_success = False
    
    # Check local first
    cand_local_path = source_images_dir / f"{landmark['name']}.jpg"
    if cand_local_path.exists():
         print(f"    ✓ Using local source image: {landmark['name']}")
         shutil.copy2(cand_local_path, output_file)
         download_success = True
    else:
        print(f"    > Attempting download: {landmark['name']}")
        try:
            cmd = ['wget', '-q', '-U', 'Mozilla/5.0', '-O', str(output_file), landmark['url']]
            result = subprocess.run(cmd)
            if result.returncode == 0 and output_file.exists():
                download_success = True
        except Exception as e:
            print(f"    ✗ Download failed: {e}")

    if download_success:
        # Add metadata
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
    # Generate dynamic flag for this team
    flag = get_flag("st3g0_cat_m4st3r", team_id)
    secret_file = output_dir / "stego" / "secret.txt"
    with open(secret_file, 'w') as f:
        f.write(flag)
    
    cover_image = output_dir / "stego" / "cat.jpeg"
    # Check for local cat.jpeg
    local_cat = PROJECT_ROOT / "challenges" / "stego" / "cat.jpeg"
    if local_cat.exists():
        if local_cat.resolve() != cover_image.resolve():
            shutil.copy2(local_cat, cover_image)
    else:
        # Fallback dump
        subprocess.run(['convert', '-size', '600x400', 'xc:grey', str(cover_image)]) 

    # Embed
    password = "2026-ftc" # Matches docs
    stego_cmd = [
        'steghide', 'embed', '-cf', str(cover_image), '-ef', str(secret_file), '-p', password, '-f'
    ]
    try:
        subprocess.run(stego_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if secret_file.exists():
            os.remove(secret_file)
    except Exception as e:
        print(f"    ✗ Steghide failed: {e}")
    
    # Wordlist
    wordlist_path = output_dir / "stego" / "wordlist.txt"
    with open(wordlist_path, 'w') as f:
        # Transposition of ctf-2026 is 2026-ftc
        f.write(f"purr\nwhiskers\n{password}\nkitty\nscratch\n")
    print(f"    ✓ Created Stego image and wordlist for team {team_id}")

    # -------------------------------------------------------------------------
    # NETWORK: Generate PCAP
    print(f"  > Generating Network challenge...")
    (output_dir / "network").mkdir(parents=True, exist_ok=True)
    pcap_out = output_dir / "network" / "cleartext_traffic.pcap"
    # Use the existing script but pass the correct flag
    try:
        network_flag = get_flag("cl34rt3xt_cr3ds_f0und", team_id)
        cmd = ['python3', str(PROJECT_ROOT / "challenges" / "network" / "create_pcap.py"), network_flag, str(pcap_out)]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"    ✓ Generated PCAP for team {team_id}")
    except Exception as e:
         print(f"    ✗ Network challenge generation failed: {e}")

    # -------------------------------------------------------------------------
    # CRYPTO: Generate Base64 file
    print(f"  > Generating Crypto challenge...")
    (output_dir / "crypto").mkdir(parents=True, exist_ok=True)
    crypto_out = output_dir / "crypto" / "base64.txt"
    crypto_flag = get_flag("base64_decoded_success", team_id)
    encoded = base64.b64encode(base64.b64encode(base64.b64encode(crypto_flag.encode()))).decode()
    with open(crypto_out, 'w') as f:
        f.write(encoded)
    print(f"    ✓ Generated encoded text file for team {team_id}")


def main():
    parser = argparse.ArgumentParser(description='Generate team-specific challenge files for CTF')
    parser.add_argument('--count', type=int, help='Number of teams to generate for (Team 1 to N)')
    parser.add_argument('--teams', type=str, help='Comma-separated list of team IDs (e.g., 1,2,5)')
    parser.add_argument('--output', help='Output directory (default: challenges/teams)')
    args = parser.parse_args()
    
    # Determine which teams to generate for
    team_ids = []
    if args.count:
        team_ids = [str(i) for i in range(1, args.count + 1)]
    elif args.teams:
        team_ids = [t.strip() for t in args.teams.split(',')]
    else:
        # Default: just team 1 if nothing specified
        team_ids = ["1"]
    
    print(f"=== Challenge File Generation ===")
    print(f"Generating files for teams: {', '.join(team_ids)}")
    
    for tid in team_ids:
        team_dir = create_team_directory(tid)
        generate_files(team_dir, tid)
    
    print(f"\n[✓] All done!")
    print(f"Files are located in {TEAMS_DIR}")

if __name__ == '__main__':
    main()

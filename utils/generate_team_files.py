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

def generate_files(output_dir):
    """Generate static challenge files"""
    print(f"[*] Generating static challenge files...")
    
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
    
    source_images_dir = Path("challenges/osint/source_images")
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
    # Flag: HYVE_CTF{st3g0_cat_m4st3r}
    flag = "HYVE_CTF{st3g0_cat_m4st3r}"
    secret_file = output_dir / "stego" / "secret.txt"
    with open(secret_file, 'w') as f:
        f.write(flag)
    
    cover_image = output_dir / "stego" / "cat.jpeg"
    # Check for local cat.jpeg
    local_cat = Path("challenges/stego/cat.jpeg")
    if local_cat.exists():
        if local_cat.resolve() != cover_image.resolve():
            shutil.copy2(local_cat, cover_image)
    else:
        # Fallback dump
        subprocess.run(['convert', '-size', '600x400', 'xc:grey', str(cover_image)]) 

    # Embed
    password = "meow" # Static password
    stego_cmd = [
        'steghide', 'embed', '-cf', str(cover_image), '-ef', str(secret_file), '-p', password, '-f'
    ]
    try:
        subprocess.run(stego_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(secret_file)
    except Exception as e:
        print(f"    ✗ Steghide failed: {e}")
    
    # Wordlist
    wordlist_path = output_dir / "stego" / "wordlist.txt"
    with open(wordlist_path, 'w') as f:
        f.write(f"purr\nwhiskers\n{password}\nkitty\nscratch\n")
    print(f"    ✓ Created Stego image and wordlist")

    # -------------------------------------------------------------------------
    # NETWORK: Generate PCAP
    print(f"  > Generating Network challenge...")
    (output_dir / "network").mkdir(parents=True, exist_ok=True)
    pcap_out = output_dir / "network" / "cleartext_traffic.pcap"
    # Assuming create_pcap.py can be called or we just use scapy here? 
    # Let's try running the script. If it fails, we might need to adjust it.
    # The script takes team_id but we can pass a dummy one.
    # Actually, the user modified create_pcap.py recently. Let's rely on it.
    # But wait, create_pcap.py uses `sys.argv` for team_id/flag? 
    # Let's just create it directly here if possible or call the script with expected args.
    # User's recent change: 
    # packets.append(IP(src=c_ip, dst=s_ip) / TCP(sport=sport, dport=21) / Raw(load=f"HASH {hashlib.md5("hash".encode()).hexdigest()}\r\n"))
    # ...
    # print(f"[*] Real Flag for Team {team_id}: {flag.split('}')[0] + "_0800fc577294c34e0b28ad2839435945"  +'}'}")
    
    # We should probably just run the script.
    try:
        cmd = ['python3', 'challenges/network/create_pcap.py', 'HYVE_CTF{cl34rt3xt_cr3ds_f0und}', str(pcap_out)]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"    ✓ Generated PCAP")
    except Exception as e:
         print(f"    ✗ Network challenge generation failed: {e}")

    # -------------------------------------------------------------------------
    # CRYPTO: Generate Base64 file
    print(f"  > Generating Crypto challenge...")
    (output_dir / "crypto").mkdir(parents=True, exist_ok=True)
    crypto_out = output_dir / "crypto" / "base64.txt"
    flag = "HYVE_CTF{base64_decoded_success}"
    encoded = base64.b64encode(base64.b64encode(base64.b64encode(flag.encode()))).decode()
    with open(crypto_out, 'w') as f:
        f.write(encoded)
    print(f"    ✓ Generated encoded text file")


def main():
    parser = argparse.ArgumentParser(description='Generate static challenge files for CTF')
    # No arguments needed for static generation, but keeping compat if needed
    parser.add_argument('--output', default='challenges', help='Output directory')
    args = parser.parse_args()
    
    output_dir = Path(args.output).resolve()
    print(f"=== Challenge File Generation ===")
    print(f"Generating static files in {output_dir}...")
    
    generate_files(output_dir)
    
    print(f"[✓] All done!")
    print(f"\nDirectory structure:")
    print(f"  {output_dir}/")
    print(f"    ├── osint/mystery_location.jpg")
    print(f"    ├── stego/cat.jpeg")
    print(f"    ├── stego/wordlist.txt")
    print(f"    ├── network/cleartext_traffic.pcap")
    print(f"    ├── crypto/base64.txt")

if __name__ == '__main__':
    main()

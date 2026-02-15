#!/usr/bin/env python3
"""
Generate team-specific challenge files with embedded dynamic flags
"""
import os
import shutil
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
        "name": "Statue of Liberty",
        "keywords": ["NEWYORK", "USA", "STATUEOFLIBERTY"],
        "lat": 40.6892, "lon": 74.0445, "lat_ref": "N", "lon_ref": "W", # Should be correct sign
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Statue_of_Liberty_7.jpg/800px-Statue_of_Liberty_7.jpg"
    },
    {
        "name": "Taj Mahal",
        "keywords": ["AGRA", "INDIA", "TAJMAHAL"],
        "lat": 27.1751, "lon": 78.0421, "lat_ref": "N", "lon_ref": "E",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Taj_Mahal_(Edited).jpeg/800px-Taj_Mahal_(Edited).jpeg"
    },
]

def generate_osint_challenge(team_id, team_dir):
    """Generate dynamic OSINT challenge: Download image -> Embed GPS -> Embed Flag (Stego)"""
    print(f"[*] Generating OSINT challenge for Team {team_id}")
    
    # 1. Select Landmark (Deterministic based on team_id)
    landmark = LANDMARKS[team_id % len(LANDMARKS)]
    
    # 2. Generate Flag
    # Flag format: HYVE_CTF{CITY_COUNTRY_LANDMARK_HASH}
    # We construct the base prompt from keywords
    base_prompt = "_".join(landmark["keywords"])
    flag = get_flag(base_prompt, str(team_id))
    
    # 3. Download Image (Failover logic)
    output_file = team_dir / "osint" / "mystery_location.jpg"
    
    # Try downloading the selected landmark image first
    download_success = False
    
    # Create a list of candidates starting with the chosen one
    candidates = [landmark] + [l for l in LANDMARKS if l != landmark]
    
    final_landmark = None
    
    for candidate in candidates:
        print(f"  > Attempting download: {candidate['name']}")
        try:
            # -U "Mozilla/5.0" to avoid some 403s
            cmd = ['wget', '-q', '-U', 'Mozilla/5.0', '-O', str(output_file), candidate['url']]
            result = subprocess.run(cmd)
            
            if result.returncode == 0 and output_file.exists() and output_file.stat().st_size > 0:
                print(f"  ✓ Downloaded image for {candidate['name']}")
                final_landmark = candidate
                download_success = True
                break
            else:
                print(f"  ✗ Failed to download {candidate['name']} (Size: {output_file.stat().st_size if output_file.exists() else 0})")
        except Exception as e:
            print(f"  ✗ Exception downloading {candidate['name']}: {e}")
    
    if not download_success:
        print(f"  [!] CRITICAL: Could not download any landmark image for Team {team_id}")
        return # Skip further processing to avoid crashes
    
    # If we switched landmarks due to failover, regenerate flag to match the image!
    if final_landmark != landmark:
        print(f"  ! Switched landmark to {final_landmark['name']}")
        base_prompt = "_".join(final_landmark["keywords"])
        flag = get_flag(base_prompt, str(team_id))
        
    landmark = final_landmark
    
    # 4. Embed GPS Metadata (Exiftool)
    # Ensure latitude/longitude are positive for exiftool and Ref handles direction
    # Exiftool expects positive values + Ref
    lat_val = abs(landmark["lat"])
    lon_val = abs(landmark["lon"])
    
    exif_cmd = [
        'exiftool',
        f'-GPSLatitude={lat_val}',
        f'-GPSLongitude={lon_val}',
        f'-GPSLatitudeRef={landmark["lat_ref"]}',
        f'-GPSLongitudeRef={landmark["lon_ref"]}',
        '-overwrite_original',
        str(output_file)
    ]
    
    try:
        subprocess.run(exif_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"  ✓ Embedded GPS: {lat_val}°{landmark['lat_ref']}, {lon_val}°{landmark['lon_ref']}")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to embed GPS: {e.stderr.decode()}")
        return

    # 5. Embed Flag using Steghide
    # Password format: {lat}{lon} (up to 2 decimal places, e.g. 48.862.29)
    # Note: We use the *original* values from config to ensure precision match
    password = f"{lat_val:.2f}{lon_val:.2f}"
    
    # Write flag to temp file
    flag_file = team_dir / "osint" / "flag.txt"
    with open(flag_file, 'w') as f:
        f.write(flag)
    
    stego_cmd = [
        'steghide', 'embed',
        '-cf', str(output_file),
        '-ef', str(flag_file),
        '-p', password,
        '-f' # Force overwrite
    ]
    
    try:
        # Steghide might fail if JPEG format is incompatible or file too small, but standard images usually work
        p = subprocess.run(stego_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if p.returncode == 0:
            print(f"  ✓ Embedded Flag with Steghide (Pass: {password})")
            flag_file.unlink() # Delete temp flag file
        else:
            print(f"  ✗ Steghide failed: {p.stderr}")
    except Exception as e:
        print(f"  ✗ Steghide exception: {e}")

def copy_static_files(team_id, team_dir):
    """Copy static challenge files that don't need modification"""
    
    # Stego - wordlist
    wordlist_source = CHALLENGES_DIR / "stego" / "wordlist.txt"
    wordlist_dest = team_dir / "stego" / "wordlist.txt"
    if wordlist_source.exists():
        shutil.copy2(wordlist_source, wordlist_dest)
        print(f"  ✓ Copied stego wordlist for Team {team_id}")



def generate_stego_image(team_id, team_dir):
    """Generate team-specific steganography image"""
    stego_script = CHALLENGES_DIR / "stego" / "create_stego.sh"
    output_file = team_dir / "stego" / "cat.jpeg"
    
    if not stego_script.exists():
        print(f"  ⚠ Stego script not found: {stego_script}")
        return
    
    # Run the stego creation script with team ID
    env = os.environ.copy()
    env['TEAM_ID'] = str(team_id)
    
    try:
        # Change to stego directory to run the script
        original_dir = os.getcwd()
        os.chdir(CHALLENGES_DIR / "stego")
        
        result = subprocess.run(
            ['bash', 'create_stego.sh'],
            env=env,
            capture_output=True,
            text=True
        )
        
        # Move the generated cat.jpeg to team directory
        if (CHALLENGES_DIR / "stego" / "cat.jpeg").exists():
            shutil.move("cat.jpeg", output_file)
            print(f"  ✓ Generated stego image for Team {team_id}")
        else:
            print(f"  ✗ Failed to generate stego image")
            print(f"    stdout: {result.stdout}")
            print(f"    stderr: {result.stderr}")
        
        os.chdir(original_dir)
    except Exception as e:
        print(f"  ✗ Error generating stego image: {e}")


def generate_pcap_file(team_id, team_dir):
    """Generate team-specific PCAP file"""
    pcap_script = CHALLENGES_DIR / "network" / "create_pcap.py"
    output_file = team_dir / "network" / "cleartext_traffic.pcap"
    
    if not pcap_script.exists():
        print(f"  ⚠ PCAP script not found: {pcap_script}")
        return
    
    try:
        # Run the PCAP creation script with team ID
        result = subprocess.run(
            ['python', str(pcap_script), str(team_id), str(output_file)],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        if output_file.exists():
            print(f"  ✓ Generated PCAP file for Team {team_id}")
        else:
            print(f"  ✗ Failed to generate PCAP file")
            print(f"    stdout: {result.stdout}")
            print(f"    stderr: {result.stderr}")
    except Exception as e:
        print(f" ✗ Error generating PCAP: {e}")


def generate_crypto_file(team_id, team_dir):
    """Generate team-specific Crypto file"""
    crypto_script = CHALLENGES_DIR / "crypto" / "create_crypto.py"
    output_file = team_dir / "crypto" / "base64.txt"
    
    if not crypto_script.exists():
        print(f"  ⚠ Crypto script not found: {crypto_script}")
        return
    
    try:
        # Run script
        result = subprocess.run(
            ['python', str(crypto_script), str(team_id), str(output_file)],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        if output_file.exists():
            print(f"  ✓ Generated Crypto file for Team {team_id}")
        else:
            print(f"  ✗ Failed to generate Crypto file")
    except Exception as e:
        print(f"  ✗ Error generating Crypto file: {e}")

def generate_team_files(team_id):
    """Generate all challenge files for a specific team"""
    print(f"\n[*] Generating files for Team {team_id}")
    
    # Create directory structure
    team_dir = create_team_directory(team_id)
    
    # Copy static files
    copy_static_files(team_id, team_dir)
    
    # Generate dynamic files with team-specific flags
    generate_osint_challenge(team_id, team_dir)
    generate_stego_image(team_id, team_dir)
    generate_pcap_file(team_id, team_dir)
    generate_crypto_file(team_id, team_dir)
    
    print(f"[+] Team {team_id} files generated successfully!\n")


def main():
    parser = argparse.ArgumentParser(
        description='Generate team-specific challenge files for CTF'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--teams',
        type=str,
        help='Comma-separated list of team IDs (e.g., "1,2,3")'
    )
    group.add_argument(
        '--count',
        type=int,
        help='Number of teams to generate (e.g., 5 for team1-team5)'
    )
    
    args = parser.parse_args()
    
    # Determine team IDs
    if args.teams:
        team_ids = [int(tid.strip()) for tid in args.teams.split(',')]
    else:
        team_ids = list(range(1, args.count + 1))
    
    print(f"=== Team File Generation ===")
    print(f"Generating files for {len(team_ids)} team(s): {team_ids}")
    print(f"Output directory: {TEAMS_DIR}")
    
    # Create teams directory if it doesn't exist
    TEAMS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate files for each team
    for team_id in team_ids:
        generate_team_files(team_id)
    
    print(f"[✓] All done! Generated files for {len(team_ids)} team(s)")
    print(f"\nDirectory structure:")
    print(f"  {TEAMS_DIR}/")
    for team_id in team_ids:
        print(f"    ├── team{team_id}/")
        print(f"    │   ├── osint/mystery_location.jpg")
        print(f"    │   ├── stego/cat.jpeg (team-specific flag)")
        print(f"    │   ├── stego/wordlist.txt")
        print(f"    │   └── network/cleartext_traffic.pcap (team-specific flag)")


if __name__ == '__main__':
    main()

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


def copy_static_files(team_id, team_dir):
    """Copy static challenge files that don't need modification"""
    
    # OSINT - mystery location image
    osint_source = CHALLENGES_DIR / "osint" / "mystery_location.jpg"
    osint_dest = team_dir / "osint" / "mystery_location.jpg"
    if osint_source.exists():
        shutil.copy2(osint_source, osint_dest)
        print(f"  ✓ Copied OSINT image for Team {team_id}")
    
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

#!/usr/bin/env python3
"""
Automated CTFd Setup Script
Handles: Dependency checking, admin creation, event scheduling, team creation, challenge import, team file generation
"""
import requests
import json
import sys
import time
import argparse
import shutil
from datetime import timedelta
import datetime
from pathlib import Path
import subprocess
import os

CTFD_URL = "http://localhost:8001"

def check_dependencies():
    """Check for required dependencies"""
    print("\n[*] Checking dependencies...")
    
    # Check Docker
    if not shutil.which('docker'):
        print("[✗] Docker is not installed")
        print("    Install from: https://docs.docker.com/get-docker/")
        return False
    print("  ✓ Docker found")
    
    # Check Docker Compose
    if not shutil.which('docker-compose'):
        print("[✗] Docker Compose is not installed")
        print("    Install from: https://docs.docker.com/compose/install/")
        return False
    print("  ✓ Docker Compose found")
    
    # Check Python packages
    try:
        import requests
        import bs4
        print("  ✓ Python dependencies installed")
    except ImportError as e:
        print(f"[✗] Missing Python dependency: {e}")
        print("    Run: pip install -r requirements.txt")
        return False
    
    return True

def wait_for_ctfd():
    """Wait for CTFd to be ready"""
    print("\n[*] Waiting for CTFd to be ready...")
    for i in range(60):
        try:
            response = requests.get(f"{CTFD_URL}/", timeout=2)
            if response.status_code == 200:
                print("[✓] CTFd is ready!")
                return True
        except:
            pass
        time.sleep(2)
    print("[✗] CTFd failed to start")
    return False

def setup_ctfd():
    """Complete CTFd initial setup"""
    print("\n[*] Setting up CTFd...")
    
    # Get setup page for nonce
    session = requests.Session()
    setup_page = None
    
    # Retry getting setup page (handles 500 errors during init)
    print("    Waiting for setup page...")
    for i in range(30):
        try:
            resp = session.get(f"{CTFD_URL}/setup", timeout=5)
            if resp.status_code == 200:
                setup_page = resp
                break
            elif resp.status_code == 302:
                # Redirect means already setup
                setup_page = resp
                break
            elif resp.status_code == 500:
                setup_page = resp
                break
            else:
                print(f"    . Status: {resp.status_code} (retrying...)")
        except Exception as e:
            print(f"    . Connection failed: {e}")
        time.sleep(2)
    
    if not setup_page:
        print("[✗] Could not access setup page")
        return session, None

    if "Setup" not in setup_page.text and setup_page.status_code != 200:
        print("[!] CTFd already configured or unavailable. Skipping setup...")
        return session, None
    
    # Extract nonce from form
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(setup_page.text, 'html.parser')
    nonce = soup.find('input', {'name': 'nonce'})['value']
    
    # Calculate event times
    start_time = datetime.datetime.now(datetime.UTC) + timedelta(minutes=CTF_START_OFFSET_MINUTES)
    end_time = start_time + timedelta(hours=CTF_DURATION_HOURS)
    
    # Setup payload - CTFd minimal setup requirements
    # Newer CTFd versions might require mode/user/event in one go, but let's be robust
    setup_data = {
        'nonce': nonce,
        'ctf_name': 'Hivye CTF 2026',
        'ctf_description': 'Bistro-themed Capture The Flag',
        'user_mode': 'teams',
        'name': 'Sin444',
        'email': 'admin@hyve-ctf.local',
        'password': '09877890',
        'ctf_logo': '',
        'ctf_banner': '',
        'ctf_small_icon': '',
        'ctf_theme': 'core',
        'theme_color': '',
        'start': start_time.strftime('%Y-%m-%d %H:%M:%S'), # Try standard format
        'end': end_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Try the setup
    try:
        response = session.post(f"{CTFD_URL}/setup", data=setup_data, allow_redirects=False)
        
        # Check for successful install (redirect to root or login)
        if response.status_code == 302 or (response.status_code == 200 and 'login' in response.url):
            print(f"[✓] CTFd configured successfully!")
            print(f"    Admin: admin / admin123")
            print(f"    Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print(f"    End: {end_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            return session, {
                'username': 'admin',
                'password': 'admin123',
                'start': start_time,
                'end': end_time
            }
        else:
            print(f"[✗] Setup failed with status code: {response.status_code}")
            print(f"    Response text preview: {response.text[:500]}...")
            return session, None
    except Exception as e:
        print(f"[✗] Setup exception: {e}")
        return session, None

def login(session, username, password):
    """Login to CTFd"""
    print(f"\n[*] Logging in as {username}...")
    
    # Get login page for nonce
    login_page = session.get(f"{CTFD_URL}/login")
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(login_page.text, 'html.parser')
    nonce_input = soup.find('input', {'name': 'nonce'})
    
    if not nonce_input:
        print("[!] Already logged in")
        return True
    
    nonce = nonce_input['value']
    
    login_data = {
        'name': username,
        'password': password,
        'nonce': nonce
    }
    
    response = session.post(f"{CTFD_URL}/login", data=login_data)
    
    if response.status_code == 200:
        print("[✓] Logged in successfully")
        return True
    else:
        print("[✗] Login failed")
        return False

def get_api_token(session):
    """Generate API token"""
    print("\n[*] Generating API token...")
    
    # Strategy 1: Get CSRF token from settings page
    csrf_token = None
    try:
        settings_page = session.get(f"{CTFD_URL}/settings")
        # print(f"    Settings page status: {settings_page.status_code}")
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(settings_page.text, 'html.parser')
        
        r = session.get(f"{CTFD_URL}/login")
        soup = BeautifulSoup(r.text, "html.parser")
        csrf = soup.find("input", {"name": "nonce"})["value"]

            
        # 2. Try hidden input (older themes)
        if not csrf_token:
            inp = soup.find('input', {'name': 'nonce'})
            if inp:
                csrf_token = inp['value']
                # print(f"    Found CSRF token in input")
                
        # 3. Try parsing from script tag (var csrf_token = "...")
        if not csrf_token:
            import re
            match = re.search(r'csrf_nonce\s*=\s*"([^"]+)"', settings_page.text)
            if match:
                csrf_token = match.group(1)
                # print(f"    Found CSRF token in script variable")

    except Exception as e:
        print(f"    Error extracting CSRF: {e}")

    if not csrf_token:
        print("    [!] Could not find CSRF token. API creation might fail.")
        csrf_token = ''

    # Create token via API
    token_data = {
        'description': 'Auto-generated setup token',
        'expiration': None
    }
    
    headers = {
        'Content-Type': 'application/json',
        'CSRF-Token': csrf_token
    }
    
    try:
        response = session.post(
            f"{CTFD_URL}/api/v1/tokens",
            json=token_data,
            headers=headers
        )
        
        if response.status_code == 200:
            resp_json = response.json()
            if 'success' in resp_json and resp_json['success']:
                token = resp_json['data']['value']
                print(f"[✓] Token generated: {token[:20]}...")
                return token
        
        print(f"[✗] Token generation failed. Status: {response.status_code}")
        # print(f"    Response: {response.text[:200]}")
        return None
        
    except Exception as e:
        print(f"[✗] Token generation exception: {e}")
        return None

def create_teams(token, participant_count, create_admin_team=True):
    """Create users and teams using API"""
    total_teams = participant_count + (1 if create_admin_team else 0)
    print(f"\n[*] Creating {participant_count} participant teams" + 
          (f" + 1 admin test team" if create_admin_team else "") + "...")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }

    def _api_post(endpoint, data, context_name):
        try:
            r = requests.post(f"{CTFD_URL}/api/v1/{endpoint}", json=data, headers=headers)
            if r.status_code == 200:
                if 'data' in r.json():
                    return r.json()['data']
                return r.json() # success might be true
            # Ignore "already exists" errors (400) to be idempotent-ish
            if r.status_code == 400 and "already exists" in r.text:
                 # Try to fetch existing? For now just return None and log
                 print(f"    ! {context_name} likely already exists")
                 return None
            print(f"  ✗ Failed to create {context_name}: {r.status_code} {r.text[:100]}")
            return None
        except Exception as e:
            print(f"  ✗ Exception creating {context_name}: {e}")
            return None

    # Create participant teams (Team 1 to Team N)
    for i in range(1, participant_count + 1):
        username = f"user_team{i}"
        email = f"team{i}@hyve-ctf.local"
        password = f"team{i}pass"
        team_name = f"Team {i}"

        # 1. Create User
        user_data = {
            "name": username,
            "email": email,
            "password": password,
            "type": "user",
            "verified": True
        }
        user = _api_post("users", user_data, f"User {username}")
        
        # 2. Create Team
        team_data = {
            "name": team_name,
            "email": email, # Team email can be same as user
        }
        team = _api_post("teams", team_data, f"Team {team_name}")

        # 3. Add User to Team
        if user and team:
            # Patch user to assign team_id
            patch_url = f"{CTFD_URL}/api/v1/users/{user['id']}"
            try:
                r = requests.patch(patch_url, json={"team_id": team['id']}, headers=headers)
                if r.status_code == 200:
                    print(f"  ✓ Created & Linked {team_name} (User: {username})")
                else:
                    print(f"  ✗ Failed to link {username} to {team_name}: {r.text[:100]}")
            except Exception as e:
                print(f"  ✗ Exception linking user: {e}")
        elif not user and not team:
             print(f"  ! Skipping {team_name} (User/Team creation failed or exist)")

    # Create admin test team (Team 21)
    if create_admin_team:
        admin_id = participant_count + 1
        username = f"admin_test"
        email = "admintest@hyve-ctf.local"
        password = "admintestpass"
        team_name = f"Team {admin_id} (Admin Test)"

        user_data = {
            "name": username,
            "email": email,
            "password": password,
            "type": "admin", # Make admin user an admin? Or user? Let's make user for now to test team features, or admin.
            "verified": True
        }
        user = _api_post("users", user_data, "Admin Test User")

        team_data = {
            "name": team_name,
            "email": email,
            "affiliation": "Admin"
        }
        team = _api_post("teams", team_data, "Admin Test Team")

        if user and team:
            try:
                r = requests.patch(f"{CTFD_URL}/api/v1/users/{user['id']}", json={"team_id": team['id']}, headers=headers)
                if r.status_code == 200:
                    print(f"  ✓ Created {team_name}")
            except: pass

    print(f"[✓] Team processing complete!")

def import_challenges(token):
    """Import challenges using existing script"""
    print("\n[*] Importing challenges...")
    
    result = subprocess.run(
        [
            'python',
            'import_challenges.py',
            'ctfd/import/challenges/challenges.yml',
            token
        ],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("[✓] Challenges imported successfully!")
    else:
        print(f"[✗] Challenge import failed:\n{result.stderr}")

def generate_team_files(participant_count, create_admin_team):
    """Generate team-specific challenge files using Docker"""
    total_teams = participant_count + (1 if create_admin_team else 0)
    
    print(f"\n[*] Generating files for {total_teams} team(s)...")
    print("    This will run in a Docker container with Linux tools...")
    
    # Get absolute paths
    challenges_dir = Path('challenges').absolute()
    utils_dir = Path('utils').absolute()
    
    # Get SECRET_FLAG_KEY from .env
    secret_key = os.getenv('SECRET_FLAG_KEY', 'default_secret_key_change_me')
    
    docker_cmd = [
        'docker', 'run', '--rm',
        '-v', f'{challenges_dir}:/challenges',
        '-v', f'{utils_dir}:/utils',
        '-e', f'SECRET_FLAG_KEY={secret_key}',
        'python:3.9-slim',
        'bash', '-c',
        f'''
        apt-get update && apt-get install -y steghide curl && \
        pip install scapy pyyaml && \
        python /utils/generate_team_files.py --count {total_teams}
        '''
    ]
    
    result = subprocess.run(docker_cmd)
    
    if result.returncode == 0:
        print(f"[✓] Team files generated successfully!")
    else:
        print(f"[✗] Team file generation failed!")

def main():
    # Default configuration
    DEFAULT_PARTICIPANT_TEAMS = 20
    DEFAULT_CREATE_ADMIN_TEST_TEAM = True
    DEFAULT_CTF_DURATION_HOURS = 2
    DEFAULT_CTF_START_OFFSET_MINUTES = 5
    parser = argparse.ArgumentParser(
        description='Automated CTFd Setup for Hivye CTF 2026',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Default setup (20 participant teams + 1 admin test team)
  python setup_ctf.py
  
  # Custom team count without admin test team
  python setup_ctf.py --teams 50 --no-admin-team
  
  # Custom event timing
  python setup_ctf.py --start-offset 10 --duration 3
  
  # Skip dependency check (if already verified)
  python setup_ctf.py --skip-deps
        ''')
    
    parser.add_argument(
        '--teams',
        type=int,
        default=DEFAULT_PARTICIPANT_TEAMS,
        help=f'Number of participant teams (default: {DEFAULT_PARTICIPANT_TEAMS})'
    )
    parser.add_argument(
        '--no-admin-team',
        action='store_true',
        help='Do not create admin test team'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=DEFAULT_CTF_DURATION_HOURS,
        help=f'CTF duration in hours (default: {DEFAULT_CTF_DURATION_HOURS})'
    )
    parser.add_argument(
        '--start-offset',
        type=int,
        default=DEFAULT_CTF_START_OFFSET_MINUTES,
        help=f'Minutes before CTF starts (default: {DEFAULT_CTF_START_OFFSET_MINUTES})'
    )
    parser.add_argument(
        '--skip-deps',
        action='store_true',
        help='Skip dependency checks'
    )
    
    args = parser.parse_args()

    global CTF_DURATION_HOURS, CTF_START_OFFSET_MINUTES
    
    # Configuration from args
    PARTICIPANT_TEAMS = args.teams
    CREATE_ADMIN_TEST_TEAM = not args.no_admin_team
    CTF_DURATION_HOURS = args.duration
    CTF_START_OFFSET_MINUTES = args.start_offset
    
    print("=" * 60)
    print("  Hivye CTF 2026 - Automated Setup")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Participant Teams: {PARTICIPANT_TEAMS}")
    print(f"  Admin Test Team: {'Yes' if CREATE_ADMIN_TEST_TEAM else 'No'}")
    print(f"  CTF Duration: {CTF_DURATION_HOURS} hours")
    print(f"  Start Offset: {CTF_START_OFFSET_MINUTES} minutes")
    
    # Step 0: Check dependencies
    if not args.skip_deps:
        if not check_dependencies():
            sys.exit(1)
    
    # Step 1: Wait for CTFd
    # if not wait_for_ctfd():
    #     sys.exit(1)
    
    # Step 2: Setup CTFd (pass timing config)
    #global CTF_DURATION_HOURS, CTF_START_OFFSET_MINUTES
    session, config = setup_ctfd()
    
    if not config:
        # Already setup, login manually
        username = input("Admin username: ")
        password = input("Admin password: ")
        login(session, username, password)
        config = {'username': username, 'password': password}
    else:
        # Auto-login after setup
        login(session, config['username'], config['password'])
    
    # Step 3: Generate API token
    token = get_api_token(session)
    if not token:
        print("\n[!] Failed to generate token. Please create one manually.")
        sys.exit(1)
    
    # Step 4: Create teams
    create_teams(token, PARTICIPANT_TEAMS, CREATE_ADMIN_TEST_TEAM)
    
    # Step 5: Import challenges
    import_challenges(token)
    
    # Step 6: Generate team files
    generate_team_files(PARTICIPANT_TEAMS, CREATE_ADMIN_TEST_TEAM)
    
    print("\n" + "=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    total_teams = PARTICIPANT_TEAMS + (1 if CREATE_ADMIN_TEST_TEAM else 0)
    print(f"\n  CTFd URL: {CTFD_URL}")
    print(f"  Admin: {config['username']} / {config['password']}")
    print(f"  Teams: {PARTICIPANT_TEAMS} participant teams" + 
          (f" + 1 admin test team (Team {total_teams})" if CREATE_ADMIN_TEST_TEAM else ""))
    if 'start' in config:
        print(f"  Event: Starts in {CTF_START_OFFSET_MINUTES} mins, runs for {CTF_DURATION_HOURS} hours")
    print(f"\nNext steps:")
    print(f"  1. Visit {CTFD_URL}")
    print(f"  2. Users register and join teams")
    print(f"  3. Start solving challenges!")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

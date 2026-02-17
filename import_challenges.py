#!/usr/bin/env python3
"""
Import challenges from challenges.yml into CTFd
Supports both API token and username/password authentication
"""
import requests
import yaml
import sys
import getpass
from bs4 import BeautifulSoup
from pathlib import Path

CTFD_URL = "http://localhost:8001"


def login_with_credentials(username, password):
    """Login to CTFd and return session"""
    session = requests.Session()
    
    # Get login page to extract nonce
    login_page = session.get(f"{CTFD_URL}/login")
    soup = BeautifulSoup(login_page.text, 'html.parser')
    nonce = soup.find('input', {'name': 'nonce'})['value']
    
    # Login
    login_data = {
        'name': username,
        'password': password,
        'nonce': nonce
    }
    
    response = session.post(f"{CTFD_URL}/login", data=login_data)
    
    if 'incorrect' in response.text.lower() or response.status_code != 200:
        print("[✗] Login failed! Check your credentials.")
        sys.exit(1)
    
    print("[✓] Logged in successfully")
    return session


def import_challenges(challenges_file, session_or_token, use_token=False):
    """Import challenges from YAML file"""
    
    if use_token:
        headers = {
            "Authorization": f"Token {session_or_token}",
            "Content-Type": "application/json"
        }
        session = requests.Session()
    else:
        session = session_or_token
        headers = {"Content-Type": "application/json"}
    
    # Load challenges
    with open(challenges_file, 'r') as f:
        data = yaml.safe_load(f)
    
    print(f"\n[*] Loaded {len(data.get('challenges', []))} challenges")
    
    for challenge in data.get('challenges', []):
        print(f"\n[*] Importing: {challenge['name']}")
        
        # Create challenge
        chal_data = {
            "name": challenge['name'],
            "category": challenge['category'],
            "description": challenge['description'],
            "value": challenge['value'],
            "state": challenge.get('state', 'visible'),
            "type": "standard"
        }
        
        # Try to create challenge
        response = session.post(
            f"{CTFD_URL}/api/v1/challenges",
            json=chal_data,
            headers=headers  
        )
        
        challenge_id = None
        if response.status_code == 200:
            challenge_id = response.json()['data']['id']
            print(f"  ✓ Created challenge (ID: {challenge_id})")
        else:
            # Check if it already exists
            print(f"  ⚠ Create failed ({response.status_code}), checking if exists...")
            # Fetch all challenges to find ID by name (inefficient but works)
            # Or simplified: just list challenges and filter
            r = session.get(f"{CTFD_URL}/api/v1/challenges", headers=headers)
            if r.status_code == 200:
                chals = r.json()['data']
                for c in chals:
                    if c['name'] == challenge['name']:
                        challenge_id = c['id']
                        print(f"  ✓ Found existing challenge (ID: {challenge_id})")
                        break
        
        if challenge_id:
            # Add flags
            for flag_item in challenge.get('flags', []):
                # Handle both string flags and dict with type
                if isinstance(flag_item, dict):
                    flag_content = flag_item.get('flag')
                    flag_type = flag_item.get('type', 'static')
                else:
                    flag_content = flag_item
                    flag_type = 'static'
                
                flag_data = {
                    "challenge_id": challenge_id,
                    "content": flag_content,
                    "type": flag_type
                }
                # Check duplication? CTFd allows multiple flags.
                # Just try to add.
                session.post(
                    f"{CTFD_URL}/api/v1/flags",
                    json=flag_data,
                    headers=headers
                )
            
            # Add hints if any
            for hint in challenge.get('hints', []):
                hint_data = {
                    "challenge_id": challenge_id,
                    "content": hint['content'],
                    "cost": hint.get('cost', 0)
                }
                session.post(
                    f"{CTFD_URL}/api/v1/hints",
                    json=hint_data,
                    headers=headers
                )
            if challenge.get('hints'):
                print(f"  ✓ Processed {len(challenge['hints'])} hint(s)")
            
            # Upload files if any
            for file_entry in challenge.get('files', []):
                file_path = file_entry['location']
                # Remove leading slash if present to make it relative
                if file_path.startswith('/'):
                     file_path = file_path[1:]
                
                path_obj = Path(file_path)
                if path_obj.exists():
                     print(f"  > Uploading file: {file_path}")
                     with open(file_path, 'rb') as f:
                         files = {'file': (path_obj.name, f)}
                         data = {'challenge_id': challenge_id, 'type': 'challenge'}
                         
                         # CTFd API v1
                         # POST /api/v1/files
                         upload_headers = {}
                         if use_token:
                             upload_headers['Authorization'] = f"Token {session_or_token}"
                         else:
                             # For session auth, we need the nonce / CSRF token
                             csrf_token = session.cookies.get('nonce')
                             if csrf_token:
                                 upload_headers['CSRF-Token'] = csrf_token

                         resp = session.post(
                             f"{CTFD_URL}/api/v1/files",
                             files=files,
                             data=data,
                             headers=upload_headers
                         )
                         if resp.status_code == 200:
                             print(f"    ✓ Uploaded {path_obj.name}")
                         else:
                             print(f"    ✗ Failed to upload {path_obj.name}: {resp.text}")
                else:
                    print(f"  ⚠ File not found locally: {file_path}")

        else:
            print(f"  ✗ Failed to create or find challenge: {response.text}")


if __name__ == "__main__":
    print("=" * 50)
    print("CTFd Challenge Importer")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python import_challenges.py <challenges.yml>")
        print("  python import_challenges.py <challenges.yml> <admin_token>")
        sys.exit(1)
    
    challenges_file = sys.argv[1]
    
    # Check if token provided
    if len(sys.argv) == 3:
        # Use token
        admin_token = sys.argv[2]
        print("\n[*] Using API token authentication")
        import_challenges(challenges_file, admin_token, use_token=True)
    else:
        # Use login credentials
        print("\n[*] Using username/password authentication")
        username = input("Admin username: ")
        password = getpass.getpass("Admin password: ")
        
        session = login_with_credentials(username, password)
        import_challenges(challenges_file, session, use_token=False)
    
    print("\n" + "=" * 50)
    print("[✓] Import complete!")
    print("=" * 50)

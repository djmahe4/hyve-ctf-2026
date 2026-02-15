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
            "type": challenge.get('type', 'standard')
        }
        
        # Add dynamic challenge fields if type is dynamic
        if challenge.get('type') == 'decay' or challenge.get('type') == 'dynamic':
            chal_data['type'] = 'dynamic'  # CTFd uses 'dynamic' not 'decay'
            chal_data['initial'] = challenge['value']
            chal_data['minimum'] = challenge.get('minimum', challenge['value'] // 2)  # Default: half of initial
            chal_data['decay'] = challenge.get('decay', 25)  # Default decay rate
        
        response = session.post(
            f"{CTFD_URL}/api/v1/challenges",
            json=chal_data,
            headers=headers  
        )
        
        if response.status_code == 200:
            challenge_id = response.json()['data']['id']
            print(f"  ✓ Created challenge (ID: {challenge_id})")
            
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
                session.post(
                    f"{CTFD_URL}/api/v1/flags",
                    json=flag_data,
                    headers=headers
                )
            print(f"  ✓ Added {len(challenge.get('flags', []))} flag(s)")
            
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
                print(f"  ✓ Added {len(challenge['hints'])} hint(s)")
        else:
            print(f"  ✗ Failed: {response.text}")


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

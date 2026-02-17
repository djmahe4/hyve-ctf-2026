import requests
import sys
import json
from bs4 import BeautifulSoup

CTFD_URL = "http://0.0.0.0:8001"
PROXY_URL = "http://0.0.0.0:8082"

def login(session, username, password):
    print(f"[*] Logging in as {username}...")
    try:
        r = session.get(f"{CTFD_URL}/login")
        soup = BeautifulSoup(r.text, 'html.parser')
        nonce = soup.find('input', {'name': 'nonce'})['value']
        
        data = {
            'name': username,
            'password': password,
            'nonce': nonce
        }
        r = session.post(f"{CTFD_URL}/login", data=data)
        if r.status_code == 200 and "Incorrect" not in r.text:
            print(f"  ✓ Login successful")
            return True
        else:
            print(f"  ✗ Login failed")
            return False
    except Exception as e:
        print(f"  ✗ Login error: {e}")
        return False

def check_challenges(session):
    print(f"[*] Checking challenges page...")
    try:
        r = session.get(f"{CTFD_URL}/challenges")
        if r.status_code == 200:
            print(f"  ✓ Challenges page loaded (200 OK)")
            # Parse specific challenges if possible, but 200 is good start
            return True
        else:
            print(f"  ✗ Challenges page failed: {r.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Challenges page error: {e}")
        return False

def test_file_proxy(session, team_id=1):
    print(f"[*] Testing File Proxy for Team {team_id}...")
    
    # Test OSINT file
    url = f"{PROXY_URL}/files/osint/mystery_location.jpg"
    print(f"  > Fetching {url}")
    try:
        # We need to pass the session cookie to the proxy
        cookies = session.cookies.get_dict()
        r = requests.get(url, cookies=cookies)
        
        if r.status_code == 200:
            print(f"  ✓ Download successful ({len(r.content)} bytes)")
        else:
            print(f"  ✗ Download failed: {r.status_code}")
            try:
                print(f"    Error: {r.json()}")
            except:
                print(f"    Body: {r.text[:100]}")
    except Exception as e:
        print(f"  ✗ Proxy error: {e}")

import argparse

def main():
    parser = argparse.ArgumentParser(description='Verify CTFd Challenges')
    parser.add_argument('--url', default="http://0.0.0.0:8001", help='CTFd URL')
    parser.add_argument('--proxy-url', default="http://0.0.0.0:8082", help='File Proxy URL')
    parser.add_argument('--username', default="user_team1", help='Team User')
    parser.add_argument('--password', default="team1pass", help='Team Password')
    
    args = parser.parse_args()
    
    global CTFD_URL, PROXY_URL
    CTFD_URL = args.url.rstrip('/')
    PROXY_URL = args.proxy_url.rstrip('/')
    
    print(f"[*] Target: {CTFD_URL}")
    print(f"[*] Proxy:  {PROXY_URL}")
    
    session = requests.Session()
    
    # Login
    if not login(session, args.username, args.password):
        print("skipping tests needing auth")
        return

    check_challenges(session)
    test_file_proxy(session)

if __name__ == "__main__":
    main()

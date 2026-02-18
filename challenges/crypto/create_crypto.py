#!/usr/bin/env python3
import base64
import os
import sys

# Import our flag generator
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from utils.flag_gen import get_flag

def create_base64_challenge(team_id="1", output_file="base64_decoded_success.txt"):
    """
    Generates a Base64 challenge file where the flag is encoded thrice.
    """
    # 1. Generate the dynamic flag for this team
    flag = get_flag("base64_decoded_success", team_id)
    
    # 2. Encode thrice
    encoded1 = base64.b64encode(flag.encode()).decode()
    encoded2 = base64.b64encode(encoded1.encode()).decode()
    encoded3 = base64.b64encode(encoded2.encode()).decode()
    
    # 3. Write to file (or print for README update)
    with open(output_file, 'w') as f:
        f.write(encoded3 + "\n\n")
        f.write("Decode this 3 times to get the flag!\n")
    
    print(f"[*] Generated Crypto Challenge for Team {team_id}")
    print(f"[*] Output File: {output_file}")
    print(f"[*] Triple-Encoded String: {encoded3}")
    print(f"[*] Base Flag: {flag}")

if __name__ == "__main__":
    team_id = os.environ.get("TEAM_ID", "1")
    output_file = "base64.txt"
    
    if len(sys.argv) > 1:
        team_id = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        
    create_base64_challenge(team_id, output_file)

#!/usr/bin/env python3
"""
Create PCAP file with FTP credentials for CTF challenge
"""

from scapy.all import *
import random
import sys
import os
import hashlib

# Import our flag generator
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from utils.flag_gen import get_flag, get_fake_flag

def create_pcap(output_file="cleartext_traffic.pcap", team_id="1"):
    """Generate PCAP file with interleaved noise and auth attempts for better realism"""
    packets = []
    
    # Generate flags
    flag = get_flag("cl34rt3xt_cr3ds_f0und", team_id)
    fake_flag = get_fake_flag("cl34rt3xt_cr3ds_f0und")
    
    # Known IPs
    GOOGLE_IPS = ["142.250.190.46", "172.217.16.142"]
    AMAZON_IPS = ["54.239.28.85", "205.251.242.103"]
    LOCAL_SERVERS = ["192.168.1.10", "10.0.0.5", "172.16.0.22"]

    def random_ip():
        return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

    def add_browsing_noise(count=10):
        for _ in range(count):
            src = random_ip()
            dst = random.choice(GOOGLE_IPS + AMAZON_IPS + LOCAL_SERVERS)
            sport = random.randint(1024, 65535)
            dport = random.choice([80, 443])
            # Simulate a simple GET request
            packets.append(IP(src=src, dst=dst) / TCP(sport=sport, dport=dport) / Raw(load="GET / HTTP/1.1\r\nHost: service.io\r\n\r\n"))

    # 1. Initial Activity (Checking mail, news, etc.)
    add_browsing_noise(20)

    # 2. Interleaved Authentication Attempts
    fake_creds = [
        ("guest", "guest"),
        ("support", "support123"),
        ("dev_team", "git_commit_2026"),
    ]
    
    for user, pw in fake_creds:
        # A bit of browsing before each attempt
        add_browsing_noise(random.randint(5, 12))
        
        c_ip = f"192.168.1.{random.randint(100, 200)}"
        s_ip = random.choice(LOCAL_SERVERS)
        sport = random.randint(30000, 60000)
        
        packets.append(IP(src=c_ip, dst=s_ip) / TCP(sport=sport, dport=21) / Raw(load=f"USER {user}\r\n"))
        packets.append(IP(src=s_ip, dst=c_ip) / TCP(sport=21, dport=sport) / Raw(load="331 Password required\r\n"))
        packets.append(IP(src=c_ip, dst=s_ip) / TCP(sport=sport, dport=21) / Raw(load=f"PASS {pw}\r\n"))
        packets.append(IP(src=s_ip, dst=c_ip) / TCP(sport=21, dport=sport) / Raw(load="530 Login incorrect\r\n"))

    # 3. Sustained Browsing (Lunch break?)
    add_browsing_noise(15)

    # 4. Deceptive Attempt (Fake Flag)
    c_ip = f"192.168.1.{random.randint(100, 200)}"
    s_ip = "192.168.1.10"
    sport = random.randint(30000, 60000)
    packets.append(IP(src=c_ip, dst=s_ip) / TCP(sport=sport, dport=21) / Raw(load="USER admin\r\n"))
    packets.append(IP(src=c_ip, dst=s_ip) / TCP(sport=sport, dport=21) / Raw(load=f"HASH {hashlib.md5('NEW_PASSWORD'.encode()).hexdigest()}\r\n"))
    packets.append(IP(src=s_ip, dst=c_ip) / TCP(sport=21, dport=sport) / Raw(load="331 Password required\r\n"))
    packets.append(IP(src=c_ip, dst=s_ip) / TCP(sport=sport, dport=21) / Raw(load=f"PASS {fake_flag}\r\n"))
    packets.append(IP(src=s_ip, dst=c_ip) / TCP(sport=21, dport=sport) / Raw(load="530 Login incorrect\r\n"))
    
    # 5. Quick check on Amazon
    add_browsing_noise(8)

    # 6. REAL Auth Request (The successful one)
    c_ip = "192.168.1.100"
    s_ip = "192.168.1.10"
    sport = 50234
    packets.append(IP(src=c_ip, dst=s_ip) / TCP(sport=sport, dport=21) / Raw(load="USER admin\r\n"))
    packets.append(IP(src=c_ip, dst=s_ip) / TCP(sport=sport, dport=21) / Raw(load=f"HASH {hashlib.md5('hash'.encode()).hexdigest()}\r\n"))
    packets.append(IP(src=s_ip, dst=c_ip) / TCP(sport=21, dport=sport) / Raw(load="331 Password required\r\n"))
    packets.append(IP(src=c_ip, dst=s_ip) / TCP(sport=sport, dport=21) / Raw(load=f"NEW_PASSWORD {flag}\r\n"))
    packets.append(IP(src=s_ip, dst=c_ip) / TCP(sport=21, dport=sport) / Raw(load="230 Login successful\r\n"))
    
    # 7. Final wrap-up noise
    add_browsing_noise(15)
    
    # Write PCAP file
    wrpcap(output_file, packets)
    print(f"[*] PCAP created: {output_file}")
    print(f"[*] Total Packets: {len(packets)}")
    print(f"[*] Real Flag for Team {team_id}: {flag.split('}')[0] + '_0800fc577294c34e0b28ad2839435945'  +'}'}")

if __name__ == '__main__':
    try:
        team_id = os.environ.get("TEAM_ID", "1")
        output_file = "cleartext_traffic.pcap"
        if len(sys.argv) > 1: team_id = sys.argv[1]
        if len(sys.argv) > 2: output_file = sys.argv[2]
        create_pcap(output_file, team_id)
    except Exception as e:
        print(f"Error creating PCAP: {e}")
        import traceback
        traceback.print_exc()

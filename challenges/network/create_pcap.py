#!/usr/bin/env python3
"""
Create PCAP file with FTP credentials for CTF challenge
"""

from scapy.all import *
import random
import sys
import os

# Import our flag generator
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from utils.flag_gen import get_flag

def create_pcap(output_file, team_id="1"):
    """Generate PCAP file with FTP traffic containing flag"""
    packets = []
    
    # Generate the dynamic flag for this team
    flag = get_flag("cl34rt3xt_cr3ds_f0und", team_id)
    
    # FTP client and server IPs
    client_ip = "192.168.1.100"
    server_ip = "192.168.1.10"
    
    # Add FTP packets with credentials
    # Packet 1: USER command
    ftp_user = IP(src=client_ip, dst=server_ip) / TCP(sport=50234, dport=21) / Raw(load="USER admin\r\n")
    packets.append(ftp_user)
    
    # Packet 2: Server response - password required
    ftp_response1 = IP(src=server_ip, dst=client_ip) / TCP(sport=21, dport=50234) / Raw(load="331 Password required\r\n")
    packets.append(ftp_response1)
    
    # Packet 3: PASS command with flag
    ftp_pass = IP(src=client_ip, dst=server_ip) / TCP(sport=50234, dport=21) / Raw(load="PASS HYVE_CTF{cl34rt3xt_cr3ds_f0und_HASH}\r\n")
    packets.append(ftp_pass)
    
    # Packet 4: Server response - login successful
    ftp_response2 = IP(src=server_ip, dst=client_ip) / TCP(sport=21, dport=50234) / Raw(load="230 Login successful\r\n")
    packets.append(ftp_response2)
    
    # Add some random HTTP traffic as noise
    for i in range(50):
        src_ip = f"192.168.1.{random.randint(1, 254)}"
        dst_ip = f"192.168.1.{random.randint(1, 254)}"
        http_packet = IP(src=src_ip, dst=dst_ip) / TCP(sport=random.randint(1024, 65535), dport=80)
        packets.append(http_packet)
    
    # Write PCAP file
    wrpcap('cleartext_traffic.pcap', packets)
    print("PCAP file created successfully: cleartext_traffic.pcap")
    print("Contains FTP traffic with flag in cleartext")

if __name__ == '__main__':
    try:
        create_pcap()
    except Exception as e:
        print(f"Error creating PCAP: {e}")
        print("Make sure scapy is installed: pip install scapy")

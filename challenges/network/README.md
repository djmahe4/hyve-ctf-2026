# Network Analysis Challenge: Cleartext Traffic

## Challenge Description
We intercepted some traffic from the bistro's network. Can you find the credentials?
The challenge involves analyzing a PCAP file to find cleartext credentials (FTP/HTTP).

## Setup Instructions (Automated)
The `generate_team_files.py` script automatically:
1.  Calls `challenges/network/create_pcap.py`.
2.  Generates `cleartext_traffic.pcap` with simulated FTP traffic containing the flag.

## Solution
1.  **Download the PCAP** from the CTFd challenge "Files" tab.
2.  **Open in Wireshark** or use `strings`/`grep`.
3.  **Filter for FTP or HTTP** traffic.
4.  **Follow TCP Stream** to see the login attempt.
5.  **Find the flag** in the password field or payload: `HYVE_CTF{cl34rt3xt_cr3ds_f0und_...}`.

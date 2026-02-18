# Cryptography Challenge: Bistro Menu Cipher

## Challenge Description
The chef left this note on the menu, but it looks like gibberish.

## Setup Instructions (Automated)
The `generate_team_files.py` script automatically:
1.  Takes the flag `HYVE_CTF{base64_decoded_success}`.
2.  Applies Base64 encoding multiple times (nested).
3.  Saves the result to `base64.txt`.

## Solution
1.  **Download the file** from the CTFd challenge "Files" tab.
2.  **Decode the content** using Base64. You may need to decode it multiple times recursively until the flag appears.
    ```bash
    cat base64.txt | base64 -d | base64 -d | base64 -d
    ```
3.  **Retrieve the flag**: `HYVE_CTF{base64_decoded_success}`.

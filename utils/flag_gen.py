#!/usr/bin/env python3
import os

def get_flag(base_content, identifier, secret=None):
    """
    Generate a dynamic XOR-hashed flag for a specific team/user.
    
    :param base_content: The core flag content (e.g., 'sql_1nj3ct10n_b4s1c')
    :param identifier: The Team ID or User ID (string)
    :param secret: The SECRET_FLAG_KEY. If None, looks for env var.
    :return: Full flag string 'HYVE_CTF{base_content_HASH}'
    """
    if secret is None:
        secret = os.environ.get('SECRET_FLAG_KEY', 'HivyeS3cretKey2026')
    
    # Replicate DynamicXORKey logic from CTFd plugin
    input_str = f"{base_content}|{identifier}|{secret}"
    xor_result = 0
    for char in input_str:
        xor_result ^= ord(char)
    
    hash_suffix = format(xor_result, '08x')
    return f"HYVE_CTF{{{base_content}_{hash_suffix}}}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: flag_gen.py <base_content> <team_id>")
        sys.exit(1)
    
    print(get_flag(sys.argv[1], sys.argv[2]))

#!/usr/bin/env python3
import os

def get_flag(base_content, identifier=None, secret=None):
    """
    Generate a static flag for the challenge.
    
    :param base_content: The core flag content (e.g., 'sql_1nj3ct10n_b4s1c')
    :param identifier: (Legacy) Team ID or User ID (ignored)
    :param secret: (Legacy) SECRET_FLAG_KEY (ignored)
    :return: Full flag string 'HYVE_CTF{base_content}'
    """
    return f"HYVE_CTF{{{base_content}}}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: flag_gen.py <base_content> <team_id>")
        sys.exit(1)
    
    print(get_flag(sys.argv[1]))

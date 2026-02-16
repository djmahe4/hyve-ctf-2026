#!/usr/bin/env python3
import os

def get_flag(base_content, identifier=None, secret=None):
    """
    Generate a static flag for the challenge.
    
    :param base_content: The core flag content (e.g., 'sql_1nj3ct10n_b4s1c')
    :param identifier: (Legacy/Compat) Team ID (ignored for static flags)
    :param secret: (Legacy/Compat) Secret key (ignored for static flags)
    :return: Full flag string 'HYVE_CTF{base_content}'
    """
    # Simple static flag generation as requested
    return f"HYVE_CTF{{{base_content}}}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: flag_gen.py <base_content> [team_id]")
        sys.exit(1)
    
    print(get_flag(sys.argv[1]))

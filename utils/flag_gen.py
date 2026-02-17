import random

def get_flag(base_content, identifier=None, secret=None):
    """
    Generate a static flag for the challenge.
    
    :param base_content: The core flag content (e.g., 'sql_1nj3ct10n_b4s1c')
    :return: Full flag string 'HYVE_CTF{base_content}'
    """
    return f"HYVE_CTF{{{base_content}}}"

def get_fake_flag(base_content):
    """
    Generate a fake flag with a humorous jargon suffix.
    """
    jargons = ["real", "riyal", "legit", "trust_me_bro", "totally_real", "actual", "final", "final_final", "v2_fixed"]
    suffix = random.choice(jargons)
    return f"HYVE_CTF{{{base_content}_{suffix}}}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: flag_gen.py <base_content> [team_id]")
        sys.exit(1)
    
    print(get_flag(sys.argv[1]))

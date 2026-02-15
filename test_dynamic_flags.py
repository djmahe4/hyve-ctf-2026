import re

def compute_xor_hash(base_flag, identifier, secret_key):
    # Combine inputs into a deterministic string
    input_str = f"{base_flag}|{identifier}|{secret_key}"
    
    # XOR all bytes together
    xor_result = 0
    for char in input_str:
        xor_result ^= ord(char)
    
    # Convert to hex string (8 characters)
    return format(xor_result, '08x')

def validate_flag(provided, saved_base, identifier, secret_key):
    # Expects HYVE_CTF{content_HASH}
    pattern = r"HYVE_CTF\{(.+)_([0-9a-f]{8})\}"
    match = re.match(pattern, provided)
    if not match:
        return False, "Invalid format"
    
    content = match.group(1)
    provided_hash = match.group(2)
    
    if content != saved_base:
        return False, "Content mismatch"
    
    expected_hash = compute_xor_hash(saved_base, identifier, secret_key)
    if provided_hash != expected_hash:
        return False, f"Hash mismatch (Expected {expected_hash}, got {provided_hash})"
    
    return True, "Valid"

# Test cases
secret = "HivyeS3cretKey2026"
base_flag = "st3g0_cat_m4st3r"

print("--- Dynamic Flag Verification ---")
for team_id in ["1", "2", "3"]:
    h = compute_xor_hash(base_flag, team_id, secret)
    full_flag = f"HYVE_CTF{{{base_flag}_{h}}}"
    print(f"Team {team_id} Flag: {full_flag}")
    
    # Test valid
    is_valid, msg = validate_flag(full_flag, base_flag, team_id, secret)
    print(f"  Validation (Self): {is_valid} ({msg})")
    
    # Test invalid (Team 1 tries Team 2's hash)
    if team_id == "1":
        h2 = compute_xor_hash(base_flag, "2", secret)
        malicious_flag = f"HYVE_CTF{{{base_flag}_{h2}}}"
        is_valid, msg = validate_flag(malicious_flag, base_flag, team_id, secret)
        print(f"  Attempting Team 2's flag as Team 1: {is_valid} ({msg})")

print("\n--- Deception Elements ---")
fake_flag = "HYVE_CTF{you_found_it}_FAKEHASH"
is_valid, msg = validate_flag(fake_flag, base_flag, "1", secret)
print(f"Fake flag validation: {is_valid} ({msg})")

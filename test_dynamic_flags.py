import re

def validate_flag(provided, saved_base):
    # Expects HYVE_CTF{content}
    pattern = r"HYVE_CTF\{(.+)\}"
    match = re.match(pattern, provided)
    if not match:
        return False, "Invalid format"
    
    content = match.group(1)
    
    if content != saved_base:
        return False, "Content mismatch"
    
    return True, "Valid"

# Test cases
base_flag = "st3g0_cat_m4st3r"

print("--- Static Flag Verification ---")
for team_id in ["1", "2", "3"]:
    full_flag = f"HYVE_CTF{{{base_flag}}}"
    print(f"Team {team_id} Flag: {full_flag}")
    
    # Test valid
    is_valid, msg = validate_flag(full_flag, base_flag)
    print(f"  Validation (Self): {is_valid} ({msg})")

print("\n--- Deception Elements ---")
fake_flag = "HYVE_CTF{you_found_it}"
is_valid, msg = validate_flag(fake_flag, base_flag)
print(f"Fake flag validation: {is_valid} ({msg})")

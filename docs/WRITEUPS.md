# Challenge Writeups

Complete solutions for all 10 challenges in Hyve CTF 2026.

---

## Challenge 1: Bistro Location (OSINT - 100 points)

**Category**: OSINT  
**Difficulty**: Easy  
**Points**: 100

### Solution

1. Download the mystery image from the challenge files.
2. Extract EXIF data using exiftool:
   ```bash
   exiftool mystery_location.jpg
   ```

3. Look for GPS coordinates in the output:
   ```
   GPS Latitude: 48° 51' 30.24" N
   GPS Longitude: 2° 17' 40.20" E
   ```

4. Identify the landmark: Eiffel Tower in Paris, France.

5. **THE FLAG**: Check the "Description" or "Image Description" field in the EXIF data.
   It contains the flag directly: `HYVE_CTF{PARIS_FRANCE_EIFFELTOWER}`

---

## Challenge 2: Secret Ingredient List (Steganography - 100 points)

**Category**: Steganography  
**Difficulty**: Easy  
**Points**: 100

### Solution

1. Download the `cat.jpeg` image and `wordlist.txt` from the challenge files.

2. The image contains a hidden message embedded with `steghide`.

3. Use the provided wordlist to crack the password (or guess common cat terms like `meow`).
   ```bash
   # Try passwords from wordlist.txt
   steghide extract -sf cat.jpeg -p 2026ftc
   ```

4. The tool extracts `secret.txt` containing the flag.

**Flag**: `HYVE_CTF{st3g0_cat_m4st3r}`

---

## Challenge 3: Bistro Menu Cipher (Cryptography - 100 points)

**Category**: Cryptography  
**Difficulty**: Easy  
**Points**: 100

### Solution

1. The encrypted message is: `SYNT{pnrfne_vf_gbb_jrnx}`

2. This is a ROT13 cipher (Caesar cipher with shift of 13)

3. Decode using any ROT13 decoder or Python:
   ```python
   import codecs
   encrypted = "SYNT{pnrfne_vf_gbb_jrnx}"
   decrypted = codecs.decode(encrypted, 'rot_13')
   print(decrypted)
   ```

**Flag**: `HYVE_CTF{caesar_is_too_weak}`

---

## Challenge 4: Staff Portal Bypass (Web - 200 points)

**Category**: Web  
**Difficulty**: Medium  
**Points**: 200

### Solution

1. Navigate to http://localhost:8080/staff-login

2. The login form is vulnerable to SQL injection

3. The SQL query structure: `SELECT * FROM users WHERE username='USER' AND password='PASS'`

4. Bypass authentication by injecting SQL comment:
   - **Username**: `admin'--`
   - **Password**: anything (will be ignored)

5. The query becomes: `SELECT * FROM users WHERE username='admin'--' AND password='...'`
   - Everything after `--` is commented out

6. Successfully logged in, flag is displayed

**Flag**: `HYVE_CTF{sql_1nj3ct10n_b4s1c}`

---

## Challenge 5: Gold Membership (Web - 200 points)

**Category**: Web  
**Difficulty**: Medium  
**Points**: 200

### Solution

1. Navigate to http://localhost:8080/profile

2. The page shows "Role: user" and mentions admin privileges needed

3. Open browser Developer Tools (F12)

4. Go to Application/Storage tab > Cookies

5. Find cookie named `role` with value `user`

6. Edit the cookie value to `admin`

7. Refresh the page

8. Flag is now visible

**Flag**: `HYVE_CTF{c00k13_m4n1pul4t10n}`

---

## Challenge 6: Bistro Traffic Audit (Network - 200 points)

**Category**: Network  
**Difficulty**: Medium  
**Points**: 200

### Solution

1. Download `cleartext_traffic.pcap` from the challenge files.

2. Open in Wireshark:
   ```bash
   wireshark cleartext_traffic.pcap
   ```

3. Apply filter for FTP traffic:
   ```
   ftp
   ```

4. Look through the packets for FTP authentication

5. Find the PASS command containing the flag:
   ```
   PASS HYVE_CTF{cl34rt3xt_cr3ds_f0und}
   ```

6. Alternatively, follow TCP stream of FTP packets

**Flag**: `HYVE_CTF{cl34rt3xt_cr3ds_f0und}`

---

## Challenge 7: Chef's Secret Recipe (Cryptography - 200 points)
**Category**: Cryptography  
**Difficulty**: Medium  
**Points**: 200

### Solution

1. The encoded string: `RlN5SkVJOVFJUk03TDJ1eU1hQXNwMkl3cHpJMEszVmpxUzl2QXdFc29KeTRzRD09`

2. Decode using Base64, then ROT13, then Base64 again:

   ```python
   import base64

   def rot13(text):
       result = ""
       for char in text:
           if 'a' <= char <= 'z':
               result += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
           elif 'A' <= char <= 'Z':
               result += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
           else:
               result += char
       return result

   encoded = "RlN5SkVJOVFJUk03TDJ1eU1hQXNwMkl3cHpJMEszVmpxUzl2QXdFc29KeTRzRD09"
   
   # First decode (Base64)
   decoded1 = base64.b64decode(encoded).decode()
   
   # Second decode (ROT13)
   decoded2 = rot13(decoded1)
   
   # Third decode (Base64)
   decoded3 = base64.b64decode(decoded2).decode()
   print(decoded3)
   ```

3. Or use command line:
   ```bash
   echo "RlN5SkVJOVFJUk03TDJ1eU1hQXNwMkl3cHpJMEszVmpxUzl2QXdFc29KeTRzRD09" | base64 -d | tr 'A-Za-z' 'N-ZA-Mn-za-m' | base64 -d
   ```

**Flag**: `HYVE_CTF{chefs_secret_r0t_b64_mix}`

---

## Challenge 8: Menu Search Vulnerability (Web - 300 points)

**Category**: Web  
**Difficulty**: Hard  
**Points**: 300

### Solution

1. Navigate to http://localhost:8080/menu-search

2. The search functionality reflects user input without sanitization

3. Test for XSS vulnerability by injecting a script tag:
   ```
   <script>alert(1)</script>
   ```

4. Full URL:
   ```
   http://localhost:8080/menu-search?q=<script>alert(1)</script>
   ```

5. The application detects the XSS payload and returns the flag

6. In a real scenario, this could steal cookies or execute malicious code

**Flag**: `HYVE_CTF{xss_r3fl3ct3d_vuln}`

---

## Challenge 9: Order Tracking (Web - 300 points)

**Category**: Web  
**Difficulty**: Hard  
**Points**: 300

### Solution

1. Navigate to http://localhost:8080/api/order/tracking/1001

2. This returns your order data (order_id=1001)

3. The API has an IDOR vulnerability - no authorization checks

4. Try accessing the admin order by changing the ID to 10:
   ```
   http://localhost:8080/api/order/tracking/10
   ```

5. The API returns admin's data including the secret field with the flag:
   ```json
   {
     "order_id": 10,
     "customer": "admin",
     "email": "admin@hyvebistro.ctf",
     "secret_note": "HYVE_CTF{1d0r_pr1v_3sc4l4t10n}"
   }
   ```

**Flag**: `HYVE_CTF{1d0r_pr1v_3sc4l4t10n}`

---

## Challenge 10: Secret Ingredient Vault (Web - 100 points)

**Category**: Web  
**Difficulty**: Easy  
**Points**: 100

### Solution

1. Navigate to http://localhost:8080/secret-ingredients

2. View the page source (Ctrl+U or right-click > View Page Source)

3. Look through the HTML for hidden elements or comments

4. Find a hidden div with a data attribute:
   ```html
   <div id="ingredient-vault" data-recipe-secret="HYVE_CTF{html_embedded_flag}" class="hidden"></div>
   ```

5. The flag is embedded in the `data-recipe-secret` attribute

6. Alternatively, use browser DevTools (F12) > Elements tab to inspect the DOM

**Flag**: `HYVE_CTF{html_embedded_flag}`

---

## Challenge 11: Secret Highway (OSINT - 100 points)

**Category**: OSINT  
**Difficulty**: Easy  
**Points**: 100

### Solution

1. Download the `unknown_highway.png` image from the challenge files.
2. The image depicts a prominent highway in a specific location.
3. Use reverse image search (e.g., Google Lens) or identify visual clues to determine the country and city.
4. The location is in Stockholm, Sweden.
5. Format the flag as per the description: `HYVE_CTF{STOCKHOLM_SWEDEN}`.

**Flag**: `HYVE_CTF{STOCKHOLM_SWEDEN}`

---

## Challenge 12: Mystery Place (OSINT - 100 points)

**Category**: OSINT  
**Difficulty**: Easy  
**Points**: 100

### Solution

1. Download the `mystery_place.jpg` image.
2. Similar to the previous OSINT challenge, reverse-search the image to identify the landmark.
3. The image is of a prominent place in China.
4. Format the flag as requested.

**Flag**: `HYVE_CTF{CHiNa}`

---

## Challenge 13: Lord of What? (Misc - 100 points)

**Category**: Misc  
**Difficulty**: Easy  
**Points**: 100

### Solution

1. The challenge description contains the text: `MXE yi jxu bet h ev cisysxut?`
2. This is a simple Caesar cipher (ROT).
3. Shift the letters by +10 (or -16) to reveal the question: `WHO is the god of mischief?`
4. The god of mischief in Norse mythology (and popular culture) is Loki.

**Flag**: `HYVE_CTF{LOKI}`

---

## Challenge 14: Layer 0 (Cryptography - 200 points)

**Category**: Cryptography  
**Difficulty**: Medium  
**Points**: 200

### Solution

1. The provided ciphertext is: `==AAAAAIBqXgjCABz+QcJh8r2lELySziLpANIts8ww4qP0ASIraNPJHD0sw/CAAAAAAAIs4H`
2. The string appears to be reversed Base64, denoted by the padding `==` at the beginning.
3. Reverse the string back to normal Base64: `H4sIAAAAAAAAC/ws0DHJPNarISA0Pq4ww8stINApLziSyLEl2r8hJcQ+zBACjgXqBIAAAAA==`
4. This new string decodes to a Gzip compressed archive (implied by the `H4sI` magic bytes in Base64).
5. Decode and decompress to reveal the flag: `HYVE_CTF{layer_cake_complete}`.

**Flag**: `HYVE_CTF{layer_cake_complete}`

---

## Challenge 15: Web explorer 1 (Web - 100 points)

**Category**: Web  
**Difficulty**: Easy  
**Points**: 100

### Solution

1. You are given an `inventory.xml` file.
2. The comment says: "Concatenate their 'id' attributes to retrieve the recovery key" for items with `status="critical"`.
3. Extract all `<item>` elements with `status="critical"` in order.
4. The extracted `id` attributes are: `C`, `TF`, `{x`, `ml_`, `pa`, `rs`, `in`, `g_`, `is`, `_t`, `ed`, `io`, `us`, `_b`, `ut`, `_n`, `3c`, `3s`, `s`, `ar`, `y}`.
5. Concatenate them: `HYVE_CTF{xml_parsing_is_tedious_but_n3c3ssary}`.

**Flag**: `HYVE_CTF{xml_parsing_is_tedious_but_n3c3ssary}`

---

## Challenge 16: Web explorer 2 (Web - 200 points)

**Category**: Web  
**Difficulty**: Medium  
**Points**: 200

### Solution

1. You are given `dashboard.html`. Inspecting the source code reveals hints left by developers about a fragmented flag.
2. The flag is split into three Base64 encoded parts hidden in the DOM:
   - Part 1 is in the HTML comment: `Q1RGe2h0bWxf` -> Base64 decodes to `CTF{html_`
   - Part 2 is the `<meta name="debug-id" content="...">` value `YmxpbmRfc3BvdHM=` -> Base64 decodes to `blind_spots`
   - Part 3 is in the `data-config` attribute: `e3JldmVhbF90cnV0aH0=` -> Base64 decodes to `{reveal_truth}`
3. Concatenate the decoded parts.

**Flag**: `HYVE_CTF{html_blind_spots_{reveal_truth}}`

---

## Challenge 17: Web explorer 3 (Web - 200 points)

**Category**: Web  
**Difficulty**: Medium  
**Points**: 200

### Solution

1. You are provided with `style_hunt.html`.
2. The page contains a "Wall of Text", but the CSS defines a specific class `.found` that is white text on a white background, making it invisible.
3. Extract all characters wrapped in `<span class="found">`.
4. The characters spell out: `CTF{css_classes_can_hide_secrets}`.

**Flag**: `HYVE_CTF{css_classes_can_hide_secrets}`

---

## Challenge 18: Binary Trouble (Misc - 300 points)

**Category**: Misc  
**Difficulty**: Hard  
**Points**: 300

### Solution

1. Download the `mystery` ELF binary and `config.dat`.
2. Running `strings` against the binary reveals the environment variable check:
   ```
   CTF_ACCESS_LEVEL
   Access Denied: Environment variable 'CTF_ACCESS_LEVEL' not set.
   ```
3. The binary expects this environment variable to be set. It also reads from the `config.dat` to decrypt the flag.
4. Set the variable (e.g., `export CTF_ACCESS_LEVEL=admin` or similar) and run `./mystery`. 
5. The binary execution flow eventually prints the flag.

**Flag**: `HYVE_CTF{binary_execution_flow_mastered}`

---

## Challenge 19: Multi-Stage Signal (Misc - 300 points)

**Category**: Misc  
**Difficulty**: Hard  
**Points**: 300

### Solution

1. Extract the `site.zip` archive. It contains directories `site1`, `site2`, `site3`, and `site4`.
2. The challenge requires assembling a fragmented flag according to `site4/final.txt`:
   - Fragment 1: The greeting in `site1/index.html`.
   - Fragment 2: Decoding the data in `site2` (base64 then hex).
   - Fragment 3: Network layers extracted from `site3` PCAPs.
3. After extracting and assembling the fragments, the signal forms the flag.

**Flag**: `HYVE_CTF{s1gn4l_trac3d_th3_n3tw0rk_p4th}`

---

## Summary

Congratulations on completing all 19 challenges! Here's what you learned:

- **OSINT**: EXIF data extraction, geolocation, and reverse image searching
- **Steganography**: Hidden data in images using steghide
- **Cryptography**: ROT shifting, Base64 triple encoding, Reverse Base64 with Gzip decompression
- **Web Security**:
  - SQL Injection and IDOR vulnerabilities
  - Cookie manipulation and XSS
  - XML parsing, HTML/DOM metadata extraction, CSS classes hiding
- **Network Analysis**: PCAP analysis with Wireshark and FTP traffic inspection
- **Misc/Binary**: Linux ELF execution flow, environment variable checks, fragment reassembly

Keep practicing and stay secure! 🎉

---

## Understanding the Flags

All flags in this CTF follow a standard format.

**Format**: `HYVE_CTF{CONTENT}`

*   **CONTENT**: A string unique to the challenge (e.g., `sql_1nj3ct10n_b4s1c`).

### Challenges & Flags

| Category | Challenge | Flag | Extraction Method |
| :--- | :--- | :--- | :--- |
| **OSINT** | Bistro Location | `HYVE_CTF{PARIS_FRANCE_EIFFELTOWER}` | **Description Field.** The flag is in the EXIF image description. |
| **OSINT** | Secret Highway | `HYVE_CTF{STOCKHOLM_SWEDEN}` | **Reverse Image Search.** Identify landmark. |
| **OSINT** | Mystery Place | `HYVE_CTF{CHiNa}` | **Reverse Image Search.** Identify landmark. |
| **Steganography** | Secret Ingredient | `HYVE_CTF{st3g0_cat_m4st3r}` | **Steghide.** Extract with password `meow`. |
| **Cryptography** | Bistro Menu Cipher | `HYVE_CTF{caesar_is_too_weak}` | **Decoding.** ROT13. |
| **Cryptography** | Chef's Recipe | `HYVE_CTF{chefs_secret_r0t_b64_mix}` | **Decoding.** Base64 -> ROT13 -> Base64. |
| **Cryptography** | Layer 0 | `HYVE_CTF{layer_cake_complete}` | **Decoding.** Reverse Base64 -> Gzip decompress. |
| **Network** | Traffic Audit | `HYVE_CTF{cl34rt3xt_cr3ds_f0und}` | **Traffic Analysis.** Find the FTP `PASS` command. |
| **Misc** | Lord of What? | `HYVE_CTF{LOKI}` | **Decoding.** ROT10 on the description text. |
| **Misc** | Binary Trouble | `HYVE_CTF{binary_execution_flow_mastered}` | **Binary Execution.** Set `CTF_ACCESS_LEVEL` env var. |
| **Misc** | Multi-Stage Signal | `HYVE_CTF{s1gn4l_trac3d_th3_n3tw0rk_p4th}` | **Signal Reassembly.** Recombine cross-site fragments. |
| **Web** | All Web Challenges | *Various* | **Exploitation/Parsing.** IDOR, cookies, HTML/XML DOM extraction. |

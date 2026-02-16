# Challenge Writeups

Complete solutions for all 10 challenges in Hivye CTF 2026.

---

## Challenge 1: Bistro Location (OSINT - 100 points)

**Category**: OSINT  
**Difficulty**: Easy  
**Points**: 100

### Solution

1. Download the mystery image from the file server
2. Extract EXIF data using exiftool:
   ```bash
   exiftool mystery_location.jpg
   ```

3. Look for GPS coordinates in the output:
   ```
   GPS Latitude: 48° 51' 30.24" N
   GPS Longitude: 2° 17' 40.20" E
   ```

4. Convert to decimal: `48.86` and `2.29` (rounded to 2 decimal places).

5. Identify the landmark: Eiffel Tower in Paris, France.

6. **CRITICAL STEP**: The flag is hidden inside the image using Steganography!
   The password is the latitude and longitude concatenated: `48.862.29`

7. Extract the flag using Steghide:
   ```bash
   steghide extract -sf mystery_location.jpg -p 48.862.29
   ```

8. The extracted file contains the full flag with the hash.

**Flag**: `HYVE_CTF{PARIS_FRANCE_EIFFELTOWER}`

---

## Challenge 2: Secret Ingredient List (Steganography - 100 points)

**Category**: Steganography  
**Difficulty**: Easy  
**Points**: 100

### Solution

1. Download the cat.jpeg image from the authenticated file server

2. Download the wordlist.txt file

3. Use steghide to extract the hidden message:
   ```bash
   steghide extract -sf cat.jpeg
   ```

4. When prompted for password, look through the wordlist - the password is `2026-ftc` (a transposition of ctf-2026)

5. The tool extracts a file containing the team-specific flag

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

4. Or use online tool: https://rot13.com

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

1. Download cleartext_traffic.pcap from http://localhost:8082/files/network/cleartext_traffic.pcap

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

1. The encoded string: `V1cxR2VscFVXVEJZTWxKc1dUSTVhMXBYVW1aak0xWnFXVEpXZW1ONU5UQmxTRkU5`

2. Decode using Base64 three times:

   ```python
   import base64
   
   encoded = "V1cxR2VscFVXVEJZTWxKc1dUSTVhMXBYVW1aak0xWnFXVEpXZW1ONU5UQmxTRkU5"
   
   # First decode
   decoded1 = base64.b64decode(encoded)
   
   # Second decode
   decoded2 = base64.b64decode(decoded1)
   
   # Third decode
   decoded3 = base64.b64decode(decoded2)
   print(decoded3.decode())
   ```

3. Or use command line:
   ```bash
   echo "V1cxR2VscFVXVEJZTWxKc1dUSTVhMXBYVW1aak0xWnFXVEpXZW1ONU5UQmxTRkU5" | base64 -d | base64 -d | base64 -d
   ```

**Flag**: `HYVE_CTF{base64_decoded_success}`

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

4. Try accessing the admin order by changing the ID to 1:
   ```
   http://localhost:8080/api/order/tracking/1
   ```

5. The API returns admin's data including the secret field with the flag:
   ```json
   {
     "order_id": 1,
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

## Summary

Congratulations on completing all 10 challenges! Here's what you learned:

- **OSINT**: EXIF data extraction and geolocation
- **Steganography**: Hidden data in images using steghide
- **Cryptography**: ROT13 and Base64 encoding (triple encoding)
- **Web Security**:
  - SQL Injection vulnerabilities
  - Cookie manipulation
  - Cross-Site Scripting (XSS)
  - Insecure Direct Object Reference (IDOR)
  - Source code inspection and HTML data attributes
- **Network Analysis**: PCAP analysis with Wireshark and FTP traffic inspection

Keep practicing and stay secure! 🎉

---

## Understanding the Flag Hash

All flags in this CTF are **Dynamic**. This means the flag you find will have a unique suffix based on your Team ID.

**Format**: `HYVE_CTF{BASE_CONTENT_HASH}`

*   **BASE_CONTENT**: The constant part of the flag (e.g., `sql_1nj3ct10n_b4s1c`).
*   **HASH**: An 8-character hexadecimal string unique to your team.

### How to Find the Flag (and Hash)

You do **not** need to calculate the hash yourself. The complete flag (including the hash) is always recoverable from the challenge itself.

| Category | Challenge | Where is the Flag + Hash? |
| :--- | :--- | :--- |
| **OSINT** | Bistro Location | **Hidden in the image.** Use EXIF data to find coordinates, then use those as a password to extract the flag with `steghide`. |
| **Steganography** | Secret Ingredient | **Hidden in the image.** Use `steghide` with the password from the wordlist to extract the flag file. |
| **Network** | Traffic Audit | **In the traffic.** The FTP `PASS` command contains the full flag string. |
| **Cryptography** | Chef's Recipe | **Encoded.** The Base64 string decodes to the full flag. |
| **Web** | All Web Challenges | **Returned by Server.** When you exploit the vulnerability (XSS, SQLi, IDOR), the server responds with the full flag. |

### Note for Administrators
If you need to manually generate a flag for testing:
```bash
python3 utils/flag_gen.py <base_content> <team_id>
# Example: python3 utils/flag_gen.py sql_1nj3ct10n_b4s1c 1
```

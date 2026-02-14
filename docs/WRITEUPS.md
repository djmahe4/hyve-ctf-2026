# Challenge Writeups

Complete solutions for all 9 challenges in Hivye CTF 2026.

---

## Challenge 1: Where in the World? (OSINT - 100 points)

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

4. Convert to decimal: 48.8584°N, 2.2945°E

5. Search coordinates on Google Maps or use reverse image search

6. Identify the landmark: Eiffel Tower in Paris, France

**Flag**: `FLAG{PARIS_FRANCE_EIFFELTOWER}`

---

## Challenge 2: Hidden Message (Steganography - 100 points)

**Category**: Steganography  
**Difficulty**: Easy  
**Points**: 100

### Solution

1. Download the cat.jpeg image from the file server

2. Use steghide to extract the hidden message:
   ```bash
   steghide extract -sf cat.jpeg
   ```

3. When prompted for password, try the year mentioned in hint: `ctf2026`

4. The tool extracts a file containing the flag

**Flag**: `FLAG{st3g0_cat_m4st3r}`

---

## Challenge 3: Ancient Cipher (Cryptography - 100 points)

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

**Flag**: `FLAG{caesar_is_too_weak}`

---

## Challenge 4: Login Bypass (Web - 200 points)

**Category**: Web  
**Difficulty**: Medium  
**Points**: 200

### Solution

1. Navigate to http://localhost:8080/login

2. The login form is vulnerable to SQL injection

3. The SQL query structure: `SELECT * FROM users WHERE username='USER' AND password='PASS'`

4. Bypass authentication by injecting SQL comment:
   - **Username**: `admin'--`
   - **Password**: anything (will be ignored)

5. The query becomes: `SELECT * FROM users WHERE username='admin'--' AND password='...'`
   - Everything after `--` is commented out

6. Successfully logged in, flag is displayed

**Flag**: `FLAG{sql_1nj3ct10n_b4s1c}`

---

## Challenge 5: Cookie Monster (Web - 200 points)

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

**Flag**: `FLAG{c00k13_m4n1pul4t10n}`

---

## Challenge 6: Wireshark Detective (Network - 200 points)

**Category**: Network  
**Difficulty**: Medium  
**Points**: 200

### Solution

1. Download cleartext_traffic.pcap from http://localhost:8081/network/

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
   PASS FLAG{cl34rt3xt_cr3ds_f0und}
   ```

6. Alternatively, follow TCP stream of FTP packets

**Flag**: `FLAG{cl34rt3xt_cr3ds_f0und}`

---

## Challenge 7: Encoded Secrets (Cryptography - 200 points)

**Category**: Cryptography  
**Difficulty**: Medium  
**Points**: 200

### Solution

1. The encoded string: `VTBGTVIxdGlZWE5sTmpSZlpHVmpiMlJsWkY5emRXTmpaWE56TG5SMGVIUT0=`

2. Decode using Base64 three times:

   ```python
   import base64
   
   encoded = "VTBGTVIxdGlZWE5sTmpSZlpHVmpiMlJsWkY5emRXTmpaWE56TG5SMGVIUT0="
   
   # First decode
   decoded1 = base64.b64decode(encoded)
   print(decoded1)  # U0FMR1tiYXNlNjRfZGVjb2RlZF9zdWNjZXNzLnR0eHQ=
   
   # Second decode
   decoded2 = base64.b64decode(decoded1)
   print(decoded2)  # RkxBR3tiYXNlNjRfZGVjb2RlZF9zdWNjZXNzLnR4dH0=
   
   # Third decode
   decoded3 = base64.b64decode(decoded2)
   print(decoded3)  # FLAG{base64_decoded_success.txt}
   ```

3. Or use command line:
   ```bash
   echo "VTBGTVIxdGlZWE5sTmpSZlpHVmpiMlJsWkY5emRXTmpaWE56TG5SMGVIUT0=" | base64 -d | base64 -d | base64 -d
   ```

**Flag**: `FLAG{base64_decoded_success.txt}`

---

## Challenge 8: Script Injection (Web - 300 points)

**Category**: Web  
**Difficulty**: Hard  
**Points**: 300

### Solution

1. Navigate to http://localhost:8080/search

2. The search functionality reflects user input without sanitization

3. Test for XSS vulnerability by injecting a script tag:
   ```
   <script>alert(document.cookie)</script>
   ```

4. Full URL:
   ```
   http://localhost:8080/search?q=<script>alert(document.cookie)</script>
   ```

5. The application detects the XSS payload and returns the flag

6. In a real scenario, this could steal cookies or execute malicious code

**Flag**: `FLAG{xss_r3fl3ct3d_vuln}`

---

## Challenge 9: Object Reference (Web - 300 points)

**Category**: Web  
**Difficulty**: Hard  
**Points**: 300

### Solution

1. Navigate to http://localhost:8080/api/user/2

2. This returns your user data (user_id=2)

3. The API has an IDOR vulnerability - no authorization checks

4. Try accessing the admin user by changing the ID to 1:
   ```
   http://localhost:8080/api/user/1
   ```

5. The API returns admin's data including the secret field with the flag:
   ```json
   {
     "id": 1,
     "username": "admin",
     "email": "admin@hivyectf.com",
     "secret": "FLAG{1d0r_pr1v_3sc4l4t10n}"
   }
   ```

**Flag**: `FLAG{1d0r_pr1v_3sc4l4t10n}`

---

## Summary

Congratulations on completing all challenges! Here's what you learned:

- **OSINT**: EXIF data extraction and geolocation
- **Steganography**: Hidden data in images using steghide
- **Cryptography**: ROT13 and Base64 encoding
- **Web Security**:
  - SQL Injection vulnerabilities
  - Cookie manipulation
  - Cross-Site Scripting (XSS)
  - Insecure Direct Object Reference (IDOR)
- **Network Analysis**: PCAP analysis with Wireshark

Keep practicing and stay secure! 🎉

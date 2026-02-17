# Hyve CTF 2026: Dynamic Flag Mechanism Guide

This document explains how flags are generated and validated in the Hyve CTF 2026 platform using the custom `DynamicXORKey` plugin.

## 1. Flag Format
All flags follow a strict format to ensure parsing consistency and security:
`HYVE_CTF{<BASE_FLAG_CONTENT>_<HASH>}`

- **BASE_FLAG_CONTENT**: The core solution to the challenge (e.g., `sql_1nj3ct10n_b4s1c`).
- **HASH**: A unique 8-character hexadecimal string tied to the team or user.

## 2. Hashing Calculation
The hash is calculated server-side using a deterministic XOR-based algorithm. This prevents players from sharing flags, as the hash for Team A will not work for Team B.

### The Algorithm
1. **Inputs**:
   - `SAVED_CONTENT`: The base flag string (e.g., `st3g0_cat_m4st3r`).
   - `IDENTIFIER`: The Team ID (or User ID if no team exists).
   - `SECRET_KEY`: A server-side secret (`SECRET_FLAG_KEY` env var).
2. **String Generation**: Strings are concatenated: `{SAVED_CONTENT}|{IDENTIFIER}|{SECRET_KEY}`.
3. **XOR Process**: Every character in the string is XORed together to produce a single integer.
4. **Hex Conversion**: The resulting integer is formatted into an 8-character hexadecimal string.

### Logic (Python snippet)
```python
input_str = f"{saved}|{identifier}|{secret}"
xor_result = 0
for char in input_str:
    xor_result ^= ord(char)
hash_suffix = format(xor_result, '08x')
```

## 3. Challenge Integration (True Dynamic Delivery)

The system is now configured for "True Dynamic Delivery". Each challenge presents the flag specific to your Team ID.

| Challenge Category | Integration Method | How to find your unique Flag |
| :--- | :--- | :--- |
| **Bistro Web App** | Real-time Rendering | The `app.py` server detects your Team ID and renders your specific `HYVE_CTF{...}` in HTML comments, profile rewards, and API responses. |
| **Stego (cat.jpeg)** | Parameterized Build | The image is generated using `create_stego.sh` for your specific Team ID. The flag embedded inside matches YOUR identity. |
| **Network (PCAP)** | Parameterized Capture | The PCAP file is generated using `create_pcap.py` with your Team ID as an input, ensuring cleartext flags match your team. |

## 4. Identifying your Team ID
To ensure you are looking for the right hash, we have integrated a **Team ID Sealer** in the Bistro App:
- Visit the **My Loyalty/Profile** page.
- At the bottom of the page, your current **Team ID** is displayed (e.g., `Team ID: 123`).
- This ID is what the platform uses to generate all your dynamic flags.

## 5. Submitting the Flag
When you find a flag (e.g., `HYVE_CTF{sql_1nj3ct10n_b4s1c_00000041}`):
- **Copy the whole string** including the braces and suffix.
- The standard `DynamicXORKey` plugin on CTFd will validate it against your Team ID.

## 6. Trigger Mechanism: When is the Flag Generated?

A common question is whether flags are pre-generated when a user is created in CTFd. **No.** The system uses an **On-Demand Generation** model.

### Trigger Flow for Different Challenge Types:

#### A. Web Challenges (Real-Time Rendering)
- **Trigger**: Every time a player visits a challenge page (e.g., `/profile` or `/staff-login`).
- **Process**:
    1. The Python `app.py` server detects the player's identity (Team ID).
    2. It calls `flag_gen.get_flag()` instantly.
    3. The resulting string is injected into the HTML before it's sent to the browser.
- **Benefit**: No database storage is needed for millions of team-specific flags.

#### B. Asset-Based Challenges (Stego/PCAP)
- **Trigger**: When the challenge deployment script or file server receives a download request.
- **Process**:
    1. The orchestrator (e.g., a custom file-serving container) identifies the requesting session's Team ID.
    2. It executes the creation script (`create_stego.sh` or `create_pcap.py`) passing the `TEAM_ID` as a parameter.
    3. The file is built in memory or temporary storage and delivered to the user.
- **Note**: For Hyve CTF 2026, the provided scripts support this `TEAM_ID` parameter for easy integration with your CI/CD or file server.

#### C. Submission Validation (Server-Side)
- **Trigger**: When a player clicks "Submit" on CTFd.
- **Process**:
    1. The `DynamicXORKey` plugin intercepts the submission.
    2. It checks the *current* Team ID logged into CTFd.
    3. It re-computes the XOR hash for that specific Team ID.
    4. If it matches the user's input, the solve is granted.

## 7. Implementation Walkthrough Summary
1. **Source of Truth**: `utils/flag_gen.py` contains the master algorithm.
2. **Web Delivery**: Integrated via `render_template_string` in `app.py`.
3. **Asset Delivery**: Scripted via Shell/Python with `TEAM_ID` arguments.
4. **Validation**: Handled by the custom CTFd `BaseKey` override in the plugin.

---
*Ready to scale - Zero pre-computation required.*

# Hivye CTF 2026 - System Logic & Integrations

This document details the internal mechanisms, API flows, and service integrations that power the Hivye CTF platform.

## 1. Automated Setup Flow (`setup_ctf.py`)

The `setup_ctf.py` script is the central orchestrator that automates the transition from a fresh Docker install to a fully configured CTF.

### API Orchestration
The script uses `requests` to interact with the CTFd API:
1. **Initial Setup**: Checks for the `/setup` endpoint. If found, it fetches the page, extracts the CSRF `nonce`, and submits a POST request to configure the admin account, event name, and timing.
2. **Authentication**: Performs a login to establish a session, then POSTs to `/api/v1/tokens` to generate a persistent **Admin API Token**.
3. **Team Creation**: Loops to create 20 participant teams via `POST /api/v1/teams`, generating unique email/password combinations for each.
4. **Challenge Import**: Triggers the `import_challenges.py` script which parses `challenges.yml` and makes `POST /api/v1/challenges` calls. It correctly handles dynamic challenge types by providing `initial`, `minimum`, and `decay` values.

## 2. Dynamic Flag Mechanism

To prevent flag sharing between teams, every flag is uniquely generated based on the Team ID.

### The Algorithm (`utils/flag_gen.py`)
```python
input_str = f"{base_content}|{team_id}|{secret_key}"
xor_result = 0
for char in input_str:
    xor_result ^= ord(char)
hash_suffix = format(xor_result, '08x')
full_flag = f"HYVE_CTF{{base_content_{hash_suffix}}}"
```
- **Base Content**: The static part of the flag (e.g., `sql_1nj3ct10n_b4s1c`).
- **Secret Key**: A server-side environment variable `SECRET_FLAG_KEY`.

### Validation Plugin
A custom CTFd plugin (`DynamicXORKey`) is used to validate submissions. When a user submits a flag, the plugin:
1. Retrieves the user's current `team_id`.
2. Re-calculates the expected hash for that team.
3. Compares it with the submitted string.

## 3. Team File Distribution System

This system ensures that when a user downloads a challenge file (e.g., a PCAP or JPEG), they receive the version containing *their* team's flag.

### The File Proxy (`deployment/docker/file_proxy.py`)
The `file-proxy` service (Port 8082) acts as an authenticated middleware:
- **Session Validation**: It receives the user's CTFd session cookie and validates it against CTFd's `/api/v1/users/me` endpoint.
- **Path Resolution**: Once authenticated, it extracts the `team_id` and maps the request:
  `GET /files/stego/cat.jpeg` -> `/challenges/teams/team{team_id}/stego/cat.jpeg`
- **Security**: Prevents directory traversal and rejects unauthorized requests.

### Asset Generation (`utils/generate_team_files.py`)
This script pre-generates the file-system structure:
1. Creates `challenges/teams/team1/` through `team21/`.
2. Executes category-specific scripts (`create_stego.sh`, `create_pcap.py`, `create_crypto.py`).
3. These scripts take a `TEAM_ID` argument and use the `flag_gen` utility to bake the correct flag into the generated asset.

## 4. Service Mesh (Docker Integration)

The platform is split across two Docker Compose files connected by a shared network:
- **`ctfd_network`**: An external network created by the CTFd stack that allows the `file-proxy` and `challenge-web` services to verify sessions and resolve internal hostnames.
- **Linkages**: 
    - `file-proxy` -> `ctfd:8000` (for session validation)
    - `setup_ctf.py` -> `localhost:8001` (external access to CTFd)
    - `challenge-web` -> `ctfd_network` (to identify teams via headers/cookies)

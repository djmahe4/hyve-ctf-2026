# Hivye CTF 2026

A 2-hour Capture The Flag (CTF) competition featuring 9 challenges across multiple security domains.

## Description

Hivye CTF 2026 is a beginner to intermediate level CTF competition designed to test skills in OSINT, steganography, cryptography, web exploitation, and network analysis. The competition runs for 2 hours and includes 9 challenges with a total of 1600 points available.

## Challenge Categories

- **OSINT** (1 challenge) - Open Source Intelligence gathering
- **Steganography** (1 challenge) - Hidden message discovery
- **Cryptography** (2 challenges) - Classical and modern encryption
- **Web** (4 challenges) - Web application vulnerabilities
- **Network** (1 challenge) - Packet analysis and forensics

## Quick Start

### Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space
- Linux, macOS, or Windows with WSL2

### Installation

```bash
# Clone the repository
git clone https://github.com/djmahe4/hyve-ctf-2026.git
cd hyve-ctf-2026

# Run the automated setup script
# This will:
#  - Create a virtual environment and install Python dependencies
#  - Check for Docker and Docker Compose
#  - Start CTFd and all challenge services
chmod +x setup.sh
./setup.sh
```

**Or manually:**

```bash
# 1. Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Start services
./start.sh
```

### Access the Platform

- **CTFd Platform**: http://localhost:8001
- **Web Challenges**: http://localhost:8080
- **File Server**: http://localhost:8081

### Default CTFd Admin Access

On first run, you'll be prompted to create an admin account through the setup wizard at http://localhost:8000.

## Challenge List

| # | Challenge Name | Category | Difficulty | Points |
|---|----------------|----------|------------|--------|
| 1 | Where in the World? | OSINT | Easy | 100 |
| 2 | Hidden Message | Steganography | Easy | 100 |
| 3 | Ancient Cipher | Cryptography | Easy | 100 |
| 4 | Login Bypass | Web | Medium | 200 |
| 5 | Cookie Monster | Web | Medium | 200 |
| 6 | Wireshark Detective | Network | Medium | 200 |
| 7 | Encoded Secrets | Cryptography | Medium | 200 |
| 8 | Script Injection | Web | Hard | 300 |
| 9 | Object Reference | Web | Hard | 300 |

**Total Points**: 1600

## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Detailed setup instructions
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment best practices
- [Challenge Writeups](docs/WRITEUPS.md) - Solutions for all challenges

## Stopping the Platform

```bash
# Use the stop script
./stop.sh

# Or manually
cd ctfd && docker-compose down
cd ../deployment/docker && docker-compose -f docker-compose.challenges.yml down
```

## Project Structure

```
hyve-ctf-2026/
├── README.md                 # This file
├── LICENSE                   # MIT License
├── .gitignore               # Git ignore patterns
├── setup.sh                 # Automated setup script
├── start.sh                 # Start all services
├── stop.sh                  # Stop all services
├── ctfd/                    # CTFd platform configuration
│   ├── docker-compose.yml
│   └── import/
│       └── challenges/
│           └── challenges.yml
├── challenges/              # Challenge files
│   ├── osint/
│   ├── web/
│   ├── crypto/
│   ├── stego/
│   └── network/
├── deployment/              # Deployment configurations
│   └── docker/
│       └── docker-compose.challenges.yml
└── docs/                    # Documentation
    ├── INSTALLATION.md
    ├── DEPLOYMENT.md
    └── WRITEUPS.md
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Credits

Created for Hivye CTF 2026 competition.

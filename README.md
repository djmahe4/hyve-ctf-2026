# Hyve CTF 2026

A 3-hour Capture The Flag (CTF) competition featuring 19 challenges across multiple security domains.

## Description

Hyve CTF 2026 is a beginner to intermediate level CTF competition designed to test skills in OSINT, steganography, cryptography, web exploitation, and network analysis. The competition runs for 3 hours and includes 19 challenges with a total of 1950+ points available.

## Challenge Categories

- **OSINT** (3 challenges) - Open Source Intelligence gathering
- **Steganography** (1 challenge) - Hidden message discovery
- **Cryptography** (3 challenges) - Classical and modern encryption
- **Web** (8 challenges) - Web application vulnerabilities
- **Network** (1 challenge) - Packet analysis and forensics
- **Misc** (3 challenges) - Scripting, basic reversing, and miscellaneous puzzles

## Quick Start

1. **Deploy Services**:
   ```bash
   cd ctfd && docker-compose up -d && cd ..
   cd deployment/docker && docker-compose -f docker-compose.challenges.yml up -d && cd ../..
   ```

2. **Automated Setup**:
   To deploy the complete set of 19 challenges locally:
   ```bash
   python setup_ctf.py --skip-users
   ```

   *(Note: Alternatively, you can use the CTFd UI to import the backup zip via Config -> Backup -> Import).*

## Documentation

- **[Installation & Deployment](docs/DEPLOYMENT.md)** - Complete setup guide from installation to production.
- **[System Logic & Integrations](docs/LOGIC.md)** - API flows, dynamic flags, and architecture details.
- **[Challenge Writeups](docs/WRITEUPS.md)** - Solutions for all 19 challenges.

## Project Structure

```
hyve-ctf-2026/
├── setup_ctf.py        # Main setup automation
├── stop.sh             # Shutdown script
├── ctfd/               # CTFd platform
├── challenges/         # Web apps & challenge source
│   └── teams/          # [Generated] Team-specific assets
├── deployment/         # Docker orchestration
├── utils/              # Internal logic & helpers
└── docs/               # Solutions
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Credits

Created for Hyve CTF 2026 competition.

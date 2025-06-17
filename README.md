# CredSentinel 🔐

CredSentinel is a CLI-based password strength and breach analyzer that combines modern techniques like blacklist checking, zxcvbn scoring, and HIBP API validation to ensure password security.

## Features
- 🔍 Checks password against top common passwords
- 📊 Visual strength meter based on zxcvbn scoring
- 🚨 HIBP API integration to detect breached passwords
- 🎨 Color-coded CLI feedback for better UX
- 💡 Randomized password hygiene tips (based on OWASP & NIST guidelines)

## How It Works
1. User inputs a password
2. Program evaluates score (0–4) using zxcvbn
3. Blacklist check using common_passwords.txt
4. Checks HIBP API for breach count
5. Displays results with color-coded feedback

## Note:
This tool uses a local file common_passwords.txt for blacklist checking. Please download or place it in the root folder manually.

## Installation

```bash
git clone https://github.com/0xCyberSleuth/CredSentinel.git
cd CredSentinel
pip install -r requirements.txt
python cli.py
```

## Requirements
- Python 3.8+
- `colorama`
- `requests`
- `zxcvbn`
- `pyfiglet`

## License
MIT License © 2025 0xCyberSleuth
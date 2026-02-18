#!/bin/bash

# Raw GitHubusercontent URL
#URL="https://raw.githubusercontent.com/djmahe4/gemini-settings/main/popup.html"

# Save in current working directory
LOCALFILE="popup.html"

# Download the file
curl -s "$URL" -o "$LOCALFILE"

# Detect OS and open in default browser
case "$(uname)" in
  Darwin)
    # macOS
    open "$LOCALFILE"
    ;;
  Linux)
    # Linux
    if ! command -v xdg-open >/dev/null; then
      echo "xdg-open not found. Attempting to install xdg-utils..."
      if command -v apt-get >/dev/null; then
        sudo apt-get update && sudo apt-get install -y xdg-utils
      elif command -v yum >/dev/null; then
        sudo yum install -y xdg-utils
      elif command -v dnf >/dev/null; then
        sudo dnf install -y xdg-utils
      elif command -v pacman >/dev/null; then
        sudo pacman -Sy xdg-utils
      fi
    fi

    if command -v xdg-open >/dev/null; then
      xdg-open "$LOCALFILE"
    else
      echo "Could not install xdg-utils. Please open $LOCALFILE manually."
    fi
    ;;
  CYGWIN*|MINGW*|MSYS*)
    # Windows (Git Bash / MSYS)
    start "$LOCALFILE"
    ;;
  *)
    echo "Unsupported OS. Please open $LOCALFILE manually."
    ;;
esac

echo "HYVE_CTF{install_gta6_success}"

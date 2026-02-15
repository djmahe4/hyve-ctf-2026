#!/bin/bash

# Raw GitHubusercontent URL
URL="https://raw.githubusercontent.com/djmahe4/gemini-settings/main/popup.html"

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
    if command -v xdg-open >/dev/null; then
      xdg-open "$LOCALFILE"
    else
      echo "xdg-open not found. Please open $LOCALFILE manually."
    fi
    ;;
  *)
    echo "Unsupported OS. Please open $LOCALFILE manually."
    ;;
esac

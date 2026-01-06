#!/bin/bash
# File watcher: Monitors directory for changes and prompts for Bender changelog
# Usage: ./watch-scripts.sh /path/to/scripts
# Requires: inotifywait (sudo apt install inotify-tools)

WATCH_DIR="${1:-/data/newimage/custodire_pipeline_v1.6/scripts}"

if ! command -v inotifywait &> /dev/null; then
    echo "Install inotify-tools: sudo apt install inotify-tools"
    exit 1
fi

echo "Bender watching: $WATCH_DIR"
echo "Press Ctrl+C to stop"
echo ""

inotifywait -m -r -e modify,create --format '%w%f' "$WATCH_DIR" | while read FILE; do
    # Only trigger on Python/Shell files
    if [[ "$FILE" =~ \.(py|sh)$ ]]; then
        FILENAME=$(basename "$FILE")

        echo ""
        echo "=========================================="
        echo "  BENDER: File modified!"
        echo "  $FILENAME"
        echo "=========================================="
        echo ""

        read -p "Log this change? (y/n): " ANSWER

        if [ "$ANSWER" = "y" ] || [ "$ANSWER" = "Y" ]; then
            read -p "What changed and why? " REASON

            if [ -n "$REASON" ]; then
                bender log "$FILENAME: $REASON"
                echo "Logged!"
            fi
        fi
    fi
done

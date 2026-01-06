#!/bin/bash
# Uninstall Bender

echo "Removing Bender..."

# Remove CLI symlink
sudo rm -f /usr/local/bin/bender 2>/dev/null

# Ask about data
read -p "Delete memory database too? (y/n): " ANSWER
if [ "$ANSWER" = "y" ]; then
    rm -rf ~/agent/memories
    echo "Memory deleted."
fi

echo "Bender uninstalled."
echo "To fully remove: rm -rf ~/agent"
